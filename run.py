#!/usr/bin/env python3
"""
OpenAI 代理服务启动脚本
"""
import asyncio
import logging
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

from proxy_server import main as proxy_main
from web_server import main as web_main
from config import PROXY_HOST, PROXY_PORT, WEB_HOST, WEB_PORT

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProxyService:
    """代理服务管理器"""
    
    def __init__(self):
        self.proxy_task = None
        self.web_task = None
        self.running = False
    
    async def start(self):
        """启动所有服务"""
        logger.info("正在启动 OpenAI 代理服务...")
        
        try:
            # 启动代理服务器
            logger.info(f"启动代理服务器: http://{PROXY_HOST}:{PROXY_PORT}")
            self.proxy_task = asyncio.create_task(proxy_main())
            
            # 启动Web界面服务器
            logger.info(f"启动Web界面服务器: http://{WEB_HOST}:{WEB_PORT}")
            self.web_task = asyncio.create_task(web_main())
            
            self.running = True
            
            # 等待任务完成
            await asyncio.gather(self.proxy_task, self.web_task)
            
        except Exception as e:
            logger.error(f"启动服务时发生错误: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """停止所有服务"""
        if not self.running:
            return
        
        logger.info("正在停止服务...")
        self.running = False
        
        # 取消任务
        if self.proxy_task and not self.proxy_task.done():
            self.proxy_task.cancel()
            try:
                await self.proxy_task
            except asyncio.CancelledError:
                pass
        
        if self.web_task and not self.web_task.done():
            self.web_task.cancel()
            try:
                await self.web_task
            except asyncio.CancelledError:
                pass
        
        logger.info("所有服务已停止")

async def main():
    """主函数"""
    service = ProxyService()
    
    # 设置信号处理器
    def signal_handler(signum, frame):
        logger.info(f"收到信号 {signum}，正在关闭服务...")
        asyncio.create_task(service.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print("=" * 60)
        print("🚀 OpenAI 代理服务")
        print("=" * 60)
        print(f"📡 代理服务器: http://{PROXY_HOST}:{PROXY_PORT}")
        print(f"🌐 Web界面: http://{WEB_HOST}:{WEB_PORT}")
        print("=" * 60)
        print("💡 使用说明:")
        print(f"   1. 将您的OpenAI API请求发送到: http://{PROXY_HOST}:{PROXY_PORT}")
        print(f"   2. 在浏览器中打开: http://{WEB_HOST}:{WEB_PORT} 查看监控界面")
        print("   3. 按 Ctrl+C 停止服务")
        print("=" * 60)
        
        await service.start()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    except Exception as e:
        logger.error(f"服务运行时发生错误: {e}")
    finally:
        await service.stop()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
