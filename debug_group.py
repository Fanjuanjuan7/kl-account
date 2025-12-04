#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 禁用代理
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.integrations.bitbrowser import BitBrowserClient
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_group_functionality():
    """测试分组功能"""
    print("=" * 60)
    print("🔍 测试分组功能")
    print("=" * 60)
    
    # 初始化客户端
    client = BitBrowserClient(base_url="http://127.0.0.1:54345", timeout=30.0)
    
    # 测试分组名称
    test_group_name = "qiaocan002"
    
    print(f"\n📝 测试分组名称: '{test_group_name}'")
    
    # 1. 获取所有分组
    print("\n1. 获取所有分组...")
    try:
        result = client.list_groups()
        print(f"   结果: {result}")
        
        if result.get("success"):
            data = result.get("data", {})
            groups = data.get("list", [])
            print(f"   当前共有 {len(groups)} 个分组")
            for i, group in enumerate(groups):
                group_name = group.get("groupName", "")
                group_id = group.get("id", "")
                print(f"   [{i+1}] '{group_name}' (ID: {group_id})")
        else:
            print(f"   ❌ 获取分组列表失败: {result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"   ❌ 获取分组列表异常: {e}")
    
    # 2. 测试获取或创建分组
    print(f"\n2. 测试获取或创建分组: '{test_group_name}'...")
    try:
        # 先列出所有分组
        print("   先列出所有分组...")
        list_result = client.list_groups()
        print(f"   分组列表: {list_result}")
        
        group_id = client.get_or_create_group(test_group_name)
        print(f"   结果: {group_id}")
        if group_id:
            print(f"   ✅ 成功获取分组ID: {group_id}")
        else:
            print(f"   ❌ 无法获取分组ID")
    except Exception as e:
        print(f"   ❌ 获取或创建分组异常: {e}")
    
    # 3. 再次获取所有分组验证
    print("\n3. 再次获取所有分组验证...")
    try:
        result = client.list_groups()
        print(f"   结果: {result}")
        
        if result.get("success"):
            data = result.get("data", {})
            groups = data.get("list", [])
            print(f"   当前共有 {len(groups)} 个分组")
            found = False
            for group in groups:
                group_name = group.get("groupName", "")
                group_id = group.get("id", "")
                if group_name == test_group_name:
                    print(f"   ✅ 找到目标分组: '{group_name}' (ID: {group_id})")
                    found = True
            if not found:
                print(f"   ❌ 未找到目标分组: '{test_group_name}'")
        else:
            print(f"   ❌ 获取分组列表失败: {result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"   ❌ 获取分组列表异常: {e}")

if __name__ == "__main__":
    test_group_functionality()