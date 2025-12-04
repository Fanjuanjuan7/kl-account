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
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def detailed_group_debug():
    """详细调试分组问题"""
    print("=" * 60)
    print("🔍 详细调试分组问题")
    print("=" * 60)
    
    # 初始化客户端
    client = BitBrowserClient(base_url="http://127.0.0.1:54345", timeout=30.0)
    
    # 测试分组名称
    test_group_name = "qiaocan002"
    
    print(f"\n📝 测试分组名称: '{test_group_name}'")
    
    # 1. 获取所有分组（多次）
    print("\n1. 获取所有分组（多次查询）...")
    for i in range(3):
        try:
            result = client.list_groups()
            print(f"   第{i+1}次查询结果: success={result.get('success')}")
            if result.get("success"):
                data = result.get("data", {})
                groups = data.get("list", [])
                print(f"   当前共有 {len(groups)} 个分组")
                for j, group in enumerate(groups):
                    group_name = group.get("groupName", "")
                    group_id = group.get("id", "")
                    print(f"     [{j+1}] '{group_name}' (ID: {group_id})")
            else:
                print(f"   ❌ 获取分组列表失败: {result.get('msg', '未知错误')}")
        except Exception as e:
            print(f"   ❌ 第{i+1}次查询异常: {e}")
    
    # 2. 尝试创建分组
    print(f"\n2. 尝试创建分组: '{test_group_name}'...")
    try:
        add_result = client.add_group(test_group_name)
        print(f"   创建结果: {add_result}")
        if add_result.get("success"):
            print("   ✅ 分组创建成功")
            data = add_result.get("data", {})
            if isinstance(data, dict):
                group_id = data.get("id")
                if group_id:
                    print(f"   新分组ID: {group_id}")
        else:
            print(f"   ❌ 分组创建失败: {add_result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"   ❌ 创建分组异常: {e}")
    
    # 3. 再次获取所有分组
    print("\n3. 再次获取所有分组...")
    try:
        result = client.list_groups()
        print(f"   查询结果: {result}")
        if result.get("success"):
            data = result.get("data", {})
            groups = data.get("list", [])
            print(f"   当前共有 {len(groups)} 个分组")
            for j, group in enumerate(groups):
                group_name = group.get("groupName", "")
                group_id = group.get("id", "")
                print(f"     [{j+1}] '{group_name}' (ID: {group_id})")
        else:
            print(f"   ❌ 获取分组列表失败: {result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"   ❌ 查询分组异常: {e}")

if __name__ == "__main__":
    detailed_group_debug()