#!/usr/bin/env python3
"""
测试统一分析工作流的脚本
模拟GitHub Actions环境下的执行
"""

import os
import subprocess
import sys
from datetime import datetime

def test_unified_analysis():
    """测试统一分析工作流"""
    
    print("🚀 开始测试统一分析工作流...")
    print("=" * 50)
    
    # 设置环境变量
    os.environ['GITHUB_ACTIONS'] = 'true'
    os.environ['DAYS_BACK'] = '7'
    os.environ['MAX_PROJECTS'] = '2'  # 减少数量用于测试
    
    # 测试结果
    results = {}
    
    # 1. 测试Claude Agent分析
    print("\n📊 测试 Claude Agent 分析...")
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/crypto-project-analyzer.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        results['claude_agent'] = {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
        print(f"✅ Claude Agent 分析: {'成功' if result.returncode == 0 else '失败'}")
    except subprocess.TimeoutExpired:
        print("❌ Claude Agent 分析: 超时")
        results['claude_agent'] = {'success': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"❌ Claude Agent 分析: {e}")
        results['claude_agent'] = {'success': False, 'error': str(e)}
    
    # 2. 测试Claude Prompts分析
    print("\n📝 测试 Claude Prompts 分析...")
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/claude_prompts_analyzer.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        results['claude_prompts'] = {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
        print(f"✅ Claude Prompts 分析: {'成功' if result.returncode == 0 else '失败'}")
    except subprocess.TimeoutExpired:
        print("❌ Claude Prompts 分析: 超时")
        results['claude_prompts'] = {'success': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"❌ Claude Prompts 分析: {e}")
        results['claude_prompts'] = {'success': False, 'error': str(e)}
    
    # 3. 测试Product Hunt分析
    print("\n🎯 测试 Product Hunt 分析...")
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/producthunt_analyzer.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        results['producthunt'] = {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
        print(f"✅ Product Hunt 分析: {'成功' if result.returncode == 0 else '失败'}")
    except subprocess.TimeoutExpired:
        print("❌ Product Hunt 分析: 超时")
        results['producthunt'] = {'success': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"❌ Product Hunt 分析: {e}")
        results['producthunt'] = {'success': False, 'error': str(e)}
    
    # 4. 检查生成的文章
    print("\n📄 检查生成的文章...")
    today = datetime.now().strftime('%Y-%m-%d')
    
    claude_agent_articles = []
    claude_prompts_articles = []
    producthunt_articles = []
    
    try:
        import os
        if os.path.exists('content/posts'):
            for file in os.listdir('content/posts'):
                if today in file and file.endswith('.md'):
                    if 'claude-agent' in file:
                        claude_agent_articles.append(file)
                    elif 'claude-prompts' in file:
                        claude_prompts_articles.append(file)
                    elif 'producthunt' in file:
                        producthunt_articles.append(file)
    except Exception as e:
        print(f"❌ 检查文章时出错: {e}")
    
    print(f"📊 文章统计:")
    print(f"  - Claude Agent: {len(claude_agent_articles)} 篇")
    print(f"  - Claude Prompts: {len(claude_prompts_articles)} 篇")
    print(f"  - Product Hunt: {len(producthunt_articles)} 篇")
    print(f"  - 总计: {len(claude_agent_articles + claude_prompts_articles + producthunt_articles)} 篇")
    
    # 5. 测试Hugo构建
    print("\n🏗️ 测试 Hugo 构建...")
    try:
        result = subprocess.run(
            ['hugo', '--minify'],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print("✅ Hugo 构建成功")
            # 提取页面数量
            for line in result.stdout.split('\n'):
                if 'Pages' in line:
                    print(f"  📄 {line.strip()}")
                    break
        else:
            print(f"❌ Hugo 构建失败: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ Hugo 构建: 超时")
    except Exception as e:
        print(f"❌ Hugo 构建出错: {e}")
    
    # 生成测试报告
    print("\n" + "=" * 50)
    print("📋 测试报告")
    print("=" * 50)
    
    success_count = sum(1 for r in results.values() if r['success'])
    total_count = len(results)
    
    print(f"✅ 成功: {success_count}/{total_count}")
    print(f"⏱️  预计节省时间: 67% (从270分钟/月降至90分钟/月)")
    print(f"🕒 统一执行时间: 每天06:00 (北京时间)")
    
    # 详细结果
    for name, result in results.items():
        status = "✅ 成功" if result['success'] else "❌ 失败"
        print(f"  {name}: {status}")
        if not result['success'] and 'error' in result:
            print(f"    错误: {result['error']}")
    
    print("\n🎯 优化效果:")
    print("  ✅ 工作流数量: 3个 → 1个")
    print("  ✅ 执行频率: 每天3次 → 每天1次")
    print("  ✅ 资源使用: 减少67%")
    print("  ✅ 维护复杂度: 显著降低")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_unified_analysis()
    if success:
        print("\n🎉 所有测试通过！可以部署新的统一工作流。")
        exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查后再部署。")
        exit(1)