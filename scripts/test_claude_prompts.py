#!/usr/bin/env python3
"""
测试Claude Prompts分析器的文章生成功能
"""

import datetime
import json
import os

def test_article_generation():
    """测试文章生成功能"""
    
    # 模拟项目数据
    mock_projects = [
        {
            'name': 'awesome-claude-prompts',
            'full_name': 'user/awesome-claude-prompts',
            'description': '精选的Claude提示词集合，包含多个实用场景',
            'url': 'https://github.com/user/awesome-claude-prompts',
            'stars': 250,
            'forks': 45,
            'language': 'Python',
            'topics': ['claude', 'prompts', 'ai', 'llm'],
            'created_at': '2025-09-01T00:00:00Z',
            'updated_at': '2025-09-08T00:00:00Z',
            'readme_content': '这是一个精选的Claude提示词集合，包含多个实用场景的示例代码和说明。',
            'recent_commits': [
                {'message': '添加新的提示词模板', 'date': '2025-09-08T10:00:00Z', 'author': 'John Doe'},
                {'message': '修复文档错误', 'date': '2025-09-07T15:30:00Z', 'author': 'Jane Smith'}
            ],
            'analysis': {
                'overall_score': 85,
                'strengths': ['高人气项目 (250 stars)', '详细的README文档', '项目活跃，最近有更新'],
                'weaknesses': [],
                'recommendations': ['优秀的Claude Code项目，推荐学习']
            }
        },
        {
            'name': 'claude-code-examples',
            'full_name': 'dev/claude-code-examples',
            'description': 'Claude Code编程实例和最佳实践指南',
            'url': 'https://github.com/dev/claude-code-examples',
            'stars': 180,
            'forks': 32,
            'language': 'JavaScript',
            'topics': ['claude', 'code-examples', 'tutorial'],
            'created_at': '2025-08-25T00:00:00Z',
            'updated_at': '2025-09-07T00:00:00Z',
            'readme_content': 'Claude Code的编程实例和最佳实践，包含多个实际项目的代码示例。',
            'recent_commits': [
                {'message': '新增React集成示例', 'date': '2025-09-07T14:20:00Z', 'author': 'Mike Johnson'}
            ],
            'analysis': {
                'overall_score': 78,
                'strengths': ['中等人气 (180 stars)', '项目标签完整', '项目描述详细'],
                'weaknesses': ['README文档不够详细'],
                'recommendations': ['不错的项目，有一定学习价值']
            }
        }
    ]
    
    # 生成文章
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    title = f"GitHub热门项目评测：Claude Code提示词项目深度分析 - {date_str}"
    filename = f"github-claude-prompts-review-{date_str}.md"
    filepath = f"content/posts/{filename}"
    
    # 计算平均数据
    avg_stars = sum(p['stars'] for p in mock_projects) / len(mock_projects)
    avg_forks = sum(p['forks'] for p in mock_projects) / len(mock_projects)
    
    # 构建Hugo格式的文章内容
    content = f"""+++
date = "{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')}"
draft = false
title = "GitHub热门项目评测：Claude Code提示词项目深度分析 - {date_str}"
description = "每日精选GitHub上最热门的Claude Code prompts项目，深度分析其特点、优势和应用场景。GitHub {int(avg_stars)} stars，提示词工程领域热门开源项目深度评测。"
summary = "今日精选{len(mock_projects)}个Claude Code提示词项目，平均{int(avg_stars)}个星标，涵盖prompt工程、开发工具、教程资源等多个方面。"
tags = ["GitHub", "开源项目", "Claude Code", "提示词工程", "项目评测"]
categories = ["GitHub热门"]
keywords = ["Claude Code提示词", "GitHub AI项目", "prompt engineering", "开源项目", "AI助手"]
author = "ERIC"
ShowToc = true
TocOpen = false
ShowReadingTime = true
ShowBreadCrumbs = true
ShowPostNavLinks = true
ShowWordCount = true
ShowShareButtons = true

[cover]
image = ""
alt = "Claude Code提示词项目评测"
caption = "GitHub热门AI项目深度分析"
relative = false
hidden = false
+++

## 📊 今日Claude Code热门项目概览

今天为大家精选了 {len(mock_projects)} 个在GitHub上表现突出的Claude Code相关项目。这些项目涵盖了prompt工程、开发工具、教程资源等多个方面，为Claude Code的学习和应用提供了宝贵的参考。

**📈 今日数据统计**:
- **平均Star数**: {int(avg_stars)}
- **平均Fork数**: {int(avg_forks)}
- **主要领域**: 提示词工程、AI助手、开发工具

"""
    
    for i, project in enumerate(mock_projects, 1):
        analysis = project.get('analysis', {})
        
        content += f"""
## {i}. {project['name']}

**⭐ GitHub Stars:** {project['stars']} | **🍴 Forks:** {project['forks']} | **📅 创建时间:** {project['created_at'][:10]}

**🔗 项目链接:** [{project['full_name']}]({project['url']})

### 项目简介

{project.get('description', '暂无描述')}

### 技术特点

**主要语言:** {project.get('language', 'N/A')}

**项目标签:** {', '.join(project.get('topics', [])) if project.get('topics') else '无'}

### 质量评估

**综合评分:** {analysis.get('overall_score', 0)}/100

#### 项目优势
{chr(10).join(f"- {strength}" for strength in analysis.get('strengths', []))}

#### 需要改进
{chr(10).join(f"- {weakness}" for weakness in analysis.get('weaknesses', []))}

#### 推荐建议
{chr(10).join(f"- {rec}" for rec in analysis.get('recommendations', []))}

### README摘要

```
{project.get('readme_content', '无README内容')[:300]}...
```

### 最近更新

"""
        
        if project.get('recent_commits'):
            for commit in project['recent_commits'][:3]:
                content += f"- **{commit['date'][:10]}** by {commit['author']}: {commit['message']}\n"
        else:
            content += "- 暂无最近更新信息\n"
        
        content += "\n---\n"
    
    content += f"""

## 📈 趋势分析

本期共分析了 {len(mock_projects)} 个Claude Code相关项目：

- **平均Star数:** {int(avg_stars)}
- **平均Fork数:** {int(avg_forks)}
- **主要编程语言:** {', '.join(set(p.get('language', 'N/A') for p in mock_projects if p.get('language')))}

## 🎯 学习建议

1. **初学者:** 建议从文档完善、Star数较高的项目开始学习
2. **进阶用户:** 可以关注最新的prompt engineering技术和工具
3. **开发者:** 考虑为优秀项目贡献代码或提出改进建议

## 🔔 关注更新

我们每天都会搜索和分析GitHub上最新的Claude Code项目，为大家提供最及时的技术动态。记得关注我们的更新！

---

## 📞 关于作者

**ERIC** - AI技术专家，专注于人工智能和自动化工具的研究与应用

### 🔗 联系方式与平台

- **📧 邮箱**: [gyc567@gmail.com](mailto:gyc567@gmail.com)
- **🐦 Twitter**: [@EricBlock2100](https://twitter.com/EricBlock2100)
- **💬 微信**: 360369487
- **📱 Telegram**: [https://t.me/fatoshi_block](https://t.me/fatoshi_block)
- **📢 Telegram频道**: [https://t.me/cryptochanneleric](https://t.me/cryptochanneleric)

### 🌐 相关平台

- **🌐 个人技术博客**: [https://www.topdigg.com/](https://www.topdigg.com/)

*欢迎关注我的各个平台，获取最新的AI技术分析和工具评测！*

---

*本文由自动化分析系统生成，数据来源于GitHub API，更新时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # 确保目录存在
    os.makedirs('content/posts', exist_ok=True)
    
    # 写入文件
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 成功生成测试文章: {filename}")
        return True
    except Exception as e:
        print(f"❌ 生成文章失败: {e}")
        return False

if __name__ == "__main__":
    test_article_generation()