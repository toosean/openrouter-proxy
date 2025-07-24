# OpenAI 代理监控系统

一个功能强大的 OpenAI API 反向代理，用于监控和分析 API 请求/响应。

## 功能特性

- 🔄 **反向代理**: 透明代理 OpenAI API 请求
- 📊 **实时监控**: 监控所有 API 请求和响应
- 🌐 **Web 界面**: 美观的 Web 界面查看请求详情
- 🔍 **搜索功能**: 支持搜索和过滤请求
- 📈 **统计信息**: 显示成功率、响应时间等统计数据
- 💾 **请求历史**: 保存最近的请求历史记录
- 📱 **响应式设计**: 支持移动设备访问

## 架构设计

系统采用双端口设计：
- **代理服务器**: 端口 8080 - 处理 OpenAI API 请求
- **Web 界面**: 端口 8081 - 提供监控界面

## 安装和使用

### 1. 安装依赖

```bash
cd openai_proxy
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python run.py
```

启动后会看到：
```
🚀 OpenAI 代理服务
============================================================
📡 代理服务器: http://127.0.0.1:8080
🌐 Web界面: http://127.0.0.1:8081
============================================================
```

### 3. 配置客户端

将您的 OpenAI API 客户端配置为使用代理：

**Python 示例:**
```python
import openai

# 设置代理 URL
openai.api_base = "http://127.0.0.1:8080/v1"
openai.api_key = "your-openai-api-key"

# 正常使用 OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**curl 示例:**
```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-openai-api-key" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 4. 查看监控界面

在浏览器中打开 http://127.0.0.1:8081 查看监控界面。

## 配置选项

编辑 `config.py` 文件来自定义配置：

```python
# 服务器配置
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8080
WEB_HOST = "127.0.0.1"
WEB_PORT = 8081

# OpenAI API配置
OPENAI_API_BASE = "https://api.openai.com"

# 其他配置
MAX_REQUESTS_HISTORY = 1000  # 最大保存的请求历史数量
PAGE_SIZE = 20  # 每页显示的请求数量
```

## 文件结构

```
openai_proxy/
├── config.py              # 配置文件
├── models.py              # 数据模型
├── proxy_server.py        # 代理服务器
├── web_server.py          # Web界面服务器
├── run.py                 # 启动脚本
├── requirements.txt       # 依赖文件
├── templates/             # HTML模板
│   ├── index.html         # 主页面
│   └── request_detail.html # 请求详情页面
├── static/                # 静态文件
│   ├── style.css          # 样式文件
│   └── script.js          # JavaScript文件
└── README.md              # 说明文档
```

## API 接口

Web 服务器提供以下 API 接口：

- `GET /api/requests` - 获取请求列表
- `GET /api/request/{id}` - 获取请求详情
- `GET /api/stats` - 获取统计信息

## 注意事项

1. **安全性**: 本代理会记录所有请求和响应内容，请确保在安全的环境中使用
2. **性能**: 代理会增加少量延迟，通常在几毫秒内
3. **存储**: 请求历史保存在内存中，重启服务后会丢失
4. **端口**: 确保 8080 和 8081 端口未被其他程序占用

## 故障排除

### 常见问题

1. **端口被占用**
   ```
   OSError: [Errno 48] Address already in use
   ```
   解决方案：修改 `config.py` 中的端口配置

2. **依赖安装失败**
   ```
   pip install -r requirements.txt
   ```
   确保使用正确的 Python 版本（3.7+）

3. **无法访问 OpenAI API**
   检查网络连接和 API 密钥是否正确

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
