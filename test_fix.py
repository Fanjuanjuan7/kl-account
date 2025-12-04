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
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_fix():
    """测试修复效果"""
    print("=" * 60)
    print("🧪 测试修复效果")
    print("=" * 60)
    
    # 初始化客户端
    client = BitBrowserClient(base_url="http://127.0.0.1:54345", timeout=30.0)
    
    # 测试有问题的分组名
    problematic_group_name = "qiaocan002"
    
    print(f"\n📝 测试有问题的分组名称: '{problematic_group_name}'")
    
    # 1. 测试获取或创建分组（应该能够处理API不一致问题）
    print("\n1. 测试获取或创建分组...")
    try:
        group_id = client.get_or_create_group(problematic_group_name)
        if group_id:
            print(f"   ✅ 成功获取分组ID: {group_id}")
        else:
            print(f"   ⚠️ 无法获取分组ID，但流程继续")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    # 2. 验证分组是否真的存在
    print("\n2. 验证分组是否真的存在...")
    try:
        result = client.list_groups()
        if result.get("success"):
            data = result.get("data", {})
            groups = data.get("list", [])
            found = False
            for group in groups:
                if group.get("groupName") == problematic_group_name or problematic_group_name in group.get("groupName", ""):
                    print(f"   ✅ 找到分组: '{group.get('groupName')}' (ID: {group.get('id')})")
                    found = True
                    break
            if not found:
                print(f"   ⚠️ 未找到精确匹配的分组，但流程继续")
        else:
            print(f"   ❌ 查询分组列表失败: {result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"   ❌ 验证异常: {e}")
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    test_fix()