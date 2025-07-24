"""
Web界面服务器
"""
import json
import logging
from aiohttp import web
from aiohttp_jinja2 import setup as jinja2_setup, template
import aiohttp_jinja2
import jinja2
from pathlib import Path

from models import request_storage
from config import WEB_HOST, WEB_PORT, PAGE_SIZE, SUPER_ADMIN_APIKEY, DEFAULT_APIKEY

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_apikey_from_request(request: web.Request) -> str:
    """从请求中获取APIKEY"""
    # 从Cookie获取
    apikey = request.cookies.get('apikey', '').strip()
    if apikey:
        return apikey
    
    return ''

def should_filter_by_apikey(apikey: str) -> str:
    """判断是否需要按APIKEY过滤，返回过滤用的APIKEY"""
    if not apikey:
        return None
    
    # 默认管理员key可以查看所有记录
    if apikey == SUPER_ADMIN_APIKEY:
        return None
    
    # 其他key只能查看自己的记录
    return apikey

@web.middleware
async def cors_middleware(request: web.Request, handler):
    """CORS中间件"""
    # 处理预检请求
    if request.method == 'OPTIONS':
        response = web.Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response
    
    # 处理实际请求
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    
    return response

@web.middleware
async def auth_middleware(request: web.Request, handler):
    """认证中间件"""
    # 登录页面和静态文件不需要认证
    if request.path in ['/login', '/static'] or request.path.startswith('/static/'):
        return await handler(request)
    
    apikey = get_apikey_from_request(request)
    
    # 如果没有APIKEY，重定向到登录页面
    if not apikey:
        if request.path.startswith('/api/'):
            return web.json_response({'error': 'API Key required'}, status=401)
        else:
            return web.HTTPFound('/login')
    
    # 将APIKEY添加到请求中
    request['apikey'] = apikey
    request['apikey_filter'] = should_filter_by_apikey(apikey)
    
    return await handler(request)

class WebServer:
    """Web界面服务器类"""

    @template('login.html')
    async def login(self, request: web.Request) -> dict:
        """登录页面"""
        return {'default_apikey': DEFAULT_APIKEY}

    @template('index.html')
    async def index(self, request: web.Request) -> dict:
        """主页面"""
        page = int(request.query.get('page', 1))
        search = request.query.get('search', '').strip()
        apikey_filter = request.get('apikey_filter')

        offset = (page - 1) * PAGE_SIZE

        if search:
            requests = request_storage.search_requests(search, limit=PAGE_SIZE, apikey_filter=apikey_filter)
            total_count = len(requests)
        else:
            requests = request_storage.get_requests(limit=PAGE_SIZE, offset=offset, apikey_filter=apikey_filter)
            total_count = request_storage.get_total_count(apikey_filter=apikey_filter)

        total_pages = (total_count + PAGE_SIZE - 1) // PAGE_SIZE

        return {
            'requests': requests,
            'current_page': page,
            'total_pages': total_pages,
            'total_count': total_count,
            'search': search,
            'page_size': PAGE_SIZE,
            'current_apikey': request.get('apikey', ''),
            'is_admin': request.get('apikey') == SUPER_ADMIN_APIKEY
        }

    @template('request_detail.html')
    async def request_detail(self, request: web.Request) -> dict:
        """请求详情页面"""
        request_id = request.match_info['request_id']
        record = request_storage.get_request(request_id)

        if not record:
            raise web.HTTPNotFound(text="Request not found")

        return {'record': record}

    async def api_requests(self, request: web.Request) -> web.Response:
        """API: 获取请求列表"""
        page = int(request.query.get('page', 1))
        search = request.query.get('search', '').strip()
        apikey_filter = request.get('apikey_filter')

        offset = (page - 1) * PAGE_SIZE

        if search:
            requests = request_storage.search_requests(search, limit=PAGE_SIZE, apikey_filter=apikey_filter)
            total_count = len(requests)
        else:
            requests = request_storage.get_requests(limit=PAGE_SIZE, offset=offset, apikey_filter=apikey_filter)
            total_count = request_storage.get_total_count(apikey_filter=apikey_filter)

        return web.json_response({
            'requests': [req.to_dict() for req in requests],
            'total_count': total_count,
            'page': page,
            'page_size': PAGE_SIZE
        })

    async def api_request_detail(self, request: web.Request) -> web.Response:
        """API: 获取请求详情"""
        request_id = request.match_info['request_id']
        record = request_storage.get_request(request_id)

        if not record:
            raise web.HTTPNotFound(text="Request not found")

        return web.json_response(record.to_dict())

    async def api_stats(self, request: web.Request) -> web.Response:
        """API: 获取统计信息"""
        apikey_filter = request.get('apikey_filter')
        
        total_requests = request_storage.get_total_count(apikey_filter=apikey_filter)
        recent_requests = request_storage.get_requests(limit=10, apikey_filter=apikey_filter)

        # 计算成功率
        success_count = sum(1 for req in recent_requests
                          if req.response_status and 200 <= req.response_status < 300)
        success_rate = (success_count / len(recent_requests) * 100) if recent_requests else 0

        # 计算平均响应时间
        response_times = [req.duration_ms for req in recent_requests
                         if req.duration_ms is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return web.json_response({
            'total_requests': total_requests,
            'success_rate': round(success_rate, 2),
            'avg_response_time': round(avg_response_time, 2),
            'recent_requests_count': len(recent_requests)
        })

async def create_web_app() -> web.Application:
    """创建Web应用"""
    app = web.Application(middlewares=[cors_middleware, auth_middleware])

    # 设置模板引擎
    template_dir = Path(__file__).parent / 'templates'
    jinja2_setup(app, loader=jinja2.FileSystemLoader(str(template_dir)))

    # 设置静态文件
    static_dir = Path(__file__).parent / 'static'
    app.router.add_static('/static/', path=static_dir, name='static')

    # 创建Web服务器实例
    web_server = WebServer()

    # 添加路由
    app.router.add_get('/login', web_server.login, name='login')
    app.router.add_get('/', web_server.index, name='index')
    app.router.add_get('/request/{request_id}', web_server.request_detail, name='request_detail')

    # API路由
    app.router.add_get('/api/requests', web_server.api_requests, name='api_requests')
    app.router.add_get('/api/request/{request_id}', web_server.api_request_detail, name='api_request_detail')
    app.router.add_get('/api/stats', web_server.api_stats, name='api_stats')

    return app

async def main():
    """主函数"""
    app = await create_web_app()

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, WEB_HOST, WEB_PORT)
    await site.start()

    logger.info(f"Web Server started on http://{WEB_HOST}:{WEB_PORT}")

    try:
        import asyncio
        await asyncio.Future()  # 永远运行
    except KeyboardInterrupt:
        logger.info("Shutting down web server...")
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())