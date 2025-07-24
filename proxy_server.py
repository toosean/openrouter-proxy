"""
OpenAI API 反向代理服务器
"""
import asyncio
import aiohttp
import json
import time
import logging
from aiohttp import web, ClientSession, ClientTimeout
from typing import Dict, Any, Optional
from urllib.parse import urljoin

from models import request_storage
from config import (
    PROXY_HOST, PROXY_PORT, OPENAI_API_BASE, DEFAULT_APIKEY
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIProxy:
    """OpenAI API 代理类"""

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.timeout = ClientTimeout(total=300)  # 5分钟超时

    def _prepare_headers(self, original_headers: Dict[str, str]) -> Dict[str, str]:
        """准备转发的请求头"""
        # 移除不需要转发的头部
        forward_headers = {k: v for k, v in original_headers.items()
                         if k.lower() not in ['host', 'content-length']}

        # 如果没有Authorization头，添加默认API Key
        if not any(k.lower() == 'authorization' for k in forward_headers.keys()):
            forward_headers['Authorization'] = f'Bearer {DEFAULT_APIKEY}'

        return forward_headers

    async def init_session(self):
        """初始化HTTP会话"""
        if not self.session:
            self.session = ClientSession(timeout=self.timeout)

    async def close_session(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _handle_regular_response(self, response, response_headers: Dict[str, str],
                                     request_id: str, start_time: float) -> web.Response:
        """处理普通（非流式）响应"""
        # 读取完整响应
        response_body = await response.read()

        # 计算耗时
        duration_ms = (time.time() - start_time) * 1000

        # 尝试解析响应体为JSON格式化
        try:
            if response.content_type == 'application/json':
                response_json = json.loads(response_body.decode('utf-8'))
                formatted_response = json.dumps(response_json, ensure_ascii=False, indent=2)
            else:
                formatted_response = response_body.decode('utf-8')
        except:
            formatted_response = response_body.decode('utf-8', errors='ignore')

        # 更新请求记录
        request_storage.update_response(
            request_id=request_id,
            status=response.status,
            headers=response_headers,
            body=formatted_response,
            duration_ms=duration_ms
        )

        logger.info(f"Response {response.status} for {request_id} ({duration_ms:.2f}ms)")

        # 返回响应
        return web.Response(
            body=response_body,
            status=response.status,
            headers=response_headers
        )

    async def _handle_streaming_response(self, response, response_headers: Dict[str, str],
                                       request_id: str, start_time: float,
                                       original_request: web.Request) -> web.StreamResponse:
        """处理流式响应"""
        logger.info(f"Handling streaming response for {request_id}")

        # 确保必要的CORS和流式响应头
        headers = dict(response_headers)
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        headers['Access-Control-Allow-Headers'] = '*'
        headers['Cache-Control'] = 'no-cache'
        headers['Connection'] = 'keep-alive'

        # 创建流式响应
        stream_response = web.StreamResponse(
            status=response.status,
            headers=headers
        )

        # 准备流式响应
        await stream_response.prepare(original_request)

        # 用于收集流式数据
        collected_chunks = []

        try:
            # 逐块转发数据，使用更小的块大小以提高响应性
            async for chunk in response.content.iter_any():
                if chunk:
                    collected_chunks.append(chunk)
                    await stream_response.write(chunk)
                    # 立即刷新数据到客户端
                    await stream_response.drain()

            # 计算耗时
            duration_ms = (time.time() - start_time) * 1000

            # 合并所有块用于记录
            full_response = b''.join(collected_chunks)
            try:
                formatted_response = full_response.decode('utf-8')
            except:
                formatted_response = full_response.decode('utf-8', errors='ignore')

            # 更新请求记录
            request_storage.update_response(
                request_id=request_id,
                status=response.status,
                headers=response_headers,
                body=formatted_response,
                duration_ms=duration_ms
            )

            logger.info(f"Streaming response completed for {request_id} ({duration_ms:.2f}ms)")

        except asyncio.CancelledError:
            logger.info(f"Streaming response cancelled for {request_id}")
            raise
        except Exception as e:
            logger.error(f"Error in streaming response for {request_id}: {e}")
            # 记录错误
            duration_ms = (time.time() - start_time) * 1000
            request_storage.update_response(
                request_id=request_id,
                status=response.status,
                headers=response_headers,
                body=None,
                duration_ms=duration_ms,
                error=str(e)
            )
            raise

        finally:
            try:
                await stream_response.write_eof()
            except:
                pass  # 忽略EOF写入错误

        return stream_response
    
    async def proxy_request(self, request: web.Request) -> web.StreamResponse:
        """代理请求处理"""
        start_time = time.time()
        
        # 记录请求信息
        method = request.method
        path = request.path_qs
        headers = dict(request.headers)
        
        # 读取请求体
        body_bytes = None
        try:
            if request.content_type == 'application/json':
                body_data = await request.json()
                body_str = json.dumps(body_data, ensure_ascii=False, indent=2)
                body_bytes = body_str.encode('utf-8')
            else:
                body_bytes = await request.read()
                body_str = body_bytes.decode('utf-8') if body_bytes else None
        except Exception as e:
            body_str = f"Error reading body: {str(e)}"
            body_bytes = None
        
        # 构建目标URL
        target_url = OPENAI_API_BASE + path

        # 准备转发的头部和API密钥
        forward_headers = self._prepare_headers(headers)
        log_headers = dict(headers)

        request_id = request_storage.add_request(
            method=method,
            url=target_url,
            headers=log_headers,
            body=body_str
        )

        logger.info(f"Proxying {method} {target_url} [ID: {request_id}]")

        try:
            await self.init_session()
            
            # 发送请求到OpenAI API
            async with self.session.request(
                method=method,
                url=target_url,
                headers=forward_headers,
                data=body_bytes if method in ['POST', 'PUT', 'PATCH'] else None
            ) as response:

                response_headers = dict(response.headers)

                # 检查是否为流式响应
                # 1. 检查响应头中的content-type
                content_type = response_headers.get('content-type', '').lower()
                is_streaming = (
                    content_type.startswith('text/event-stream') or
                    content_type.startswith('text/plain') or  # OpenAI有时使用text/plain
                    response_headers.get('transfer-encoding', '').lower() == 'chunked'
                )

                # 2. 如果响应头不明确，检查请求体中是否有stream参数
                if not is_streaming and body_str:
                    try:
                        if request.content_type == 'application/json':
                            body_data = json.loads(body_str)
                            is_streaming = body_data.get('stream', False)
                    except:
                        pass

                if is_streaming:
                    # 处理流式响应
                    return await self._handle_streaming_response(
                        response, response_headers, request_id, start_time, request
                    )
                else:
                    # 处理普通响应
                    return await self._handle_regular_response(
                        response, response_headers, request_id, start_time
                    )
                
        except Exception as e:
            error_msg = str(e)
            duration_ms = (time.time() - start_time) * 1000
            
            # 记录错误
            request_storage.update_response(
                request_id=request_id,
                status=500,
                headers={},
                body=None,
                duration_ms=duration_ms,
                error=error_msg
            )
            
            logger.error(f"Proxy error for {request_id}: {error_msg}")
            
            return web.Response(
                text=json.dumps({"error": error_msg}),
                status=500,
                content_type='application/json'
            )

async def create_app() -> web.Application:
    """创建应用"""
    app = web.Application()
    proxy = OpenAIProxy()
    
    # 添加所有路由到代理处理器
    app.router.add_route('*', '/{path:.*}', proxy.proxy_request)
    
    # 清理资源
    async def cleanup_context(app):
        yield
        await proxy.close_session()
    
    app.cleanup_ctx.append(cleanup_context)
    
    return app

async def main():
    """主函数"""
    app = await create_app()
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, PROXY_HOST, PROXY_PORT)
    await site.start()
    
    logger.info(f"OpenAI Proxy Server started on http://{PROXY_HOST}:{PROXY_PORT}")
    
    try:
        await asyncio.Future()  # 永远运行
    except KeyboardInterrupt:
        logger.info("Shutting down proxy server...")
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
