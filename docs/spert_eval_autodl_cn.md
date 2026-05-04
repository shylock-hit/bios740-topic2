# SpERT 评测执行说明（AutoDL）

这份说明只解决一件事：把已经训练好的 ADKG / MDKG SpERT + PubMedBERT checkpoint，在 AutoDL 上补出本地缺失的：

- `test` 指标
- 固定采样 `dev100` 指标

## 1. 前置依赖

运行前必须满足下面几个条件：

### 1.1 项目代码完整

项目目录下需要有：

- `external/spert/`
- `outputs/spert/adkg/`
- `outputs/spert/mdkg/`
- `scripts/eval_spert_test_autodl.sh`
- `scripts/eval_spert_dev100_autodl.sh`

如果 `external/spert/` 不在项目里，先执行：

```bash
cd /root/autodl-tmp/graph
git clone https://github.com/lavis-nlp/spert.git external/spert
```

### 1.2 训练好的 checkpoint 已经存在

需要至少有这两个根目录之一：

```text
outputs/checkpoints/adkg/adkg_pubmedbert_e20_bs2/
outputs/checkpoints/mdkg/mdkg_pubmedbert_e20_bs2/
```

脚本会自动选择每个目录下最新时间戳的 checkpoint。

### 1.3 Python 环境可用

需要环境中能导入这些包：

- `torch`
- `transformers`
- `safetensors`

### 1.4 数据文件已在项目目录中

至少需要这些文件：

```text
outputs/spert/adkg/dev.json
outputs/spert/adkg/test.json
outputs/spert/adkg/types.json
outputs/spert/mdkg/dev.json
outputs/spert/mdkg/test.json
outputs/spert/mdkg/types.json
data/raw/ADKG.json
data/raw/MDKG.json
```

## 2. 跑 test 评测

在 AutoDL 项目根目录执行：

```bash
cd /root/autodl-tmp/graph
bash scripts/eval_spert_test_autodl.sh
```

这个脚本会自动完成：

1. 找到 ADKG 最新 checkpoint
2. 找到 MDKG 最新 checkpoint
3. 必要时把 `model.safetensors` 转成 `pytorch_model.bin`
4. 分别对 `outputs/spert/adkg/test.json` 和 `outputs/spert/mdkg/test.json` 做评测

输出位置：

```text
outputs/logs/adkg_test_eval.log
outputs/logs/mdkg_test_eval.log
outputs/test_eval/adkg/
outputs/test_eval/mdkg/
```

## 3. 跑 dev100 评测

在 AutoDL 项目根目录执行：

```bash
cd /root/autodl-tmp/graph
bash scripts/eval_spert_dev100_autodl.sh
```

这个脚本会自动完成：

1. 如果不存在 sample，则从原始数据生成固定 `dev100` 样本
2. 从 `outputs/spert/*/dev.json` 中抽取同一批 `sent_id`
3. 生成：
   - `outputs/dev100_eval/adkg/dev100.json`
   - `outputs/dev100_eval/mdkg/dev100.json`
4. 用最新 checkpoint 对这两个 `dev100` 文件评测

输出位置：

```text
outputs/logs/adkg_dev100_eval.log
outputs/logs/mdkg_dev100_eval.log
outputs/dev100_eval/adkg/
outputs/dev100_eval/mdkg/
```

## 4. 建议执行顺序

建议按这个顺序跑：

```text
先 test，再 dev100
```

对应命令：

```bash
cd /root/autodl-tmp/graph
bash scripts/eval_spert_test_autodl.sh
bash scripts/eval_spert_dev100_autodl.sh
```

如果想后台运行：

```bash
cd /root/autodl-tmp/graph
nohup bash scripts/eval_spert_test_autodl.sh > outputs/logs/eval_test_console.log 2>&1 &
nohup bash scripts/eval_spert_dev100_autodl.sh > outputs/logs/eval_dev100_console.log 2>&1 &
```

查看日志：

```bash
tail -f outputs/logs/adkg_test_eval.log
tail -f outputs/logs/mdkg_test_eval.log
tail -f outputs/logs/adkg_dev100_eval.log
tail -f outputs/logs/mdkg_dev100_eval.log
```

## 5. 跑完后需要带回本地的文件

最少同步这些文件回 Git 仓库：

```text
outputs/logs/adkg_test_eval.log
outputs/logs/mdkg_test_eval.log
outputs/logs/adkg_dev100_eval.log
outputs/logs/mdkg_dev100_eval.log
outputs/test_eval/adkg/
outputs/test_eval/mdkg/
outputs/dev100_eval/adkg/
outputs/dev100_eval/mdkg/
```

如果空间紧张，最少带回四个 log：

```text
outputs/logs/adkg_test_eval.log
outputs/logs/mdkg_test_eval.log
outputs/logs/adkg_dev100_eval.log
outputs/logs/mdkg_dev100_eval.log
```

因为当前 summary 主要缺的是可以解析的最终评测日志。

## 6. 当前为什么本地不能直接跑

当前本地工作区缺的是运行依赖，不是脚本本身：

- 本地没有 `outputs/checkpoints/`
- 本地没有 `outputs/logs/`
- 本地没有 `external/spert/`

所以这部分最合理的执行位置就是 AutoDL。

## 7. 跑完之后如何更新 summary

一旦四个评测日志同步回本地，就可以继续补这些文件：

- `outputs/final_summary/spert_adkg_test_metrics.md`
- `outputs/final_summary/spert_mdkg_test_metrics.md`
- `outputs/final_summary/spert_adkg_dev100_metrics.md`
- `outputs/final_summary/spert_mdkg_dev100_metrics.md`

并进一步更新：

- `outputs/final_summary/metrics_summary.md`
- `outputs/final_summary/metrics_summary.json`
