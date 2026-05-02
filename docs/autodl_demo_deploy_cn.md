# AutoDL Demo 部署说明

这份文档只覆盖当前 Demo 控制台部署，不包含 baseline 训练细节。

## 一、适用范围

适用于你已经把项目代码放到 AutoDL 实例里的场景，例如：

```bash
cd /root/autodl-tmp
git clone https://github.com/<your-name>/<repo>.git graph
cd graph
```

如果仓库已经在实例里，直接进入项目目录即可。

## 二、一键准备命令

在 AutoDL 上执行：

```bash
cd /root/autodl-tmp/graph
bash scripts/autodl_deploy_demo.sh bios740-topic2
```

这个脚本会做：

1. 进入项目目录
2. 创建或复用 conda 环境
3. 安装 Python 依赖
4. 安装前端依赖
5. 构建前端 `web/dist`

## 三、启动服务

准备完成后，执行：

```bash
cd /root/autodl-tmp/graph
conda activate bios740-topic2
PYTHONPATH=src python -m uvicorn bios740_topic2.demo_api:app --host 0.0.0.0 --port 6008
```

如果想后台运行：

```bash
cd /root/autodl-tmp/graph
conda activate bios740-topic2
nohup env PYTHONPATH=src python -m uvicorn bios740_topic2.demo_api:app --host 0.0.0.0 --port 6008 > outputs/logs/demo_console.log 2>&1 &
```

## 四、页面访问

在 AutoDL 面板中：

1. 优先使用实例的 `6008` 端口
2. 在 AutoDL 的「自定义服务」里获取 `6008` 对应的公网访问地址
3. 用映射出的地址访问页面

注意：

- 不能用 `127.0.0.1:6008` 从你本地直接访问远端实例
- 必须使用 AutoDL 提供的端口映射地址
- 如果当前账号不能直接开放端口，可以使用 SSH 隧道访问远端 `6008`

### 关于 AutoDL 端口限制

根据 AutoDL 文档，实例默认适合映射到公网的端口主要是：

- `6006`
- `6008`

建议：

- `6008` 用于当前 Demo 页面
- `6006` 留给 TensorBoard 等训练可视化

如果你的账号有企业认证，可以直接通过「自定义服务」开放 `6008`。  
如果没有企业认证，优先改用 **SSH 隧道**，不要假设任意端口都能直接公网访问。

## 五、如果要跑真实 LLM 实验

先配置环境文件：

```bash
cd /root/autodl-tmp/graph
cp .env.llm.example .env.llm
```

然后编辑 `.env.llm`，填入例如：

```env
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=你的key
LLM_MODEL=deepseek-v4-flash
LLM_WIRE_API=chat_completions
```

## 六、更新代码后的正确顺序

如果你本地代码更新并重新推送了 GitHub：

```bash
cd /root/autodl-tmp/graph
git pull
cd web
npm run build
cd ..
```

如果改了下面任意内容，还要重启 `uvicorn`：

- `src/bios740_topic2/demo_api.py`
- `scripts/` 下的 Python 脚本
- `web/src/` 下的前端代码

## 七、常见问题

### 1. 页面还是旧版本

原因：

- 前端没重新 build
- 后端没重启

处理：

```bash
cd /root/autodl-tmp/graph/web
npm run build
cd ..
```

然后重启 `uvicorn`

### 2. 提示旧脚本路径不存在

例如：

```json
{
  "detail": "python: can't open file '/root/autodl-tmp/graph/scripts/sample_adkg_dev_for_llm.py'"
}
```

原因：

- 后端还在跑旧代码

处理：

- 停掉旧 `uvicorn`
- 重新启动服务

### 3. 页面打不开

优先检查：

1. `uvicorn` 是否启动成功
2. 是否监听 `0.0.0.0`
3. AutoDL `6008` 端口是否已经映射

## 八、推荐最短部署链路

如果你只想最快把页面跑起来，直接照这个执行：

```bash
cd /root/autodl-tmp/graph
bash scripts/autodl_deploy_demo.sh bios740-topic2
conda activate bios740-topic2
cp .env.llm.example .env.llm
PYTHONPATH=src python -m uvicorn bios740_topic2.demo_api:app --host 0.0.0.0 --port 6008
```
