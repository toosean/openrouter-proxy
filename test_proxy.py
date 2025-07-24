#!/usr/bin/env python3
"""
测试OpenAI代理的脚本
"""
import requests
import json
import time

# 代理配置
PROXY_URL = "http://127.0.0.1:8080"
WEB_URL = "http://127.0.0.1:8081"

def test_proxy():
    """测试代理功能"""
    print("🧪 测试 OpenAI 代理...")
    
    # 模拟OpenAI API请求
    test_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello, this is a test message!"}
        ],
        "max_tokens": 100
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-test-key-for-demo"
    }
    
    try:
        print(f"📡 发送请求到代理服务器: {PROXY_URL}/v1/chat/completions")
        
        # 发送请求到代理
        response = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            headers=headers,
            json=test_data,
            timeout=30
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📝 响应内容: {response.text[:200]}...")
        
        # 等待一下让请求被记录
        time.sleep(1)
        
        print(f"🌐 请在浏览器中查看监控界面: {WEB_URL}")
        print("✅ 测试完成！您应该能在Web界面中看到这个请求的详细信息。")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_multiple_requests():
    """测试多个请求"""
    print("\n🔄 发送多个测试请求...")
    
    test_cases = [
        {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "What is Python?"}],
            "max_tokens": 50
        },
        {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Explain machine learning"}],
            "max_tokens": 100
        },
        {
            "model": "text-davinci-003",
            "prompt": "Write a short poem about coding",
            "max_tokens": 80
        }
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-test-key-for-demo"
    }
    
    for i, test_data in enumerate(test_cases, 1):
        try:
            print(f"📤 发送请求 {i}/3...")
            
            # 根据模型选择不同的端点
            if "davinci" in test_data.get("model", ""):
                endpoint = f"{PROXY_URL}/v1/completions"
            else:
                endpoint = f"{PROXY_URL}/v1/chat/completions"
            
            response = requests.post(
                endpoint,
                headers=headers,
                json=test_data,
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            time.sleep(0.5)  # 短暂延迟
            
        except Exception as e:
            print(f"   ❌ 请求 {i} 失败: {e}")
    
    print("✅ 多请求测试完成！")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 OpenAI 代理测试工具")
    print("=" * 60)
    
    # 基本测试
    test_proxy()
    
    # 多请求测试
    test_multiple_requests()
    
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    print(f"   • 代理服务器: {PROXY_URL}")
    print(f"   • 监控界面: {WEB_URL}")
    print("   • 所有请求都会被记录和显示在Web界面中")
    print("=" * 60)
