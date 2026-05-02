# Demo 控制台交接手册

这份文档用于交接当前 Extension C Demo 控制台，重点说明：

- 前后端怎么启动
- 页面按钮按什么顺序点击
- 哪些情况下必须重启服务
- 常见报错怎么判断

## 一、页面用途

当前 Demo 控制台负责这几件事：

1. 对 ADKG / MDKG 的 dev 数据做采样
2. 探测当前配置的 LLM API 是否可用
3. 运行 one-shot / workflow 两种实验
4. 生成摘要表、图表产物、错误分析文档
5. 预览输出文件

## 二、启动顺序

### 1. 进入项目根目录

```bash
cd /Users/Zhuanz1/Desktop/graph
```

### 2. 如果前端代码有改动，先重新打包

```bash
cd web
npm run build
cd ..
```

### 3. 启动后端服务

```bash
PYTHONPATH=src python -m uvicorn bios740_topic2.demo_api:app --host 127.0.0.1 --port 8010
```

### 4. 浏览器打开页面

```text
http://127.0.0.1:8010
```

## 三、什么情况下必须重启服务

如果修改了下面任意内容，必须重启 `uvicorn`：

- `src/bios740_topic2/demo_api.py`
- `scripts/` 下面任何 Python 脚本
- `web/src/` 下面任何前端代码

原因：

- Python 后端进程可能还在引用旧脚本路径
- 前端页面可能还在加载旧的 `web/dist`

典型现象：

```json
{
  "detail": "python: can't open file '/Users/.../scripts/sample_adkg_dev_for_llm.py'"
}
```

这通常不是现在代码有问题，而是**旧后端进程还没重启**。

正确处理方法：

1. 停掉旧的 `uvicorn`
2. 如果前端有修改，重新执行 `npm run build`
3. 重新启动 `uvicorn`

## 四、Run Control 按钮点击流程

页面里的 `Run Control` 区，建议严格按下面顺序点击：

### 第一步：选择数据集模板

先在配置区选择：

- `ADKG`
- `MDKG`
- `Custom`

模板会自动联动这些字段：

- `Raw Input`
- `Sample File`
- `Run Directory`
- `Gold Path`

当前默认：

- `ADKG`：100 条
- `MDKG`：30 条

## 五、标准点击顺序

### 1. `Probe Provider`

用途：

- 检查 API key、base URL、协议配置是否正确

为什么先点它：

- 可以在真正跑实验之前先发现接口不通、鉴权失败、配置错等问题

### 2. `Sample Data`

用途：

- 根据当前 `Raw Input`、`Sample Size`、`Seed` 生成采样文件

当前使用脚本：

```text
scripts/sample_dev_for_llm.py
```

注意：

- 这个脚本现在已经是通用的，不是只支持 ADKG
- 只要输入 JSON 有 `train/dev/test` 结构，就可以用于 MDKG

### 3. `Run Experiment`

用途：

- 启动 LLM 标注实验

建议：

- 一般保持 `Mode = both`
- 除非只想单独调试 `one_shot` 或 `workflow`

### 4. 等待实验完成

看 `Live Status` 区里的两个面板：

- `One-shot`
- `Workflow`

完成判断标准：

1. `processed = total`
2. 运行目录下已经生成 `metrics.json`

在实验没跑完之前，不要急着点后面的摘要/图表/错误分析按钮。

### 5. `Generate Summary`

用途：

- 根据 `metrics.json` 生成摘要表 `summary.md`

### 6. `Generate Artifacts`

用途：

- 生成图表文件，例如：
  - 质量对比图
  - 延迟图
  - 稳定性图

### 7. `Analyze Errors`

用途：

- 生成错误分析文档

这里一定要注意：

- `Gold Path` 必须和当前数据集一致

例如跑 MDKG 时，不能还指向 ADKG 的 sample 文件。

## 六、推荐顺序一句话版

页面正确使用顺序：

```text
Probe Provider -> Sample Data -> Run Experiment -> Generate Summary -> Generate Artifacts -> Analyze Errors
```

对应中文含义：

- `Probe Provider`：先检查当前模型接口是否可用
- `Sample Data`：按当前数据集和采样条数生成实验样本
- `Run Experiment`：启动 one-shot / workflow 实验
- `Generate Summary`：根据 `metrics.json` 生成摘要表
- `Generate Artifacts`：生成图表等可视化产物
- `Analyze Errors`：生成错误分析文档

## 七、MDKG 推荐运行策略

不要一开始就跑 100 条。

推荐：

1. 冒烟检查：`10`
2. 快速比较：`20` 或 `30`
3. 需要更稳一点再跑：`50`

原因：

- ADKG 100 条已经大约跑了 90 分钟
- MDKG baseline 更强，小样本也足够先看趋势

## 八、重要输出文件位置

例如某次运行目录是：

```text
outputs/llm_runs/adkg_dev100_deepseek/
```

关键产物包括：

- `metrics.json`
- `summary.md`
- `one_shot_predictions.json`
- `workflow_predictions.json`
- `one_shot_progress.json`
- `workflow_progress.json`
- `one_shot_progress.jsonl`
- `workflow_progress.jsonl`
- `one_shot_error_summary.md`
- `workflow_error_summary.md`
- `artifacts/artifact_index.md`

## 九、常见报错与处理

### 1. 旧脚本路径报错

报错示例：

```json
{
  "detail": "python: can't open file '/Users/.../scripts/sample_adkg_dev_for_llm.py'"
}
```

原因：

- 后端还在跑旧代码

处理：

- 重启 `uvicorn`

### 2. 页面看起来还是旧版本

原因：

- `web/dist` 没重新打包

处理：

```bash
cd web
npm run build
cd ..
PYTHONPATH=src python -m uvicorn bios740_topic2.demo_api:app --host 127.0.0.1 --port 8010
```

### 3. 点击 `Generate Summary` / `Generate Artifacts` 失败

先检查：

1. 实验是否真的完成
2. `metrics.json` 是否存在
3. 当前 `Run Directory` 是否选对

### 4. 错误分析结果不对

优先检查：

- `Gold Path` 是否还是上一个数据集的路径

## 十、交接时最少确认哪些内容

把项目交给下一个人前，至少确认：

1. 当前使用的是哪个数据集
2. 当前运行目录是什么
3. 前端是否已经重新 build
4. 后端是否已经重启
5. `metrics.json`、`summary.md`、`artifacts/artifact_index.md` 是否已经生成

## 十一、最简操作准则

只要改过前端或脚本，就执行：

1. `npm run build`
2. 重启 `uvicorn`
3. 按下面顺序使用页面：

```text
Probe -> Sample -> Run -> Summary -> Artifacts -> Errors
```
