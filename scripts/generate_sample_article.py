#!/usr/bin/env python3
"""
生成Product Hunt测试文章的脚本
用于验收功能演示
"""

import datetime
from producthunt_analyzer import ProductHuntAnalyzer

def generate_sample_article():
    """生成示例文章用于验收"""
    print("🎯 生成Product Hunt测试文章用于验收...")
    
    # 创建示例产品数据
    sample_products = [
        {
            'name': 'AI Code Reviewer Pro',
            'votes': 1247,
            'description': 'AI-powered code review tool that helps developers write better, cleaner code',
            'detailed_description': 'AI Code Reviewer Pro is a revolutionary development tool that uses advanced machine learning algorithms to analyze your code in real-time. It identifies potential bugs, suggests optimizations, and ensures your code follows best practices. With support for 20+ programming languages and seamless IDE integration, it\'s the ultimate coding companion for modern developers.',
            'url': 'https://www.producthunt.com/posts/ai-code-reviewer-pro',
            'tags': ['AI', 'Developer Tools', 'Code Review', 'Productivity', 'Machine Learning'],
            'analysis': {
                'overall_score': 92,
                'strengths': [
                    '高人气产品 (1247 votes)',
                    '产品描述详细',
                    '产品标签丰富',
                    '产品名称简洁明了',
                    '产品链接完整'
                ],
                'weaknesses': [],
                'recommendations': ['优秀的Product Hunt产品，值得关注']
            }
        },
        {
            'name': 'Smart Meeting Assistant',
            'votes': 823,
            'description': 'Transform your meetings with AI-powered transcription and smart insights',
            'detailed_description': 'Smart Meeting Assistant revolutionizes how teams conduct and follow up on meetings. Using advanced natural language processing, it automatically transcripts conversations, extracts key action items, and generates comprehensive meeting summaries. The tool integrates with popular video conferencing platforms and provides real-time collaboration features.',
            'url': 'https://www.producthunt.com/posts/smart-meeting-assistant',
            'tags': ['Productivity', 'AI', 'Meeting', 'Collaboration', 'SaaS'],
            'analysis': {
                'overall_score': 85,
                'strengths': [
                    '高人气产品 (823 votes)',
                    '产品描述详细',
                    '产品标签丰富',
                    '产品名称简洁明了',
                    '产品链接完整'
                ],
                'weaknesses': [],
                'recommendations': ['优秀的Product Hunt产品，值得关注']
            }
        },
        {
            'name': 'DesignSync Studio',
            'votes': 654,
            'description': 'Collaborative design platform for remote teams',
            'detailed_description': 'DesignSync Studio is a comprehensive design collaboration platform that enables remote teams to work together seamlessly. It features real-time editing, version control, design system management, and advanced commenting tools. The platform supports multiple file formats and integrates with popular design tools like Figma, Sketch, and Adobe Creative Suite.',
            'url': 'https://www.producthunt.com/posts/designsync-studio',
            'tags': ['Design', 'Collaboration', 'Remote Work', 'Creative Tools', 'Team Management'],
            'analysis': {
                'overall_score': 78,
                'strengths': [
                    '高人气产品 (654 votes)',
                    '产品描述详细',
                    '产品标签丰富',
                    '产品名称简洁明了',
                    '产品链接完整'
                ],
                'weaknesses': [],
                'recommendations': ['不错的产品，具有一定市场潜力']
            }
        }
    ]
    
    # 创建分析器实例并生成文章
    analyzer = ProductHuntAnalyzer()
    success = analyzer.generate_article(sample_products)
    
    if success:
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        filename = f"producthunt-top3-review-{date_str}.md"
        filepath = f"content/posts/{filename}"
        
        print(f"✅ 成功生成测试文章: {filepath}")
        
        # 显示文章摘要
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            print(f"\n📄 文章信息:")
            print(f"   文件路径: {filepath}")
            print(f"   文章长度: {len(content)} 字符")
            print(f"   总行数: {len(lines)} 行")
            
            print(f"\n📝 文章预览 (前20行):")
            print("=" * 60)
            for i, line in enumerate(lines[:20], 1):
                print(f"{i:2d}│ {line}")
            if len(lines) > 20:
                print("   │ ...")
                print(f"   │ (还有 {len(lines) - 20} 行)")
            print("=" * 60)
        
        # 保存示例数据到历史记录
        analyzer.save_analyzed_products({
            f'AI Code Reviewer Pro-{date_str}',
            f'Smart Meeting Assistant-{date_str}',
            f'DesignSync Studio-{date_str}'
        })
        
        return True
    else:
        print("❌ 生成测试文章失败")
        return False

if __name__ == "__main__":
    generate_sample_article()