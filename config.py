"""
OpenAI代理配置文件
"""
import os

# 服务器配置
PROXY_HOST = os.getenv("PROXY_HOST", "127.0.0.1")
PROXY_PORT = int(os.getenv("PROXY_PORT", "8080"))
WEB_HOST = os.getenv("WEB_HOST", "127.0.0.1")
WEB_PORT = int(os.getenv("WEB_PORT", "8081"))

# OpenAI API配置
OPENAI_API_BASE = "https://openrouter.ai/api/v1"

# 日志配置
LOG_LEVEL = "INFO"
MAX_REQUESTS_HISTORY = 1000  # 最大保存的请求历史数量

# 界面配置
PAGE_SIZE = 20  # 每页显示的请求数量

# 默认APIKEY配置
DEFAULT_APIKEY = os.getenv("DEFAULT_APIKEY","")  # 默认APIKEY
SUPER_ADMIN_APIKEY = os.getenv("SUPER_ADMIN_APIKEY","")  # 管理员APIKEY
