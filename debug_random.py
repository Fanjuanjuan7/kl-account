#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import uuid

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

def test_with_random_name():
    """使用随机分组名测试"""
    print("=" * 60)
    print("🔍 使用随机分组名测试")
    print("=" * 60)
    
    # 初始化客户端
    client = BitBrowserClient(base_url="http://127.0.0.1:54345", timeout=30.0)
    
    # 生成随机分组名称
    random_group_name = f"test_group_{uuid.uuid4().hex[:8]}"
    
    print(f"\n📝 随机分组名称: '{random_group_name}'")
    
    # 1. 先查询所有分组
    print("\n1. 查询当前所有分组...")
    try:
        result = client.list_groups()
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
    
    # 2. 尝试创建随机分组
    print(f"\n2. 尝试创建随机分组: '{random_group_name}'...")
    try:
        add_result = client.add_group(random_group_name)
        print(f"   创建结果: {add_result}")
        if add_result.get("success"):
            print("   ✅ 随机分组创建成功!")
            data = add_result.get("data", {})
            if isinstance(data, dict):
                group_id = data.get("id")
                if group_id:
                    print(f"   新分组ID: {group_id}")
                    
                    # 3. 验证分组是否真的创建成功
                    print("\n3. 验证分组是否真的创建成功...")
                    verify_result = client.list_groups()
                    if verify_result.get("success"):
                        verify_data = verify_result.get("data", {})
                        verify_groups = verify_data.get("list", [])
                        found = False
                        for group in verify_groups:
                            if group.get("groupName") == random_group_name:
                                print(f"   ✅ 验证成功，找到新创建的分组: '{random_group_name}' (ID: {group.get('id')})")
                                found = True
                                break
                        if not found:
                            print(f"   ❌ 验证失败，未找到新创建的分组: '{random_group_name}'")
                    else:
                        print(f"   ❌ 验证查询失败: {verify_result.get('msg', '未知错误')}")
        else:
            print(f"   ❌ 随机分组创建失败: {add_result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"   ❌ 创建随机分组异常: {e}")

if __name__ == "__main__":
    test_with_random_name()