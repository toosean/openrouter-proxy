# OpenRouter 代理监控系统

一个功能强大的 OpenRouter/OpenAI API 反向代理服务，提供完整的请求监控、用户管理和数据分析功能。

## ✨ 核心特性

### 🔄 反向代理功能
- **透明代理**: 完全兼容 OpenAI API 格式，无缝转发到 OpenRouter
- **流式响应支持**: 完整支持 SSE 流式输出，实时传输数据
- **自动重试**: 智能错误处理和连接管理
- **超时控制**: 可配置的请求超时设置（默认5分钟）

### 📊 实时监控系统
- **请求记录**: 详细记录所有API请求和响应
- **性能分析**: 响应时间、成功率、错误率统计
- **实时更新**: 前端实时刷新监控数据
- **数据持久化**: SQLite数据库存储，重启后数据不丢失

### 🔐 用户认证系统
- **API Key 认证**: 基于API Key的用户身份验证
- **权限分级**: 管理员可查看所有记录，普通用户只能查看自己的记录
- **Cookie会话**: 基于Cookie的登录状态管理
- **默认Key**: 支持为未提供API Key的请求设置默认Key

### 🌐 Web监控界面
- **现代UI设计**: 响应式界面，支持桌面和移动设备
- **请求列表**: 分页显示所有API请求记录
- **详情查看**: 点击查看完整的请求/响应详情
- **搜索过滤**: 支持按URL、方法、内容等多维度搜索
- **统计面板**: 实时显示总请求数、成功率、平均响应时间

### 🔍 高级搜索功能
- **全文搜索**: 在请求URL、方法、请求体、响应体中搜索
- **用户过滤**: 按API Key过滤显示特定用户的请求
- **时间排序**: 按时间倒序显示最新请求

## 🏗️ 系统架构

```
┌─────────────────┬─────────────────┐
│   代理服务器     │   Web监控界面   │
│   Port: 8080    │   Port: 8081    │
│                 │                 │
│ ┌─────────────┐ │ ┌─────────────┐ │
│ │ 请求转发    │ │ │ 用户认证    │ │
│ │ 流式处理    │ │ │ 数据展示    │ │
│ │ 错误处理    │ │ │ 搜索过滤    │ │
│ └─────────────┘ │ └─────────────┘ │
└─────────────────┴─────────────────┘
         │                   │
         └───────────────────┘
                   │
          ┌─────────────────┐
          │  SQLite 数据库  │
          │  请求记录存储   │
          └─────────────────┘
```

## 🚀 快速开始

### 环境要求
- Python 3.7+
- pip 包管理器

### 安装部署

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd openrouter-proxy
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动服务**
   ```bash
   python run.py
   ```

4. **访问服务**
   ```
   🚀 OpenAI 代理服务
   ============================================================
   📡 代理服务器: http://127.0.0.1:8080
   🌐 Web界面: http://127.0.0.1:8081
   ============================================================
   ```

### Docker 部署

使用 Docker Compose 快速部署：

```bash
docker-compose up -d
```

详细的 Docker 部署说明请参考 [DOCKER.md](DOCKER.md)

## 🔧 配置说明

### 基础配置 (config.py)

```python
# 服务器配置
PROXY_HOST = "127.0.0.1"        # 代理服务器主机
PROXY_PORT = 8080               # 代理服务器端口
WEB_HOST = "127.0.0.1"          # Web界面主机  
WEB_PORT = 8081                 # Web界面端口

# API配置
OPENAI_API_BASE = "https://openrouter.ai/api/v1"  # OpenRouter API地址
DEFAULT_APIKEY = "sk-hntsz-free-key"              # 默认API Key
SUPER_ADMIN_APIKEY = ""                           # 超管API Key

# 数据配置
MAX_REQUESTS_HISTORY = 1000     # 最大历史记录数
PAGE_SIZE = 20                  # 分页大小
```

### 环境变量支持

所有配置项都支持环境变量：

```bash
export PROXY_HOST=0.0.0.0
export PROXY_PORT=8080
export WEB_PORT=8081
export SUPER_ADMIN_APIKEY=your-admin-key
```

## 📖 使用指南

### 客户端配置

将你的 OpenAI 客户端配置为使用代理服务器：

#### Python (openai 库)
```python
import openai

# 新版本 (v1.0+)
client = openai.OpenAI(
    base_url="http://127.0.0.1:8080/v1",
    api_key="your-openrouter-api-key"
)

response = client.chat.completions.create(
    model="anthropic/claude-3.5-sonnet",
    messages=[{"role": "user", "content": "Hello!"}]
)

# 旧版本
openai.api_base = "http://127.0.0.1:8080/v1"
openai.api_key = "your-openrouter-api-key"
```

#### curl 示例
```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-openrouter-api-key" \
  -d '{
    "model": "anthropic/claude-3.5-sonnet",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

#### JavaScript/Node.js
```javascript
import OpenAI from 'openai';

const openai = new OpenAI({
  baseURL: 'http://127.0.0.1:8080/v1',
  apiKey: 'your-openrouter-api-key',
});

const response = await openai.chat.completions.create({
  model: 'anthropic/claude-3.5-sonnet',
  messages: [{ role: 'user', content: 'Hello!' }],
});
```

### Web界面使用

1. **登录认证**
   - 访问 `http://127.0.0.1:8081`
   - 输入你的 OpenRouter API Key 登录
   - 管理员Key可查看所有用户请求

2. **监控面板**
   - 查看实时统计：总请求数、成功率、平均响应时间
   - 浏览请求列表，支持分页导航
   - 使用搜索功能快速定位特定请求

3. **请求详情**
   - 点击任意请求查看完整详情
   - 包含请求头、请求体、响应头、响应体
   - 显示响应时间和状态码

## 🔌 API 接口

Web服务器提供 RESTful API：

### 获取请求列表
```http
GET /api/requests?page=1&search=keyword
```

**响应格式:**
```json
{
  "requests": [...],
  "total_count": 100,
  "page": 1,
  "page_size": 20
}
```

### 获取请求详情
```http
GET /api/request/{request_id}
```

### 获取统计信息
```http
GET /api/stats
```

**响应格式:**
```json
{
  "total_requests": 150,
  "success_rate": 98.5,
  "avg_response_time": 1250.3,
  "recent_requests_count": 10
}
```

## 🗄️ 数据存储

### SQLite 数据库结构

```sql
CREATE TABLE requests (
    id TEXT PRIMARY KEY,                -- 请求唯一ID
    timestamp TEXT NOT NULL,            -- 请求时间戳
    method TEXT NOT NULL,               -- HTTP方法
    url TEXT NOT NULL,                  -- 请求URL
    headers TEXT NOT NULL,              -- 请求头(JSON)
    body TEXT,                          -- 请求体
    authorization_bearer TEXT,          -- API Key
    response_status INTEGER,            -- 响应状态码
    response_headers TEXT,              -- 响应头(JSON)
    response_body TEXT,                 -- 响应体
    duration_ms REAL,                   -- 响应时间(毫秒)
    error TEXT                          -- 错误信息
);
```

### 数据特性
- **持久化存储**: 数据保存在 `proxy_requests.db` 文件中
- **并发安全**: 使用线程锁确保数据一致性
- **自动索引**: 按时间戳和API Key建立索引优化查询
- **搜索优化**: 支持全文搜索多个字段

## 🧪 测试验证

### 运行测试脚本

```bash
# 测试基本代理功能
python test_proxy.py

# 测试流式响应
python test_streaming.py
```

### 测试流程
1. 确保服务已启动
2. 运行测试脚本验证代理功能
3. 在Web界面查看测试请求记录
4. 验证统计数据更新

## 🐳 Docker 支持

### 快速部署
```bash
# 使用 docker-compose
docker-compose up -d

# 使用 docker
docker build -t openrouter-proxy .
docker run -p 8080:8080 -p 8081:8081 openrouter-proxy
```

### 配置挂载
```yaml
volumes:
  - ./data:/app/data          # 数据库文件持久化
  - ./config.py:/app/config.py # 自定义配置
```

## ⚠️ 注意事项

### 安全考虑
- **敏感数据**: 系统会记录完整的请求和响应内容，请在安全环境中使用
- **API Key保护**: API Key会以明文形式存储在数据库中，确保数据库文件安全
- **网络访问**: 默认只监听本地地址，生产环境请配置防火墙

### 性能影响
- **延迟增加**: 代理会增加 2-10ms 的延迟
- **内存使用**: 请求数据会占用额外内存和磁盘空间
- **并发处理**: 支持高并发请求，但受限于单机性能

### 存储管理
- **数据库大小**: 长期使用会产生大量数据，建议定期清理
- **备份策略**: 重要数据请定期备份 SQLite 数据库文件
- **磁盘空间**: 确保有足够磁盘空间存储请求日志

## 🛠️ 故障排除

### 常见问题

1. **端口被占用**
   ```
   OSError: [Errno 48] Address already in use
   ```
   - 修改 `config.py` 中的端口配置
   - 或使用环境变量 `PROXY_PORT`、`WEB_PORT`

2. **依赖安装失败**
   ```bash
   pip install -r requirements.txt --upgrade
   ```
   - 确保使用 Python 3.7+ 版本
   - 尝试使用虚拟环境

3. **数据库锁定**
   ```
   sqlite3.OperationalError: database is locked
   ```
   - 确保没有多个进程同时访问数据库
   - 重启服务解决锁定问题

4. **无法连接 OpenRouter**
   - 检查网络连接
   - 验证 API Key 是否有效
   - 确认 `OPENAI_API_BASE` 配置正确

### 日志调试

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 开发说明

### 项目结构
```
openrouter-proxy/
├── config.py              # 配置管理
├── models.py              # 数据模型和存储
├── proxy_server.py        # 代理服务器核心
├── web_server.py          # Web界面服务器
├── run.py                 # 启动入口
├── requirements.txt       # Python依赖
├── Dockerfile             # Docker镜像
├── docker-compose.yml     # Docker编排
├── templates/             # HTML模板
│   ├── index.html         # 主页面
│   ├── login.html         # 登录页面
│   └── request_detail.html # 请求详情页面
├── static/                # 静态资源
│   ├── style.css          # 样式文件
│   └── script.js          # 前端脚本
├── test_proxy.py          # 代理功能测试
├── test_streaming.py      # 流式响应测试
├── DOCKER.md              # Docker部署文档
├── USAGE.md               # 使用指南
└── README.md              # 项目说明
```

### 技术栈
- **后端**: Python 3.7+, aiohttp, SQLite
- **前端**: HTML5, CSS3, JavaScript (Vanilla)
- **数据库**: SQLite 3
- **模板引擎**: Jinja2
- **部署**: Docker, Docker Compose
