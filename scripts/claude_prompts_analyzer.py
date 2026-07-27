#!/usr/bin/env python3
"""
Claude Code Prompts项目自动分析和评测生成器
每日抓取GitHub上最热门的Claude Code Prompts项目和教程，生成专业评测文章
"""

import requests
import json
import os
import datetime
from typing import List, Dict, Any, Set
import time
import re
import hashlib

class ClaudePromptsAnalyzer:
    def __init__(self, github_token: str = None):
        self.github_token = github_token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Claude-Prompts-Analyzer/1.0'
        }
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'
        
        # 项目历史记录文件路径
        self.history_file = 'data/claude_prompts_projects.json'
        self.ensure_data_directory()
        
        # Claude Code相关的搜索关键词
        self.search_keywords = [
            'claude code',
            'claude prompts',
            'anthropic claude',
            'claude tutorial',
            'claude prompt engineering',
            'claude code examples',
            'claude ai prompts',
            'claude development'
        ]
    
    def ensure_data_directory(self):
        """确保data目录存在"""
        os.makedirs('data', exist_ok=True)
        os.makedirs('content/posts', exist_ok=True)
    
    def load_analyzed_projects(self) -> Set[str]:
        """加载已分析的项目历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('analyzed_projects', []))
            return set()
        except Exception as e:
            print(f"⚠️  加载项目历史记录失败: {e}")
            return set()
    
    def save_analyzed_projects(self, analyzed_projects: Set[str]):
        """保存已分析的项目历史记录"""
        try:
            data = {
                'last_updated': datetime.datetime.now().isoformat(),
                'analyzed_projects': list(analyzed_projects),
                'total_projects': len(analyzed_projects)
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  保存项目历史记录失败: {e}")
    
    def search_github_repositories(self, keyword: str, days_back: int = 7, per_page: int = 30) -> List[Dict]:
        """搜索GitHub仓库"""
        # 构建搜索查询 - 移除语言限制以获得更多结果
        query = f"{keyword} stars:>1"
        
        url = "https://api.github.com/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': per_page
        }
        
        try:
            print(f"🔍 搜索关键词: {keyword}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 403:
                print("⚠️  GitHub API速率限制，等待重试...")
                time.sleep(60)
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            response.raise_for_status()
            data = response.json()
            
            repositories = []
            for repo in data.get('items', []):
                # 过滤掉一些不相关的仓库
                if self._is_relevant_repository(repo, keyword):
                    repositories.append({
                        'id': repo['id'],
                        'name': repo['name'],
                        'full_name': repo['full_name'],
                        'description': repo.get('description', ''),
                        'url': repo['html_url'],
                        'stars': repo['stargazers_count'],
                        'forks': repo['forks_count'],
                        'language': repo.get('language', ''),
                        'topics': repo.get('topics', []),
                        'created_at': repo['created_at'],
                        'updated_at': repo['updated_at'],
                        'keyword': keyword
                    })
            
            print(f"✅ 找到 {len(repositories)} 个相关仓库")
            return repositories
            
        except Exception as e:
            print(f"❌ 搜索GitHub仓库失败 ({keyword}): {e}")
            return []
    
    def _is_relevant_repository(self, repo: Dict, keyword: str) -> bool:
        """判断仓库是否与Claude Code相关"""
        name = repo.get('name', '').lower()
        description = repo.get('description', '').lower()
        topics = [topic.lower() for topic in repo.get('topics', [])]
        
        # Claude相关关键词
        claude_keywords = ['claude', 'anthropic', 'ai', 'prompt', 'assistant', 'chatbot', 'llm']
        
        # 检查名称、描述和主题中是否包含相关关键词
        text_to_check = f"{name} {description} {' '.join(topics)}"
        
        return any(keyword in text_to_check for keyword in claude_keywords)
    
    def get_repository_details(self, repo: Dict) -> Dict:
        """获取仓库详细信息"""
        try:
            # 获取README内容
            readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"
            readme_response = requests.get(readme_url, headers=self.headers, timeout=15)
            
            readme_content = ""
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                if readme_data.get('content'):
                    import base64
                    readme_content = base64.b64decode(readme_data['content']).decode('utf-8', errors='ignore')
                    # 限制README长度
                    readme_content = readme_content[:2000]
            
            # 获取最新的commits
            commits_url = f"https://api.github.com/repos/{repo['full_name']}/commits"
            commits_response = requests.get(commits_url, headers=self.headers, params={'per_page': 5}, timeout=15)
            
            recent_commits = []
            if commits_response.status_code == 200:
                commits_data = commits_response.json()
                for commit in commits_data:
                    recent_commits.append({
                        'message': commit['commit']['message'][:100],
                        'date': commit['commit']['author']['date'],
                        'author': commit['commit']['author']['name']
                    })
            
            repo['readme_content'] = readme_content
            repo['recent_commits'] = recent_commits
            
            return repo
            
        except Exception as e:
            print(f"⚠️  获取仓库详情失败 {repo['full_name']}: {e}")
            repo['readme_content'] = ""
            repo['recent_commits'] = []
            return repo
    
    def analyze_project_quality(self, repo: Dict) -> Dict:
        """分析项目质量"""
        score = 0
        max_score = 100
        analysis = {
            'overall_score': 0,
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # 评分标准
        if repo['stars'] > 100:
            score += 20
            analysis['strengths'].append(f"高人气项目 ({repo['stars']} stars)")
        elif repo['stars'] > 50:
            score += 15
            analysis['strengths'].append(f"中等人气 ({repo['stars']} stars)")
        elif repo['stars'] > 10:
            score += 10
        else:
            analysis['weaknesses'].append("Star数量较少，可能是新项目")
        
        # README质量
        readme = repo.get('readme_content', '')
        if len(readme) > 500:
            score += 15
            analysis['strengths'].append("详细的README文档")
        elif len(readme) > 200:
            score += 10
        else:
            analysis['weaknesses'].append("README文档不够详细")
            analysis['recommendations'].append("建议完善项目文档")
        
        # 最近活跃度
        if repo.get('recent_commits'):
            recent_commit = repo['recent_commits'][0]
            commit_date = datetime.datetime.strptime(recent_commit['date'], '%Y-%m-%dT%H:%M:%SZ')
            days_since_commit = (datetime.datetime.now() - commit_date).days
            
            if days_since_commit < 30:
                score += 20
                analysis['strengths'].append("项目活跃，最近有更新")
            elif days_since_commit < 90:
                score += 10
            else:
                analysis['weaknesses'].append("项目更新不够频繁")
        
        # Topics和描述质量
        if repo.get('topics') and len(repo['topics']) > 2:
            score += 10
            analysis['strengths'].append("项目标签完整")
        
        if repo.get('description') and len(repo['description']) > 50:
            score += 10
            analysis['strengths'].append("项目描述详细")
        
        # Fork比例
        if repo['forks'] > repo['stars'] * 0.1:
            score += 15
            analysis['strengths'].append("项目有较好的参与度")
        
        analysis['overall_score'] = min(score, max_score)
        
        # 生成推荐
        if analysis['overall_score'] > 80:
            analysis['recommendations'].append("优秀的Claude Code项目，推荐学习")
        elif analysis['overall_score'] > 60:
            analysis['recommendations'].append("不错的项目，有一定学习价值")
        else:
            analysis['recommendations'].append("项目有待完善，可关注后续发展")
        
        return analysis
    
    def generate_article(self, projects: List[Dict]) -> bool:
        """生成评测文章"""
        if not projects:
            print("📝 没有找到符合条件的项目，跳过文章生成")
            return False
        
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        title = f"GitHub热门项目评测：Claude Code提示词项目深度分析 - {date_str}"
        filename = f"github-claude-prompts-review-{date_str}.md"
        filepath = f"content/posts/{filename}"
        
        # 计算平均数据
        avg_stars = sum(p['stars'] for p in projects) / len(projects)
        avg_forks = sum(p['forks'] for p in projects) / len(projects)
        
        # 构建Hugo格式的文章内容
        content = f"""+++
date = "{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')}"
draft = false
title = "GitHub热门项目评测：Claude Code提示词项目深度分析 - {date_str}"
description = "每日精选GitHub上最热门的Claude Code prompts项目，深度分析其特点、优势和应用场景。GitHub {int(avg_stars)} stars，提示词工程领域热门开源项目深度评测。"
summary = "今日精选{len(projects)}个Claude Code提示词项目，平均{int(avg_stars)}个星标，涵盖prompt工程、开发工具、教程资源等多个方面。"
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

今天为大家精选了 {len(projects)} 个在GitHub上表现突出的Claude Code相关项目。这些项目涵盖了prompt工程、开发工具、教程资源等多个方面，为Claude Code的学习和应用提供了宝贵的参考。

**📈 今日数据统计**:
- **平均Star数**: {int(avg_stars)}
- **平均Fork数**: {int(avg_forks)}
- **主要领域**: 提示词工程、AI助手、开发工具

"""
        
        for i, project in enumerate(projects, 1):
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

本期共分析了 {len(projects)} 个Claude Code相关项目：

- **平均Star数:** {int(avg_stars)}
- **平均Fork数:** {int(avg_forks)}
- **主要编程语言:** {', '.join(set(p.get('language', 'N/A') for p in projects if p.get('language')))}

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
        
        # 写入文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 成功生成文章: {filename}")
            return True
        except Exception as e:
            print(f"❌ 生成文章失败: {e}")
            return False
    
    def run_analysis(self, days_back: int = 7, max_projects: int = 3) -> bool:
        """运行完整的分析流程"""
        print("🚀 开始Claude Code项目分析...")
        
        # 加载历史记录
        analyzed_projects = self.load_analyzed_projects()
        print(f"📚 已分析项目数量: {len(analyzed_projects)}")
        
        all_projects = []
        
        # 搜索所有关键词
        for keyword in self.search_keywords:
            repositories = self.search_github_repositories(keyword, days_back)
            for repo in repositories:
                # 避免重复分析
                project_id = f"{repo['full_name']}-{repo['updated_at']}"
                if project_id not in analyzed_projects:
                    # 获取详细信息
                    detailed_repo = self.get_repository_details(repo)
                    # 进行质量分析
                    detailed_repo['analysis'] = self.analyze_project_quality(detailed_repo)
                    all_projects.append(detailed_repo)
                    analyzed_projects.add(project_id)
            
            # API限制，添加延迟
            time.sleep(2)
        
        # 按综合评分排序，选择top项目
        if all_projects:
            all_projects.sort(key=lambda x: x['analysis']['overall_score'], reverse=True)
            top_projects = all_projects[:max_projects]
            
            # 生成文章
            success = self.generate_article(top_projects)
            
            if success:
                # 保存历史记录
                self.save_analyzed_projects(analyzed_projects)
                print(f"🎉 分析完成！共分析 {len(top_projects)} 个项目")
                return True
        
        print("📝 今日无新项目需要分析")
        return False

def main():
    """主函数"""
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("⚠️  未设置GITHUB_TOKEN环境变量")
    
    days_back = int(os.getenv('DAYS_BACK', 7))
    max_projects = int(os.getenv('MAX_PROJECTS', 3))
    
    analyzer = ClaudePromptsAnalyzer(github_token)
    success = analyzer.run_analysis(days_back, max_projects)
    
    if not success:
        print("❌ 分析过程中出现问题")
        exit(1)
    
    print("✅ Claude Code项目分析完成")

if __name__ == "__main__":
    main()