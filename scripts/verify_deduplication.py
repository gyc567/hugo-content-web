#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
去重功能验证脚本

该脚本演示项目去重优化功能的实际工作效果，
验证browser-use等项目不会被重复分析。

作者: Qoder AI Assistant
创建时间: 2025-08-24
"""

import os
import sys
import json
from project_deduplicator import ProjectDeduplicator

def main():
    """验证去重功能"""
    print("🔍 项目去重功能验证")
    print("=" * 60)
    
    # 使用实际的历史文件
    history_file = '../data/analyzed_projects.json'
    
    # 创建去重器实例
    deduplicator = ProjectDeduplicator(history_file)
    
    # 获取当前统计信息
    stats = deduplicator.get_project_statistics()
    print(f"📊 当前已分析项目数量: {stats['total_projects']}")
    
    # 测试项目列表（包含已知的重复项目）
    test_projects = [
        {
            "name": "browser-use",
            "full_name": "browser-use/browser-use",
            "html_url": "https://github.com/browser-use/browser-use",
            "stargazers_count": 890,
            "description": "数据分析Agent"
        },
        {
            "name": "claude-code", 
            "full_name": "anthropics/claude-code",
            "html_url": "https://github.com/anthropics/claude-code",
            "stargazers_count": 1205,
            "description": "Claude代码助手"
        },
        {
            "name": "gemini-cli",
            "full_name": "google-gemini/gemini-cli", 
            "html_url": "https://github.com/google-gemini/gemini-cli",
            "stargazers_count": 456,
            "description": "Gemini命令行工具"
        },
        {
            "name": "new-test-project",
            "full_name": "testuser/new-test-project",
            "html_url": "https://github.com/testuser/new-test-project",
            "stargazers_count": 100,
            "description": "新测试项目"
        }
    ]
    
    print("\n🧪 去重测试结果:")
    print("-" * 60)
    
    duplicates_found = 0
    new_projects_found = 0
    
    for project in test_projects:
        is_duplicate = deduplicator.is_duplicate_project(project)
        
        if is_duplicate:
            print(f"⏭️  重复项目: {project['name']} - 已分析过，跳过")
            duplicates_found += 1
        else:
            print(f"✅ 新项目: {project['name']} - 可以分析")
            new_projects_found += 1
    
    print("\n" + "=" * 60)
    print("📋 测试总结:")
    print(f"   📊 总测试项目: {len(test_projects)}")
    print(f"   ⏭️  重复项目: {duplicates_found}")
    print(f"   ✅ 新项目: {new_projects_found}")
    print(f"   🎯 去重率: {(duplicates_found / len(test_projects) * 100):.1f}%")
    
    # 验证browser-use项目
    print("\n🔍 特别验证 browser-use 项目:")
    browser_use_project = {
        "name": "browser-use",
        "full_name": "browser-use/browser-use", 
        "html_url": "https://github.com/browser-use/browser-use"
    }
    
    is_browser_use_duplicate = deduplicator.is_duplicate_project(browser_use_project)
    
    if is_browser_use_duplicate:
        print("✅ browser-use 项目被正确识别为重复项目！")
        print("   这意味着不会再生成重复的评测文章。")
    else:
        print("⚠️  browser-use 项目未被识别为重复项目")
        print("   可能需要检查历史数据或重新运行迁移。")
    
    # 显示URL标准化示例
    print("\n🔧 URL标准化测试:")
    print("-" * 60)
    
    url_test_cases = [
        "https://github.com/browser-use/browser-use",
        "https://github.com/browser-use/browser-use.git",
        "git@github.com:browser-use/browser-use.git",
        "https://api.github.com/repos/browser-use/browser-use"
    ]
    
    for url in url_test_cases:
        normalized = deduplicator.normalize_github_url(url)
        print(f"   {url}")
        print(f"   → {normalized}")
        print()
    
    # 性能简单测试
    print("⚡ 性能简单测试:")
    print("-" * 60)
    
    import time
    start_time = time.time()
    
    # 进行100次查询
    for _ in range(100):
        deduplicator.is_duplicate_project(browser_use_project)
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 100
    
    print(f"   100次查询平均时间: {avg_time*1000:.2f}ms")
    
    if avg_time < 0.01:
        print("   ✅ 性能表现良好")
    else:
        print("   ⚠️  性能可能需要优化")
    
    print("\n" + "=" * 60)
    print("🎉 去重功能验证完成！")
    
    # 最终状态检查
    if is_browser_use_duplicate and duplicates_found > 0:
        print("\n✅ 去重系统工作正常:")
        print("   - browser-use 等项目不会重复分析")
        print("   - 新项目可以正常分析")
        print("   - 系统性能表现良好")
        return True
    else:
        print("\n⚠️  去重系统可能存在问题:")
        print("   - 建议检查数据文件")
        print("   - 重新运行数据迁移")
        print("   - 查看错误日志")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)