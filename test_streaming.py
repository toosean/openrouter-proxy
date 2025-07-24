#!/usr/bin/env python3
"""
测试OpenAI代理的流式响应功能
"""
import requests
import json
import time

# 代理配置
PROXY_URL = "http://127.0.0.1:8080"
WEB_URL = "http://127.0.0.1:8081"

def test_streaming_request():
    """测试流式请求"""
    print("🌊 测试流式响应...")
    
    # 模拟OpenAI流式API请求
    test_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "请写一首关于编程的短诗"}
        ],
        "max_tokens": 150,
        "stream": True  # 启用流式响应
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-test-key-for-demo"
    }
    
    try:
        print(f"📡 发送流式请求到代理服务器: {PROXY_URL}/v1/chat/completions")
        
        # 发送流式请求到代理
        response = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            headers=headers,
            json=test_data,
            stream=True,  # 启用流式接收
            timeout=30
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("📥 接收流式数据:")
            chunk_count = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    chunk_count += 1
                    print(f"  块 {chunk_count}: {len(chunk)} 字节")
                    # 显示前100个字符
                    chunk_text = chunk.decode('utf-8', errors='ignore')
                    print(f"    内容: {chunk_text[:100]}...")
                    
                    if chunk_count >= 5:  # 只显示前5个块
                        print("    ...")
                        break
            
            print(f"✅ 流式响应测试完成！共接收 {chunk_count} 个数据块")
        else:
            print(f"❌ 请求失败: {response.text}")
        
        print(f"🌐 请在浏览器中查看监控界面: {WEB_URL}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_non_streaming_request():
    """测试非流式请求"""
    print("\n📄 测试非流式响应...")
    
    # 模拟OpenAI非流式API请求
    test_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello, world!"}
        ],
        "max_tokens": 50
        # 注意：没有 stream: True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-test-key-for-demo"
    }
    
    try:
        print(f"📡 发送非流式请求到代理服务器: {PROXY_URL}/v1/chat/completions")
        
        # 发送非流式请求到代理
        response = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            headers=headers,
            json=test_data,
            timeout=30
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📝 响应内容: {response.text[:200]}...")
        
        print("✅ 非流式响应测试完成！")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_different_endpoints():
    """测试不同的API端点"""
    print("\n🔄 测试不同API端点...")
    
    endpoints = [
        ("/v1/models", "GET", None),
        ("/v1/completions", "POST", {
            "model": "text-davinci-003",
            "prompt": "Hello",
            "max_tokens": 10
        }),
        ("/v1/embeddings", "POST", {
            "model": "text-embedding-ada-002",
            "input": "Hello world"
        })
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-test-key-for-demo"
    }
    
    for endpoint, method, data in endpoints:
        try:
            print(f"📡 测试 {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(f"{PROXY_URL}{endpoint}", headers=headers, timeout=10)
            else:
                response = requests.post(f"{PROXY_URL}{endpoint}", headers=headers, json=data, timeout=10)
            
            print(f"   状态码: {response.status_code}")
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🌊 OpenAI 代理流式响应测试工具")
    print("=" * 60)
    
    # 测试流式响应
    test_streaming_request()
    
    # 测试非流式响应
    test_non_streaming_request()
    
    # 测试不同端点
    test_different_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    print(f"   • 代理服务器: {PROXY_URL}")
    print(f"   • 监控界面: {WEB_URL}")
    print("   • 流式和非流式请求都会被正确处理和记录")
    print("   • 所有请求详情可在Web界面中查看")
    print("=" * 60)
