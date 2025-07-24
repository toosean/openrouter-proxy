# OpenAI 代理服务 Docker 部署指南

## 快速开始

### 使用 Docker Compose（推荐）

1. **构建并启动服务**：
   ```bash
   docker-compose up -d
   ```

2. **查看日志**：
   ```bash
   docker-compose logs -f
   ```

3. **停止服务**：
   ```bash
   docker-compose down
   ```

### 使用 Docker 命令

1. **构建镜像**：
   ```bash
   docker build -t openai-proxy .
   ```

2. **运行容器**：
   ```bash
   docker run -d \
     --name openai-proxy \
     -p 8080:8080 \
     -p 8081:8081 \
     -e PROXY_HOST=0.0.0.0 \
     -e WEB_HOST=0.0.0.0 \
     openai-proxy
   ```

## 访问服务

- **代理服务器**: http://localhost:8080
- **Web 监控界面**: http://localhost:8081

## 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `PROXY_HOST` | `127.0.0.1` | 代理服务器监听地址 |
| `PROXY_PORT` | `8080` | 代理服务器端口 |
| `WEB_HOST` | `127.0.0.1` | Web界面监听地址 |
| `WEB_PORT` | `8081` | Web界面端口 |

## 自定义配置

如果需要自定义配置，可以通过环境变量或挂载配置文件：

```bash
docker run -d \
  --name openai-proxy \
  -p 8080:8080 \
  -p 8081:8081 \
  -e PROXY_HOST=0.0.0.0 \
  -e PROXY_PORT=8080 \
  -e WEB_HOST=0.0.0.0 \
  -e WEB_PORT=8081 \
  openai-proxy
```

## 健康检查

容器包含健康检查功能，会定期检查 Web 服务是否正常运行。

## 故障排除

1. **查看容器日志**：
   ```bash
   docker logs openai-proxy
   ```

2. **进入容器调试**：
   ```bash
   docker exec -it openai-proxy /bin/bash
   ```

3. **检查端口占用**：
   ```bash
   docker port openai-proxy
   ```
