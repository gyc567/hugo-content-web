#!/usr/bin/env python3
"""
Product Hunt分析器集成测试脚本
用于验证实际功能是否正常工作
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import patch, Mock
from producthunt_analyzer import ProductHuntAnalyzer


def test_integration_with_mock():
    """使用Mock数据进行集成测试"""
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    
    try:
        os.chdir(test_dir)
        
        print("🧪 开始Product Hunt分析器集成测试...")
        
        # Mock HTML响应
        mock_html = '''
        <html>
            <div class="styles_item__abc123">
                <h3>AI Code Assistant</h3>
                <a href="/posts/ai-code-assistant">Link</a>
                <span>Revolutionary AI-powered coding assistant that helps developers write better code faster</span>
                <span>1234</span>
            </div>
            <div class="styles_item__def456">
                <h3>Smart Productivity Tool</h3>
                <a href="/posts/smart-productivity-tool">Link</a>
                <span>Boost your productivity with this innovative task management solution</span>
                <span>856</span>
            </div>
            <div class="styles_item__ghi789">
                <h3>Design System Builder</h3>
                <a href="/posts/design-system-builder">Link</a>
                <span>Create consistent design systems for your entire organization</span>
                <span>623</span>
            </div>
        </html>
        '''
        
        # Mock详情页HTML
        mock_detail_html = '''
        <html>
            <p>This is a comprehensive product description that provides detailed information about the features and benefits of this amazing tool that helps users achieve their goals</p>
            <span class="tag">AI</span>
            <span class="tag">Productivity</span>
            <span class="tag">SaaS</span>
            <a href="/topics/developer-tools">Developer Tools</a>
        </html>
        '''
        
        def mock_response_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            
            if 'producthunt.com/posts/' in url:
                mock_response.content = mock_detail_html.encode('utf-8')
            else:
                mock_response.content = mock_html.encode('utf-8')
            
            return mock_response
        
        with patch('requests.get', side_effect=mock_response_side_effect):
            analyzer = ProductHuntAnalyzer()
            success = analyzer.run_analysis()
            
            if success:
                print("✅ 集成测试成功！")
                
                # 检查生成的文件
                import datetime
                date_str = datetime.datetime.now().strftime('%Y-%m-%d')
                article_file = f"content/posts/producthunt-top3-review-{date_str}.md"
                data_file = "data/producthunt_products.json"
                
                if os.path.exists(article_file):
                    print(f"✅ 文章文件已生成: {article_file}")
                    with open(article_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"📄 文章长度: {len(content)} 字符")
                        
                        # 验证关键内容
                        assert "AI Code Assistant" in content, "文章应包含产品名称"
                        assert "1234" in content, "文章应包含投票数"
                        assert "Product Hunt今日TOP3" in content, "文章应包含标题"
                        print("✅ 文章内容验证通过")
                
                if os.path.exists(data_file):
                    print(f"✅ 数据文件已生成: {data_file}")
                    import json
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"📊 已分析产品数量: {data['total_products']}")
                        assert data['total_products'] > 0, "应该有分析的产品"
                        print("✅ 数据文件验证通过")
                
                print("\n🎉 所有集成测试通过！")
                return True
            else:
                print("❌ 集成测试失败：分析器返回失败")
                return False
        
    except Exception as e:
        print(f"❌ 集成测试异常: {e}")
        return False
        
    finally:
        os.chdir(original_cwd)
        shutil.rmtree(test_dir, ignore_errors=True)


def test_workflow_simulation():
    """模拟GitHub Actions工作流执行"""
    print("\n🎭 模拟GitHub Actions工作流执行...")
    
    # 设置环境变量
    env_vars = {
        'GITHUB_ACTIONS': 'true',
        'GITHUB_WORKSPACE': os.getcwd(),
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"🔧 设置环境变量: {key}={value}")
    
    # 检查必要文件
    required_files = [
        'scripts/producthunt_analyzer.py',
        '.github/workflows/daily-producthunt-analysis.yml',
        'content',
        'scripts/requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 所有必要文件存在")
    
    # 检查Python依赖
    try:
        import requests
        import json
        import datetime
        from bs4 import BeautifulSoup
        print("✅ Python依赖检查通过")
    except ImportError as e:
        print(f"❌ Python依赖缺失: {e}")
        return False
    
    print("✅ 工作流模拟验证通过")
    return True


def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 Product Hunt分析器集成测试套件")
    print("=" * 60)
    
    test_results = []
    
    # 测试1: 集成测试
    print("\n📋 测试1: 完整功能集成测试")
    result1 = test_integration_with_mock()
    test_results.append(("集成测试", result1))
    
    # 测试2: 工作流模拟
    print("\n📋 测试2: GitHub Actions工作流模拟")
    result2 = test_workflow_simulation()
    test_results.append(("工作流模拟", result2))
    
    # 总结报告
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"- {test_name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\n🎯 总体通过率: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 所有集成测试通过！Product Hunt分析器功能完整。")
        return True
    else:
        print("⚠️  部分测试未通过，请检查相关功能。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)