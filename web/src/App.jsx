import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'
import { detectInitialLocale, messages } from './i18n'

const seriesColors = {
  one_shot: '#71d7ab',
  workflow: '#6fa8ff',
  avg: '#6fa8ff',
  p90: '#ff8f7b',
  parse: '#71d7ab',
}

const datasetTemplates = {
  ADKG: {
    sampleCount: 100,
    rawInput: 'data/raw/ADKG.json',
    samplePath: 'outputs/llm_runs/adkg_dev100_sample.json',
    runDir: 'adkg_dev100_deepseek',
    goldPath: 'outputs/llm_runs/adkg_dev100_sample.json',
  },
  MDKG: {
    sampleCount: 30,
    rawInput: 'data/raw/MDKG.json',
    samplePath: 'outputs/llm_runs/mdkg_dev30_sample.json',
    runDir: 'mdkg_dev30_deepseek',
    goldPath: 'outputs/llm_runs/mdkg_dev30_sample.json',
  },
}

const trainingTemplates = {
  ADKG: {
    smoke: { epochs: 1, batchSize: 1, label: 'smoke_adkg' },
    full: { epochs: 20, batchSize: 2, label: 'adkg_pubmedbert_e20_bs2' },
  },
  MDKG: {
    smoke: { epochs: 1, batchSize: 1, label: 'smoke_mdkg' },
    full: { epochs: 20, batchSize: 2, label: 'mdkg_pubmedbert_e20_bs2' },
  },
}

const api = async (path, options = {}) => {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text()
  if (!response.ok) {
    throw new Error(typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2))
  }
  return payload
}

const prettyPath = (path, runDir = '') => {
  const runPrefix = runDir ? `outputs/llm_runs/${runDir}/` : ''
  if (runPrefix && path.startsWith(runPrefix)) return path.slice(runPrefix.length)
  return path.replace(/^outputs\/llm_runs\//, '')
}

function estimateEta(progress, rows, windowSize = 10) {
  if (!progress) {
    return { remaining: 0, etaSeconds: 0, recentAvg: 0, source: 'pending' }
  }
  const processed = Number(progress.processed || 0)
  const total = Number(progress.total || 0)
  const remaining = Math.max(total - processed, 0)
  const validRows = rows.map((row) => Number(row.latency || 0)).filter((value) => value > 0)
  const recentRows = validRows.slice(-windowSize)

  let recentAvg = 0
  let source = 'pending'
  if (recentRows.length >= 3) {
    recentAvg = recentRows.reduce((sum, value) => sum + value, 0) / recentRows.length
    source = 'recent_window'
  } else if (Number(progress.avg_latency_seconds || 0) > 0) {
    recentAvg = Number(progress.avg_latency_seconds)
    source = 'overall_average'
  }

  return {
    remaining,
    etaSeconds: remaining * recentAvg,
    recentAvg,
    source,
  }
}

function formatDuration(seconds, t) {
  if (!seconds || seconds <= 0) return t.ui.pending
  const rounded = Math.round(seconds)
  const mins = Math.floor(rounded / 60)
  const secs = rounded % 60
  if (mins <= 0) return `${secs}s`
  return `${mins}m ${secs}s`
}

function groupFiles(files) {
  return [
    {
      key: 'summaries',
      title: 'Summaries',
      files: files.filter((file) => /summary\.md$|error_summary\.md$|artifact_index\.md$/.test(file)),
    },
    {
      key: 'charts',
      title: 'Charts',
      files: files.filter((file) => file.includes('/artifacts/') && file.endsWith('.png')),
    },
    {
      key: 'predictions',
      title: 'Predictions',
      files: files.filter((file) => file.endsWith('_predictions.json')),
    },
    {
      key: 'progress',
      title: 'Progress Logs',
      files: files.filter((file) => file.endsWith('_progress.json') || file.endsWith('_progress.jsonl')),
    },
    {
      key: 'other',
      title: 'Other',
      files: files.filter(
        (file) =>
          !/summary\.md$|error_summary\.md$|artifact_index\.md$/.test(file) &&
          !(file.includes('/artifacts/') && file.endsWith('.png')) &&
          !file.endsWith('_predictions.json') &&
          !file.endsWith('_progress.json') &&
          !file.endsWith('_progress.jsonl'),
      ),
    },
  ].filter((group) => group.files.length)
}

function MetricBars({ data, series, t }) {
  if (!data.length) return <div className="empty-state">{t.ui.noMetricsYet}</div>
  return (
    <div className="metric-bars">
      {data.map((row) => (
        <div key={row.metric} className="metric-row">
          <div className="metric-label">{row.metric}</div>
          <div className="metric-series">
            {series.map((key) => {
              const value = Number(row[key] || 0)
              return (
                <div key={key} className="metric-series-row">
                  <span className="metric-series-name">{key}</span>
                  <div className="metric-track">
                    <div
                      className="metric-fill"
                      style={{ width: `${Math.max(0, Math.min(100, value * 100))}%`, background: seriesColors[key] }}
                    />
                  </div>
                  <span className="metric-value">{(value * 100).toFixed(1)}%</span>
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}

function SystemBars({ data, t }) {
  if (!data.length) return <div className="empty-state">{t.ui.noSystemMetricsYet}</div>
  const maxLatency = Math.max(...data.flatMap((row) => [row.avg || 0, row.p90 || 0]), 1)
  return (
    <div className="metric-bars">
      {data.map((row) => (
        <div key={row.method} className="metric-row">
          <div className="metric-label">{row.method}</div>
          <div className="metric-series">
            {[
              ['avg', row.avg, `${row.avg.toFixed(1)}s`],
              ['p90', row.p90, `${row.p90.toFixed(1)}s`],
              ['parse', row.parse, `${row.parse.toFixed(1)}%`],
            ].map(([key, rawValue, display]) => {
              const width = key === 'parse' ? Number(rawValue) : (Number(rawValue) / maxLatency) * 100
              return (
                <div key={key} className="metric-series-row">
                  <span className="metric-series-name">{key}</span>
                  <div className="metric-track">
                    <div
                      className="metric-fill"
                      style={{ width: `${Math.max(0, Math.min(100, width))}%`, background: seriesColors[key] }}
                    />
                  </div>
                  <span className="metric-value">{display}</span>
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}

function LatencyTrace({ data, t }) {
  const [hoveredPoint, setHoveredPoint] = useState(null)
  if (!data.length) return <div className="empty-state">{t.ui.noLatencyTraceYet}</div>
  const width = 760
  const height = 260
  const padding = 24
  const leftPad = 56
  const bottomPad = 34
  const maxIndex = Math.max(...data.map((row) => row.index || 0), 1)
  const maxLatency = Math.max(...data.map((row) => row.latency || 0), 1)
  const yTickValues = [0, 0.25, 0.5, 0.75, 1].map((ratio) => Number((maxLatency * ratio).toFixed(1)))
  const xTickValues = Array.from({ length: 6 }, (_, i) => Math.round((maxIndex * i) / 5))
  const grouped = ['one_shot', 'workflow'].map((mode) => ({
    mode,
    rows: data.filter((row) => row.mode === mode),
  }))
  const getX = (index) => leftPad + ((index || 0) / maxIndex) * (width - leftPad - padding)
  const getY = (latency) =>
    height - bottomPad - ((latency || 0) / maxLatency) * (height - padding - bottomPad)
  const toPath = (rows) =>
    rows
      .map((row, i) => {
        const x = getX(row.index || 0)
        const y = getY(row.latency || 0)
        return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
      })
      .join(' ')
  return (
    <div className="trace-wrap">
      <svg viewBox={`0 0 ${width} ${height}`} className="trace-svg" role="img" aria-label="Latency trace">
        <rect x="0" y="0" width={width} height={height} fill="rgba(255,255,255,0.02)" rx="8" />
        {yTickValues.map((value) => {
          const y = getY(value)
          return (
            <g key={`y-${value}`}>
              <line x1={leftPad} y1={y} x2={width - padding} y2={y} className="trace-grid" />
              <text x={leftPad - 8} y={y + 4} className="trace-axis-label" textAnchor="end">
                {value.toFixed(0)}s
              </text>
            </g>
          )
        })}
        {xTickValues.map((value) => {
          const x = getX(value)
          return (
            <g key={`x-${value}`}>
              <line x1={x} y1={padding} x2={x} y2={height - bottomPad} className="trace-grid trace-grid-vertical" />
              <text x={x} y={height - 10} className="trace-axis-label" textAnchor="middle">
                {value}
              </text>
            </g>
          )
        })}
        <line x1={leftPad} y1={padding} x2={leftPad} y2={height - bottomPad} className="trace-axis-line" />
        <line x1={leftPad} y1={height - bottomPad} x2={width - padding} y2={height - bottomPad} className="trace-axis-line" />
        {grouped.map(({ mode, rows }) =>
          rows.length ? (
            <g key={mode}>
              <path
                d={toPath(rows)}
                fill="none"
                stroke={seriesColors[mode]}
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              {rows.map((row) => {
                const x = getX(row.index || 0)
                const y = getY(row.latency || 0)
                return (
                  <circle
                    key={`${mode}-${row.index}`}
                    cx={x}
                    cy={y}
                    r="5"
                    className="trace-point-hit"
                    onMouseEnter={() => setHoveredPoint({ mode, index: row.index, latency: row.latency, x, y })}
                    onMouseLeave={() => setHoveredPoint(null)}
                  />
                )
              })}
            </g>
          ) : null,
        )}
        {hoveredPoint ? (
          <g className="trace-tooltip">
            <circle cx={hoveredPoint.x} cy={hoveredPoint.y} r="4" fill={seriesColors[hoveredPoint.mode]} />
            <rect
              x={Math.min(hoveredPoint.x + 10, width - 148)}
              y={Math.max(hoveredPoint.y - 48, 8)}
              width="138"
              height="40"
              rx="6"
              className="trace-tooltip-box"
            />
            <text
              x={Math.min(hoveredPoint.x + 18, width - 140)}
              y={Math.max(hoveredPoint.y - 30, 24)}
              className="trace-tooltip-text"
            >
              {hoveredPoint.mode} #{hoveredPoint.index}
            </text>
            <text
              x={Math.min(hoveredPoint.x + 18, width - 140)}
              y={Math.max(hoveredPoint.y - 14, 40)}
              className="trace-tooltip-text"
            >
              {hoveredPoint.latency.toFixed(2)}s
            </text>
          </g>
        ) : null}
      </svg>
      <div className="trace-legend">
        <span><i style={{ background: seriesColors.one_shot }} />{t.labels.oneShot} latency</span>
        <span><i style={{ background: seriesColors.workflow }} />{t.labels.workflow} latency</span>
      </div>
    </div>
  )
}

function ProgressPanel({ title, progress, eta, t }) {
  const pct = progress?.total ? Math.round((progress.processed / progress.total) * 100) : 0
  const completed = progress?.total && progress?.processed >= progress?.total
  const failed = progress?.phase === 'failed'
  return (
    <div className="progress-panel refined">
      <div className="progress-head">
        <span>{title}</span>
        <span className={`status-badge ${failed ? 'failed' : completed ? 'done' : 'running'}`}>
          {failed ? t.labels.failed : completed ? t.ui.completed : progress?.phase || t.ui.running}
        </span>
        <strong>{progress ? `${progress.processed}/${progress.total}` : t.ui.idle}</strong>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="status-metric-grid">
        <div className="status-metric">
          <span>{t.ui.progress}</span>
          <strong>{pct}%</strong>
        </div>
        <div className="status-metric">
          <span>{t.ui.avgLatency}</span>
          <strong>{eta.recentAvg ? `${eta.recentAvg.toFixed(1)}s` : t.ui.pending}</strong>
        </div>
        <div className="status-metric">
          <span>{t.ui.recentEta}</span>
          <strong>{formatDuration(eta.etaSeconds, t)}</strong>
        </div>
      </div>
      <div className="progress-meta compact">
        <span>{t.labels.etaSource}</span>
        <strong>{eta.source === 'recent_window' ? t.ui.recentWindow : eta.source === 'overall_average' ? t.ui.overallAverage : t.ui.pending}</strong>
      </div>
    </div>
  )
}

function ProbeSummary({ probe, t }) {
  if (!probe) return <div className="empty-state">{t.ui.noProbeRunYet}</div>
  const result = Array.isArray(probe.results) ? probe.results[0] : null
  const ok = result?.ok
  return (
    <div className="probe-summary">
      <div className="probe-header">
        <span className={`status-badge ${ok ? 'done' : 'failed'}`}>{ok ? t.labels.success : t.labels.failed}</span>
      </div>
      <div className="probe-summary-title">{t.labels.structuredProbe}</div>
      <div className="status-metric-grid">
        <div className="status-metric">
          <span>{t.labels.baseUrl}</span>
          <strong>{probe.base_url || '-'}</strong>
        </div>
        <div className="status-metric">
          <span>{t.labels.model}</span>
          <strong>{probe.model || '-'}</strong>
        </div>
        <div className="status-metric">
          <span>{t.labels.wireApi}</span>
          <strong>{probe.wire_api || '-'}</strong>
        </div>
        <div className="status-metric">
          <span>{t.labels.endpoint}</span>
          <strong>{result?.url || '-'}</strong>
        </div>
        <div className="status-metric">
          <span>{t.labels.httpStatus}</span>
          <strong>{result?.http_status ?? '-'}</strong>
        </div>
        <div className="status-metric">
          <span>{t.labels.result}</span>
          <strong>{ok ? t.labels.success : t.labels.failed}</strong>
        </div>
      </div>
      <details className="raw-panel">
        <summary>{t.labels.rawProbe}</summary>
        <pre className="log-block compact">{JSON.stringify(probe, null, 2)}</pre>
      </details>
    </div>
  )
}

function KnowledgeGraph({ graph, t }) {
  const [hovered, setHovered] = useState(null)
  if (!graph) return <div className="empty-state">{t.labels.noGraphLoaded}</div>
  if (!graph.nodes.length) return <div className="empty-state">{t.ui.noMetricsYet}</div>

  const width = 900
  const height = 420
  const cx = width / 2
  const cy = height / 2
  const radius = 140
  const typeColors = {
    disease: '#ff8f7b',
    drug: '#71d7ab',
    gene: '#6fa8ff',
    method: '#f4c95d',
    mutation: '#c08cff',
    other: '#94a6bb',
    symptom: '#ffb86b',
    region: '#7ad4ff',
    physiology: '#8dd694',
    signs: '#f28fad',
    Health_factors: '#a8e6cf',
  }

  const nodes = graph.nodes.map((node, index) => {
    const angle = (index / graph.nodes.length) * Math.PI * 2
    return {
      ...node,
      x: cx + Math.cos(angle) * radius,
      y: cy + Math.sin(angle) * radius,
      color: typeColors[node.type] || '#94a6bb',
    }
  })
  const nodeMap = Object.fromEntries(nodes.map((node) => [node.id, node]))

  return (
    <div className="kg-wrap">
      <svg viewBox={`0 0 ${width} ${height}`} className="kg-svg" role="img" aria-label="Knowledge graph">
        <rect x="0" y="0" width={width} height={height} fill="rgba(255,255,255,0.02)" rx="8" />
        {graph.edges.map((edge, index) => {
          const source = nodeMap[edge.source]
          const target = nodeMap[edge.target]
          if (!source || !target) return null
          const midX = (source.x + target.x) / 2
          const midY = (source.y + target.y) / 2
          return (
            <g key={`${edge.source}-${edge.target}-${index}`}>
              <line
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                className="kg-edge"
                strokeWidth={1 + edge.count}
                onMouseEnter={() => setHovered({ kind: 'edge', x: midX, y: midY, edge })}
                onMouseLeave={() => setHovered(null)}
              />
              <text
                x={midX}
                y={midY}
                className="kg-edge-label"
                textAnchor="middle"
              >
                {edge.relation}
              </text>
            </g>
          )
        })}
        {nodes.map((node) => (
          <g key={node.id}>
            <circle
              cx={node.x}
              cy={node.y}
              r={10 + Math.min(node.count * 1.5, 10)}
              fill={node.color}
              className="kg-node"
              onMouseEnter={() => setHovered({ kind: 'node', x: node.x, y: node.y, node })}
              onMouseLeave={() => setHovered(null)}
            />
            <text x={node.x} y={node.y - 16} textAnchor="middle" className="kg-node-label">
              {node.label}
            </text>
          </g>
        ))}
        {hovered ? (
          <g className="kg-tooltip">
            <rect
              x={Math.min(hovered.x + 12, width - 180)}
              y={Math.max(hovered.y - 56, 8)}
              width="170"
              height="48"
              rx="6"
              className="trace-tooltip-box"
            />
            {hovered.kind === 'node' ? (
              <>
                <text x={Math.min(hovered.x + 20, width - 172)} y={Math.max(hovered.y - 38, 24)} className="trace-tooltip-text">
                  {hovered.node.label}
                </text>
                <text x={Math.min(hovered.x + 20, width - 172)} y={Math.max(hovered.y - 22, 40)} className="trace-tooltip-text">
                  {t.labels.nodeType}: {hovered.node.type}
                </text>
                <text x={Math.min(hovered.x + 20, width - 172)} y={Math.max(hovered.y - 6, 56)} className="trace-tooltip-text">
                  {t.labels.occurrences}: {hovered.node.count}
                </text>
              </>
            ) : (
              <>
                <text x={Math.min(hovered.x + 20, width - 172)} y={Math.max(hovered.y - 30, 24)} className="trace-tooltip-text">
                  {hovered.edge.relation}
                </text>
                <text x={Math.min(hovered.x + 20, width - 172)} y={Math.max(hovered.y - 14, 40)} className="trace-tooltip-text">
                  {t.labels.occurrences}: {hovered.edge.count}
                </text>
              </>
            )}
          </g>
        ) : null}
      </svg>
      <div className="trace-legend">
        {[...new Set(nodes.map((node) => node.type))].map((type) => (
          <span key={type}><i style={{ background: typeColors[type] || '#94a6bb' }} />{type}</span>
        ))}
      </div>
    </div>
  )
}

function FileGroups({ groups, handleFilePreview, runDir, t }) {
  return (
    <div className="file-groups">
      {groups.map((group) => (
        <details key={group.key} className="file-group" open={group.key === 'summaries' || group.key === 'charts'}>
          <summary>{group.title} ({group.files.length})</summary>
          <div className="file-list">
            {group.files.map((file) => (
              <button key={file} className="file-item" onClick={() => handleFilePreview(file)}>
                {prettyPath(file, runDir)}
              </button>
            ))}
          </div>
        </details>
      ))}
      {!groups.length && <div className="empty-state small">{t.ui.noFileSelected}</div>}
    </div>
  )
}

function App() {
  const [locale, setLocale] = useState(detectInitialLocale())
  const t = messages[locale]
  const [config, setConfig] = useState({
    dataset: 'ADKG',
    rawInput: datasetTemplates.ADKG.rawInput,
    provider: 'openai_compat',
    mode: 'both',
    sampleCount: datasetTemplates.ADKG.sampleCount,
    seed: 740,
    samplePath: datasetTemplates.ADKG.samplePath,
    runDir: datasetTemplates.ADKG.runDir,
    goldPath: datasetTemplates.ADKG.goldPath,
    envFile: '.env.llm',
  })
  const [health, setHealth] = useState('checking')
  const [jobs, setJobs] = useState([])
  const [probe, setProbe] = useState(null)
  const [files, setFiles] = useState([])
  const [preview, setPreview] = useState({ type: 'text', title: t.ui.noFileSelected, content: '' })
  const [oneShotProgress, setOneShotProgress] = useState(null)
  const [workflowProgress, setWorkflowProgress] = useState(null)
  const [systemChart, setSystemChart] = useState([])
  const [qualityChart, setQualityChart] = useState([])
  const [latencyChart, setLatencyChart] = useState([])
  const [busyAction, setBusyAction] = useState('')
  const [progressRows, setProgressRows] = useState({ one_shot: [], workflow: [] })
  const [trainingConfig, setTrainingConfig] = useState({
    dataset: 'ADKG',
    preset: 'smoke',
    epochs: trainingTemplates.ADKG.smoke.epochs,
    batchSize: trainingTemplates.ADKG.smoke.batchSize,
    label: trainingTemplates.ADKG.smoke.label,
  })
  const [trainingJobId, setTrainingJobId] = useState('')
  const [trainingStatus, setTrainingStatus] = useState(null)
  const [gpuStatus, setGpuStatus] = useState(null)
  const [graphConfig, setGraphConfig] = useState({
    mode: 'one_shot',
    topKEdges: 30,
    relationType: '',
  })
  const [graphData, setGraphData] = useState(null)
  const [graphRelations, setGraphRelations] = useState([])
  const runDirRef = useRef(config.runDir)

  useEffect(() => {
    window.localStorage.setItem('bios740-demo-locale', locale)
  }, [locale])

  useEffect(() => {
    runDirRef.current = config.runDir
  }, [config.runDir])

  useEffect(() => {
    if (!preview.content) {
      setPreview((prev) => ({ ...prev, title: t.ui.noFileSelected }))
    }
  }, [locale])

  useEffect(() => {
    refreshHealth()
    refreshStatus()
    const timer = setInterval(refreshStatus, 5000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    if (!trainingJobId) return
    const timer = setInterval(() => {
      refreshTrainingStatus(trainingJobId)
      refreshGpuStatus()
    }, 5000)
    return () => clearInterval(timer)
  }, [trainingJobId])

  useEffect(() => {
    refreshFiles()
  }, [config.runDir])

  const updateConfig = (key, value) => setConfig((prev) => ({ ...prev, [key]: value }))
  const updateTrainingConfig = (key, value) => setTrainingConfig((prev) => ({ ...prev, [key]: value }))
  const updateGraphConfig = (key, value) => setGraphConfig((prev) => ({ ...prev, [key]: value }))

  const applyTrainingTemplate = (nextDataset, nextPreset) => {
    const template = trainingTemplates[nextDataset]?.[nextPreset]
    if (!template) return
    setTrainingConfig((prev) => ({
      ...prev,
      dataset: nextDataset,
      preset: nextPreset,
      epochs: template.epochs,
      batchSize: template.batchSize,
      label: template.label,
    }))
  }

  const applyDatasetTemplate = (dataset) => {
    if (!datasetTemplates[dataset]) {
      updateConfig('dataset', dataset)
      return
    }
    const template = datasetTemplates[dataset]
    setConfig((prev) => ({
      ...prev,
      dataset,
      rawInput: template.rawInput,
      sampleCount: template.sampleCount,
      samplePath: template.samplePath,
      runDir: template.runDir,
      goldPath: template.goldPath,
    }))
  }

  const refreshHealth = async () => {
    try {
      await api('/api/health')
      setHealth('healthy')
    } catch {
      setHealth('offline')
    }
  }

  const refreshTrainingStatus = async (jobId) => {
    try {
      const payload = await api(`/api/train/status?job_id=${encodeURIComponent(jobId)}`)
      setTrainingStatus(payload)
    } catch {}
  }

  const refreshGpuStatus = async () => {
    try {
      const payload = await api('/api/train/gpu')
      setGpuStatus(payload)
    } catch {}
  }

  const refreshStatus = async () => {
    try {
      const payload = await api('/api/status')
      setJobs(payload.jobs)
    } catch {}
    await refreshFiles(runDirRef.current)
  }

  const refreshFiles = async (runDirName = runDirRef.current) => {
    try {
      const payload = await api(`/api/files?run_dir_name=${encodeURIComponent(runDirName)}`)
      setFiles(payload.files)
      await hydrateDerivedViews(payload.files)
    } catch {
      setFiles([])
      setOneShotProgress(null)
      setWorkflowProgress(null)
      setSystemChart([])
      setQualityChart([])
      setLatencyChart([])
      setProgressRows({ one_shot: [], workflow: [] })
    }
  }

  const fetchTextFile = async (path) => {
    const payload = await api(`/api/file?path=${encodeURIComponent(path)}`)
    return payload.content
  }

  const hydrateDerivedViews = async (nextFiles) => {
    const oneShotFile = nextFiles.find((item) => item.endsWith('one_shot_progress.json'))
    const workflowFile = nextFiles.find((item) => item.endsWith('workflow_progress.json'))
    const metricsFile = nextFiles.find((item) => item.endsWith('metrics.json'))
    const oneShotJsonl = nextFiles.find((item) => item.endsWith('one_shot_progress.jsonl'))
    const workflowJsonl = nextFiles.find((item) => item.endsWith('workflow_progress.jsonl'))

    setOneShotProgress(oneShotFile ? JSON.parse(await fetchTextFile(oneShotFile)) : null)
    setWorkflowProgress(workflowFile ? JSON.parse(await fetchTextFile(workflowFile)) : null)

    if (metricsFile) {
      const metrics = JSON.parse(await fetchTextFile(metricsFile))
      setQualityChart([
        { metric: 'Strict Entity', ...Object.fromEntries(Object.entries(metrics).map(([m, r]) => [m, r.strict.entities.micro.f1])) },
        { metric: 'Strict Relation', ...Object.fromEntries(Object.entries(metrics).map(([m, r]) => [m, r.strict.relations.micro.f1])) },
        { metric: 'Relaxed Entity', ...Object.fromEntries(Object.entries(metrics).map(([m, r]) => [m, r.relaxed.entities.f1])) },
        { metric: 'Relaxed Relation', ...Object.fromEntries(Object.entries(metrics).map(([m, r]) => [m, r.relaxed.relations.f1])) },
      ])
      setSystemChart(
        Object.entries(metrics).map(([method, result]) => ({
          method,
          avg: result.avg_latency_seconds,
          p50: result.p50_latency_seconds,
          p90: result.p90_latency_seconds,
          parse: Number((result.parse_success_rate * 100).toFixed(2)),
        })),
      )
    } else {
      setQualityChart([])
      setSystemChart([])
    }

    const traceRows = []
    const nextProgressRows = { one_shot: [], workflow: [] }
    for (const [label, file] of [['one_shot', oneShotJsonl], ['workflow', workflowJsonl]]) {
      if (!file) continue
      const rows = (await fetchTextFile(file)).split('\n').filter(Boolean).map((line) => JSON.parse(line))
      nextProgressRows[label] = rows.map((row) => ({ ...row, latency: row.latency_seconds }))
      traceRows.push(...rows.map((row) => ({ mode: label, index: row.index, latency: row.latency_seconds })))
    }
    setProgressRows(nextProgressRows)
    setLatencyChart(traceRows)
  }

  const callAction = async (label, path, body) => {
    setBusyAction(label)
    try {
      const payload = await api(path, { method: 'POST', body: JSON.stringify(body) })
      if (path === '/api/probe') setProbe(payload)
      if (payload.output) setPreview({ type: 'text', title: label, content: JSON.stringify(payload, null, 2) })
      if (payload.output?.endsWith('_sample.json')) {
        updateConfig('samplePath', payload.output)
        updateConfig('goldPath', payload.output)
      }
      if (payload.run_dir) {
        const nextRunDir = payload.run_dir.replace(/^outputs\/llm_runs\//, '')
        runDirRef.current = nextRunDir
        updateConfig('runDir', nextRunDir)
      }
      await refreshStatus(runDirRef.current)
    } catch (error) {
      setPreview({ type: 'text', title: `${label} ${t.ui.error}`, content: String(error.message || error) })
    } finally {
      setBusyAction('')
    }
  }

  const handleFilePreview = async (path) => {
    if (path.endsWith('.png')) {
      setPreview({ type: 'image', title: prettyPath(path, config.runDir), content: `/api/file?path=${encodeURIComponent(path)}` })
      return
    }
    const content = await fetchTextFile(path)
    setPreview({ type: 'text', title: prettyPath(path, config.runDir), content })
  }

  const startTraining = async () => {
    setBusyAction(t.actions.startTraining)
    try {
      const payload = await api('/api/train/start', {
        method: 'POST',
        body: JSON.stringify({
          dataset: trainingConfig.dataset,
          preset: trainingConfig.preset,
          epochs: trainingConfig.epochs,
          batch_size: trainingConfig.batchSize,
          label: trainingConfig.label,
        }),
      })
      setTrainingJobId(payload.job_id)
      await refreshTrainingStatus(payload.job_id)
      await refreshGpuStatus()
    } catch (error) {
      setPreview({ type: 'text', title: `${t.actions.startTraining} ${t.ui.error}`, content: String(error.message || error) })
    } finally {
      setBusyAction('')
    }
  }

  const stopTraining = async () => {
    if (!trainingJobId) return
    setBusyAction(t.actions.stopTraining)
    try {
      await api('/api/train/stop', {
        method: 'POST',
        body: JSON.stringify({ job_id: trainingJobId }),
      })
      await refreshTrainingStatus(trainingJobId)
    } catch (error) {
      setPreview({ type: 'text', title: `${t.actions.stopTraining} ${t.ui.error}`, content: String(error.message || error) })
    } finally {
      setBusyAction('')
    }
  }

  const loadGraph = async () => {
    setBusyAction(t.labels.knowledgeGraph)
    try {
      const query = new URLSearchParams({
        run_dir_name: config.runDir,
        mode: graphConfig.mode,
        top_k_edges: String(graphConfig.topKEdges),
      })
      if (graphConfig.relationType) query.set('relation_type', graphConfig.relationType)
      const payload = await api(`/api/kg/graph?${query.toString()}`)
      setGraphData(payload)
    } catch (error) {
      setPreview({ type: 'text', title: `${t.labels.knowledgeGraph} ${t.ui.error}`, content: String(error.message || error) })
    } finally {
      setBusyAction('')
    }
  }

  const loadGraphRelations = async () => {
    try {
      const payload = await api(
        `/api/kg/relations?run_dir_name=${encodeURIComponent(config.runDir)}&mode=${encodeURIComponent(graphConfig.mode)}`,
      )
      setGraphRelations(payload.relation_types || [])
    } catch {
      setGraphRelations([])
    }
  }

  useEffect(() => {
    loadGraphRelations()
  }, [config.runDir, graphConfig.mode])

  const latestJob = jobs[jobs.length - 1]
  const oneShotEta = estimateEta(oneShotProgress, progressRows.one_shot)
  const workflowEta = estimateEta(workflowProgress, progressRows.workflow)
  const fileGroups = useMemo(() => groupFiles(files), [files])

  return (
    <div className="console-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">KG</div>
          <div>
            <div className="eyebrow">{t.labels.biomedicalKg}</div>
            <h1>{t.labels.extensionConsole}</h1>
          </div>
          <div className="locale-switch">
            <button className={locale === 'zh' ? 'active' : ''} onClick={() => setLocale('zh')}>{t.ui.zh}</button>
            <button className={locale === 'en' ? 'active' : ''} onClick={() => setLocale('en')}>{t.ui.en}</button>
          </div>
        </div>

        <section className="card">
          <div className="section-title">{t.labels.experimentConfig}</div>
          <div className="field-grid">
            <label>
              <span>{t.labels.dataset}</span>
              <select value={config.dataset} onChange={(e) => applyDatasetTemplate(e.target.value)}>
                <option value="ADKG">{t.dataset.adkg}</option>
                <option value="MDKG">{t.dataset.mdkg}</option>
                <option value="Custom">{t.dataset.custom}</option>
              </select>
            </label>
            <label className="wide">
              <span>{t.labels.rawInput}</span>
              <input value={config.rawInput} onChange={(e) => updateConfig('rawInput', e.target.value)} />
            </label>
            <label>
              <span>{t.labels.provider}</span>
              <select value={config.provider} onChange={(e) => updateConfig('provider', e.target.value)}>
                <option value="openai_compat">{t.providerOptions.openaiCompat}</option>
                <option value="mock">{t.providerOptions.mock}</option>
              </select>
            </label>
            <label>
              <span>{t.labels.mode}</span>
              <select value={config.mode} onChange={(e) => updateConfig('mode', e.target.value)}>
                <option value="both">both</option>
                <option value="one_shot">one_shot</option>
                <option value="workflow">workflow</option>
              </select>
            </label>
            <label>
              <span>{t.labels.sampleSize}</span>
              <input type="number" value={config.sampleCount} onChange={(e) => updateConfig('sampleCount', Number(e.target.value))} />
            </label>
            <label>
              <span>{t.labels.seed}</span>
              <input type="number" value={config.seed} onChange={(e) => updateConfig('seed', Number(e.target.value))} />
            </label>
            <label className="wide">
              <span>{t.labels.sampleFile}</span>
              <input value={config.samplePath} onChange={(e) => updateConfig('samplePath', e.target.value)} />
            </label>
            <label className="wide">
              <span>{t.labels.runDirectory}</span>
              <input value={config.runDir} onChange={(e) => updateConfig('runDir', e.target.value)} />
            </label>
            <label className="wide">
              <span>{t.labels.goldPath}</span>
              <input value={config.goldPath} onChange={(e) => updateConfig('goldPath', e.target.value)} />
            </label>
            <label className="wide">
              <span>{t.labels.envFile}</span>
              <input value={config.envFile} onChange={(e) => updateConfig('envFile', e.target.value)} />
            </label>
          </div>
          <div className="busy-row">{t.labels.autoTemplateHint}</div>
        </section>

        <section className="card">
          <div className="section-title">{t.labels.runControl}</div>
          <div className="button-grid">
            <button onClick={() => callAction(t.actions.sampleData, '/api/sample', {
              input_path: config.rawInput,
              count: config.sampleCount,
              seed: config.seed,
              output_name: `${config.runDir}_sample.json`,
            })}>{t.actions.sampleData}</button>
            <button onClick={() => callAction(t.actions.probeProvider, '/api/probe', { env_file: config.envFile })}>{t.actions.probeProvider}</button>
            <button className="accent" onClick={() => callAction(t.actions.runExperiment, '/api/run', {
              sample_path: config.samplePath,
              output_dir_name: config.runDir,
              mode: config.mode,
              provider: config.provider,
              env_file: config.envFile,
            })}>{t.actions.runExperiment}</button>
            <button onClick={() => callAction(t.actions.generateSummary, '/api/summarize', { run_dir_name: config.runDir })}>{t.actions.generateSummary}</button>
            <button onClick={() => callAction(t.actions.generateArtifacts, '/api/artifacts', { run_dir_name: config.runDir })}>{t.actions.generateArtifacts}</button>
            <button onClick={() => callAction(t.actions.analyzeErrors, '/api/errors', { run_dir_name: config.runDir, gold_path: config.goldPath })}>{t.actions.analyzeErrors}</button>
          </div>
          <div className="busy-row">{busyAction ? `${t.ui.running}: ${busyAction}` : t.ui.idle}</div>
          <div className="run-guide">
            <div className="run-guide-title">{t.labels.runGuideTitle}</div>
            <ol className="run-guide-list">
              <li><strong>{t.actions.probeProvider}</strong><span>{t.guide.probeProvider}</span></li>
              <li><strong>{t.actions.sampleData}</strong><span>{t.guide.sampleData}</span></li>
              <li><strong>{t.actions.runExperiment}</strong><span>{t.guide.runExperiment}</span></li>
              <li><strong>{t.actions.generateSummary}</strong><span>{t.guide.generateSummary}</span></li>
              <li><strong>{t.actions.generateArtifacts}</strong><span>{t.guide.generateArtifacts}</span></li>
              <li><strong>{t.actions.analyzeErrors}</strong><span>{t.guide.analyzeErrors}</span></li>
            </ol>
          </div>
        </section>
      </aside>

      <main className="main">
        <section className="hero card">
          <div>
            <div className="eyebrow">{t.hero.eyebrow}</div>
            <h2>{t.hero.title}</h2>
            <p>{t.hero.desc}</p>
          </div>
          <div className={`health-pill ${health}`}>{t.ui.backend}: {t.ui[health] || health}</div>
        </section>

        <section className="grid two">
          <div className="card">
            <div className="section-title">{t.labels.liveStatus}</div>
            <div className="stat-grid">
              <div className="stat-tile"><span>{t.labels.lastJob}</span><strong>{latestJob?.status || t.ui.none}</strong></div>
              <div className="stat-tile"><span>{t.labels.runDir}</span><strong>{config.runDir}</strong></div>
              <div className="stat-tile"><span>{t.labels.dataset}</span><strong>{config.dataset}</strong></div>
              <div className="stat-tile"><span>{t.labels.sampleSize}</span><strong>{config.sampleCount}</strong></div>
            </div>
            <div className="progress-stack">
              <ProgressPanel title={t.labels.oneShot} progress={oneShotProgress} eta={oneShotEta} t={t} />
              <ProgressPanel title={t.labels.workflow} progress={workflowProgress} eta={workflowEta} t={t} />
            </div>
            <details className="raw-panel">
              <summary>{t.labels.rawJobs}</summary>
              <pre className="log-block compact">{JSON.stringify(jobs, null, 2)}</pre>
            </details>
          </div>

          <div className="card">
            <div className="section-title">{t.labels.probeOutput}</div>
            <ProbeSummary probe={probe} t={t} />
          </div>
        </section>

        <section className="grid two">
          <div className="card">
            <div className="section-title">{t.labels.producedFiles}</div>
            <FileGroups groups={fileGroups} handleFilePreview={handleFilePreview} runDir={config.runDir} t={t} />
          </div>

          <div className="card">
            <div className="section-title">{t.labels.preview}</div>
            <div className="preview-box">
              <div className="preview-title">{preview.title}</div>
              {preview.type === 'image'
                ? <img src={preview.content} alt={preview.title} className="preview-image" />
                : <pre className="preview-text">{preview.content}</pre>}
            </div>
          </div>
        </section>

        <section className="grid two">
          <div className="card">
            <div className="section-title">{t.labels.qualityComparison}</div>
            <div className="chart-box">
              <MetricBars data={qualityChart} series={['one_shot', 'workflow']} t={t} />
            </div>
          </div>

          <div className="card">
            <div className="section-title">{t.labels.systemComparison}</div>
            <div className="chart-box">
              <SystemBars data={systemChart} t={t} />
            </div>
          </div>
        </section>

        <section className="card">
          <div className="section-title">{t.labels.latencyTrace}</div>
          <div className="chart-box">
            <LatencyTrace data={latencyChart} t={t} />
          </div>
        </section>

        <section className="grid two">
          <div className="card">
            <div className="section-title">{t.labels.baselineTraining}</div>
            <div className="field-grid">
              <label>
                <span>{t.labels.dataset}</span>
                <select value={trainingConfig.dataset} onChange={(e) => applyTrainingTemplate(e.target.value, trainingConfig.preset)}>
                  <option value="ADKG">{t.dataset.adkg}</option>
                  <option value="MDKG">{t.dataset.mdkg}</option>
                </select>
              </label>
              <label>
                <span>{t.labels.preset}</span>
                <select value={trainingConfig.preset} onChange={(e) => applyTrainingTemplate(trainingConfig.dataset, e.target.value)}>
                  <option value="smoke">{t.training.smoke}</option>
                  <option value="full">{t.training.full}</option>
                </select>
              </label>
              <label>
                <span>{t.labels.epochs}</span>
                <input type="number" value={trainingConfig.epochs} onChange={(e) => updateTrainingConfig('epochs', Number(e.target.value))} />
              </label>
              <label>
                <span>{t.labels.batchSize}</span>
                <input type="number" value={trainingConfig.batchSize} onChange={(e) => updateTrainingConfig('batchSize', Number(e.target.value))} />
              </label>
              <label className="wide">
                <span>{t.labels.runLabel}</span>
                <input value={trainingConfig.label} onChange={(e) => updateTrainingConfig('label', e.target.value)} />
              </label>
            </div>
            <div className="busy-row">{t.labels.trainDatasetHint}</div>
            <div className="button-grid training-actions">
              <button className="accent" onClick={startTraining}>{t.actions.startTraining}</button>
              <button onClick={stopTraining} disabled={!trainingJobId || trainingStatus?.job?.status !== 'running'}>
                {t.actions.stopTraining}
              </button>
            </div>
          </div>

          <div className="card">
            <div className="section-title">{t.labels.trainingStatus}</div>
            {trainingStatus ? (
              <>
                <div className="status-metric-grid">
                  <div className="status-metric">
                    <span>{t.labels.dataset}</span>
                    <strong>{trainingStatus.job.metadata.dataset}</strong>
                  </div>
                  <div className="status-metric">
                    <span>{t.labels.preset}</span>
                    <strong>{trainingStatus.job.metadata.preset}</strong>
                  </div>
                  <div className="status-metric">
                    <span>{t.labels.phase}</span>
                    <strong>{trainingStatus.progress.phase}</strong>
                  </div>
                  <div className="status-metric">
                    <span>{t.labels.currentEpoch}</span>
                    <strong>{trainingStatus.progress.current_epoch}/{trainingStatus.progress.total_epochs}</strong>
                  </div>
                </div>
                <div className="progress-panel refined training-panel">
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${trainingStatus.progress.progress_percent}%` }} />
                  </div>
                  <div className="progress-meta">
                    <span>{t.ui.progress}: {trainingStatus.progress.progress_percent}%</span>
                    <span>{trainingStatus.job.status}</span>
                  </div>
                </div>
                <div className="section-title training-subtitle">{t.labels.logTail}</div>
                <pre className="log-block compact training-log">{trainingStatus.log_tail || t.ui.pending}</pre>
              </>
            ) : (
              <div className="empty-state">{t.ui.pending}</div>
            )}
          </div>
        </section>

        <section className="card">
          <div className="section-title">{t.labels.gpuSummary}</div>
          {gpuStatus ? (
            <div className="status-metric-grid">
              <div className="status-metric">
                <span>{t.labels.gpuName}</span>
                <strong>{gpuStatus.gpu_name || '-'}</strong>
              </div>
              <div className="status-metric">
                <span>{t.labels.gpuMemory}</span>
                <strong>{gpuStatus.memory_used_mib}/{gpuStatus.memory_total_mib} MiB</strong>
              </div>
              <div className="status-metric">
                <span>{t.labels.gpuUtil}</span>
                <strong>{gpuStatus.gpu_util_percent}%</strong>
              </div>
            </div>
          ) : (
            <div className="empty-state">{t.ui.pending}</div>
          )}
        </section>

        <section className="grid two">
          <div className="card">
            <div className="section-title">{t.labels.knowledgeGraph}</div>
            <div className="field-grid">
              <label>
                <span>{t.labels.graphMode}</span>
                <select value={graphConfig.mode} onChange={(e) => updateGraphConfig('mode', e.target.value)}>
                  <option value="one_shot">{t.labels.oneShot}</option>
                  <option value="workflow">{t.labels.workflow}</option>
                </select>
              </label>
              <label>
                <span>{t.labels.topKEdges}</span>
                <input type="number" value={graphConfig.topKEdges} onChange={(e) => updateGraphConfig('topKEdges', Number(e.target.value))} />
              </label>
              <label className="wide">
                <span>{t.labels.relationFilter}</span>
                <select value={graphConfig.relationType} onChange={(e) => updateGraphConfig('relationType', e.target.value)}>
                  <option value="">{t.ui.all}</option>
                  {!graphRelations.length ? <option value="" disabled>{t.ui.noOptions}</option> : null}
                  {graphRelations.map((relation) => (
                    <option key={relation} value={relation}>{relation}</option>
                  ))}
                </select>
              </label>
            </div>
            <div className="button-grid single-action">
              <button className="accent" onClick={loadGraph}>{t.labels.loadGraph}</button>
            </div>
            {graphData ? (
              <div className="status-metric-grid">
                <div className="status-metric">
                  <span>{t.labels.nodeCount}</span>
                  <strong>{graphData.summary.node_count}</strong>
                </div>
                <div className="status-metric">
                  <span>{t.labels.edgeCount}</span>
                  <strong>{graphData.summary.edge_count}</strong>
                </div>
                <div className="status-metric">
                  <span>{t.labels.topRelation}</span>
                  <strong>{graphData.summary.top_relation || '-'}</strong>
                </div>
              </div>
            ) : null}
          </div>

          <div className="card">
            <div className="section-title">{t.labels.graphSummary}</div>
            <KnowledgeGraph graph={graphData} t={t} />
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
