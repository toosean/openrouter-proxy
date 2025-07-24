# OpenAI 代理使用指南

## 🚀 快速开始

### 1. 启动服务

```bash
cd openai_proxy
python run.py
```

启动后您会看到：
```
🚀 OpenAI 代理服务
============================================================
📡 代理服务器: http://127.0.0.1:8080
🌐 Web界面: http://127.0.0.1:8081
============================================================
```

### 2. 配置您的应用

将您的OpenAI API客户端配置为使用代理服务器：

#### Python (openai库)
```python
import openai

# 方法1: 设置base_url
client = openai.OpenAI(
    api_key="your-real-openai-api-key",
    base_url="http://127.0.0.1:8080/v1"
)

# 方法2: 使用环境变量
import os
os.environ["OPENAI_API_KEY"] = "your-real-openai-api-key"
os.environ["OPENAI_BASE_URL"] = "http://127.0.0.1:8080/v1"

client = openai.OpenAI()

# 正常使用
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

#### JavaScript/Node.js
```javascript
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: 'your-real-openai-api-key',
  baseURL: 'http://127.0.0.1:8080/v1',
});

const response = await openai.chat.completions.create({
  model: 'gpt-3.5-turbo',
  messages: [{ role: 'user', content: 'Hello!' }],
});
```

#### curl
```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-real-openai-api-key" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 3. 查看监控界面

在浏览器中打开 http://127.0.0.1:8081 查看所有API请求的详细信息。

## 📊 Web界面功能

### 主页面功能
- **实时统计**: 显示总请求数、成功率、平均响应时间
- **请求列表**: 显示所有API请求的概览
- **搜索功能**: 支持按URL、方法、内容搜索
- **分页浏览**: 支持大量请求的分页显示
- **自动刷新**: 页面会自动更新统计信息

### 请求详情页面
- **基本信息**: 请求方法、URL、时间戳、响应状态、耗时
- **请求头**: 完整的HTTP请求头信息
- **请求体**: 格式化的JSON请求内容
- **响应头**: 完整的HTTP响应头信息
- **响应体**: 格式化的JSON响应内容
- **复制功能**: 一键复制请求/响应内容

## ⚙️ 配置选项

编辑 `config.py` 文件来自定义设置：

```python
# 服务器端口配置
PROXY_HOST = "127.0.0.1"    # 代理服务器地址
PROXY_PORT = 8080           # 代理服务器端口
WEB_HOST = "127.0.0.1"      # Web界面地址
WEB_PORT = 8081             # Web界面端口

# OpenAI API配置
OPENAI_API_BASE = "https://api.openai.com"  # OpenAI API基础URL

# API密钥配置
PASSTHROUGH_API_KEY = True  # 直接透传客户端的API密钥
MASK_API_KEY_IN_LOGS = True # 在日志中隐藏API密钥（推荐开启）
DEFAULT_API_KEY = ""        # 默认API密钥（可选，通常留空）

# 存储配置
MAX_REQUESTS_HISTORY = 1000  # 最大保存的请求历史数量
PAGE_SIZE = 20               # 每页显示的请求数量
```

### API密钥处理模式

代理支持**透传模式**，这意味着：

1. **客户端密钥优先**: 直接使用客户端请求头中的API密钥
2. **无需预配置**: 不需要在代理中预先配置API密钥
3. **多用户支持**: 不同客户端可以使用各自的API密钥
4. **安全透明**: 代理不存储或修改API密钥，只是透传

如果客户端没有提供API密钥，可以设置 `DEFAULT_API_KEY` 作为后备选项。

## 🔧 高级用法

### 1. 自定义端口
如果默认端口被占用，可以修改配置：

```python
# config.py
PROXY_PORT = 9080  # 改为其他端口
WEB_PORT = 9081    # 改为其他端口
```

### 2. 远程访问
如果需要从其他机器访问，修改主机地址：

```python
# config.py
PROXY_HOST = "0.0.0.0"  # 允许所有IP访问
WEB_HOST = "0.0.0.0"    # 允许所有IP访问
```

⚠️ **安全警告**: 只在安全的网络环境中使用远程访问！

### 3. 增加历史记录容量
```python
# config.py
MAX_REQUESTS_HISTORY = 5000  # 保存更多历史记录
```

## 🛠️ 故障排除

### 常见问题

#### 1. 端口被占用
```
OSError: [Errno 48] Address already in use
```
**解决方案**: 修改 `config.py` 中的端口配置，或停止占用端口的程序。

#### 2. 无法连接到OpenAI API
```
aiohttp.client_exceptions.ClientConnectorError
```
**解决方案**: 检查网络连接，确认可以访问 https://api.openai.com

#### 3. API密钥错误
```
401 Unauthorized
```
**解决方案**: 检查您的OpenAI API密钥是否正确且有效。

#### 4. 请求超时
```
asyncio.TimeoutError
```
**解决方案**: 检查网络连接，或在 `proxy_server.py` 中增加超时时间。

### 调试模式

启用详细日志：
```python
# 在 config.py 中添加
LOG_LEVEL = "DEBUG"
```

## 📈 性能优化

### 1. 内存使用
- 定期清理历史记录：重启服务或减少 `MAX_REQUESTS_HISTORY`
- 监控内存使用：使用系统监控工具

### 2. 响应时间
- 代理会增加约1-5ms的延迟
- 大部分延迟来自网络传输
- 使用更快的网络连接可以改善性能

## 🔒 安全注意事项

1. **API密钥安全**: 代理会记录包含API密钥的请求头，确保在安全环境中使用
2. **数据隐私**: 所有请求和响应内容都会被记录，包含敏感信息
3. **网络安全**: 默认只监听本地地址，避免暴露到公网
4. **访问控制**: 没有内置认证，请在安全环境中使用

## 📝 API接口

Web服务器提供REST API：

### GET /api/requests
获取请求列表
```bash
curl "http://127.0.0.1:8081/api/requests?page=1&search=gpt"
```

### GET /api/request/{id}
获取请求详情
```bash
curl "http://127.0.0.1:8081/api/request/eff79fe3-993d-4201-87b6-f6f26657fed9"
```

### GET /api/stats
获取统计信息
```bash
curl "http://127.0.0.1:8081/api/stats"
```

## 🤝 支持

如果遇到问题：
1. 检查日志输出
2. 确认配置正确
3. 测试网络连接
4. 查看本文档的故障排除部分
