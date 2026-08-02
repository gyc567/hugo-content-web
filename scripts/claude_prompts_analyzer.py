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
from project_deduplicator import ProjectDeduplicator


class ClaudePromptsAnalyzer:
    def __init__(self, github_token: str = None):
        self.github_token = github_token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Claude-Prompts-Analyzer/1.0'
        }
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'

        self.history_file = 'data/claude_prompts_projects.json'
        self.ensure_data_directory()
        self.deduplicator = ProjectDeduplicator(self.history_file)

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
        os.makedirs('data', exist_ok=True)
        os.makedirs('content/posts', exist_ok=True)

    def _search_github(self, query: str, per_page: int = 20) -> List[Dict]:
        """执行单次GitHub搜索"""
        url = "https://api.github.com/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': per_page
        }
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 403:
                print("⚠️  GitHub API速率限制，等待重试...")
                time.sleep(60)
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get('items', [])
        except Exception as e:
            print(f"❌ 搜索失败 ({query}): {e}")
            return []

    def search_github_repositories(self, keyword: str, days_back: int = 30) -> List[Dict]:
        """双轨搜索：新项目 + 活跃成熟项目"""
        date_filter = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime('%Y-%m-%d')

        # 轨道A: 最近创建的新项目
        query_new = f"{keyword} created:>{date_filter} stars:>5"
        print(f"🔍 搜索新项目: {keyword}")
        raw_new = self._search_github(query_new, per_page=15)

        time.sleep(1)

        # 轨道B: 持续活跃的成熟项目
        query_active = f"{keyword} pushed:>{date_filter} stars:>50"
        print(f"🔍 搜索活跃项目: {keyword}")
        raw_active = self._search_github(query_active, per_page=10)

        # 合并去重（按 id）
        seen_ids = set()
        repositories = []
        for repo in raw_new + raw_active:
            if repo['id'] in seen_ids:
                continue
            seen_ids.add(repo['id'])
            if self._is_relevant_repository(repo):
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

    def _is_relevant_repository(self, repo: Dict) -> bool:
        """判断仓库是否与Claude Code/Prompts相关"""
        name = repo.get('name', '').lower()
        description = repo.get('description', '').lower()
        topics = [t.lower() for t in repo.get('topics', [])]
        text = f"{name} {description} {' '.join(topics)}"

        has_claude = any(kw in text for kw in ['claude', 'anthropic'])
        has_prompt = any(kw in text for kw in [
            'prompt', 'system-prompt', 'prompt-engineering',
            'claude-code', 'cursor', 'copilot', 'llm-agent',
            'ai-agent', 'chatbot', 'assistant'
        ])

        return has_claude or has_prompt

    def _is_quality_project(self, repo: Dict) -> bool:
        """项目质量门槛"""
        if repo['stars'] < 5:
            return False
        if not repo.get('description'):
            return False
        try:
            updated = datetime.datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
            if (datetime.datetime.now() - updated).days > 730:
                return False
        except (ValueError, KeyError):
            pass
        return True

    def get_repository_details(self, repo: Dict) -> Dict:
        """获取仓库详细信息"""
        try:
            readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"
            readme_response = requests.get(readme_url, headers=self.headers, timeout=15)
            readme_content = ""
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                if readme_data.get('content'):
                    import base64
                    readme_content = base64.b64decode(readme_data['content']).decode('utf-8', errors='ignore')
                    readme_content = readme_content[:2000]

            commits_url = f"https://api.github.com/repos/{repo['full_name']}/commits"
            commits_response = requests.get(commits_url, headers=self.headers, params={'per_page': 5}, timeout=15)
            recent_commits = []
            if commits_response.status_code == 200:
                for commit in commits_response.json():
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
        analysis = {
            'overall_score': 0,
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }

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

        readme = repo.get('readme_content', '')
        if len(readme) > 500:
            score += 15
            analysis['strengths'].append("详细的README文档")
        elif len(readme) > 200:
            score += 10
        else:
            analysis['weaknesses'].append("README文档不够详细")
            analysis['recommendations'].append("建议完善项目文档")

        if repo.get('recent_commits'):
            commit_date = datetime.datetime.strptime(
                repo['recent_commits'][0]['date'], '%Y-%m-%dT%H:%M:%SZ'
            )
            days_since = (datetime.datetime.now() - commit_date).days
            if days_since < 30:
                score += 20
                analysis['strengths'].append("项目活跃，最近有更新")
            elif days_since < 90:
                score += 10
            else:
                analysis['weaknesses'].append("项目更新不够频繁")

        if repo.get('topics') and len(repo['topics']) > 2:
            score += 10
            analysis['strengths'].append("项目标签完整")

        if repo.get('description') and len(repo['description']) > 50:
            score += 10
            analysis['strengths'].append("项目描述详细")

        if repo['forks'] > repo['stars'] * 0.1:
            score += 15
            analysis['strengths'].append("项目有较好的参与度")

        analysis['overall_score'] = min(score, 100)

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
        filename = f"github-claude-prompts-review-{date_str}.md"
        filepath = f"content/posts/{filename}"

        avg_stars = sum(p['stars'] for p in projects) / len(projects)
        avg_forks = sum(p['forks'] for p in projects) / len(projects)

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
{chr(10).join(f"- {s}" for s in analysis.get('strengths', []))}

#### 需要改进
{chr(10).join(f"- {w}" for w in analysis.get('weaknesses', []))}

#### 推荐建议
{chr(10).join(f"- {r}" for r in analysis.get('recommendations', []))}

### README摘要

```
{project.get('readme_content', '无README内容')[:300]}...
```

### 最近更新

"""
            if project.get('recent_commits'):
                for c in project['recent_commits'][:3]:
                    content += f"- **{c['date'][:10]}** by {c['author']}: {c['message']}\n"
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

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 成功生成文章: {filename}")
            return True
        except Exception as e:
            print(f"❌ 生成文章失败: {e}")
            return False

    def run_analysis(self, days_back: int = 30, max_projects: int = 3) -> bool:
        """运行完整的分析流程"""
        print("🚀 开始Claude Code项目分析...")

        stats = self.deduplicator.get_project_statistics()
        print(f"📚 已分析项目数量: {stats['total_projects']}")

        all_projects = []
        MAX_PER_KEYWORD = 10

        for keyword in self.search_keywords:
            repositories = self.search_github_repositories(keyword, days_back)
            # 按 stars 排序，每关键词最多取 top N
            repositories.sort(key=lambda x: x['stars'], reverse=True)
            repositories = repositories[:MAX_PER_KEYWORD]

            for repo in repositories:
                if self.deduplicator.is_duplicate_project(repo):
                    continue
                if not self._is_quality_project(repo):
                    continue

                detailed = self.get_repository_details(repo)
                detailed['analysis'] = self.analyze_project_quality(detailed)
                # 计算新鲜度分数
                detailed['freshness_score'] = self.calculate_freshness_score(detailed)
                all_projects.append(detailed)
                # 立即标记为已分析，防止文章生成失败时丢失去重状态
                self.deduplicator.add_analyzed_project(repo)

            time.sleep(2)

        if all_projects:
            # 获取最近文章中已包含的项目（用于多样性采样）
            recent_project_names = self.get_recent_article_projects(days=3)
            
            # 计算综合分数（质量分数 + 新鲜度权重 + 多样性调整）
            for project in all_projects:
                project['final_score'] = self.calculate_final_score(
                    project, 
                    recent_project_names
                )
            
            # 按综合分数排序
            all_projects.sort(key=lambda x: x['final_score'], reverse=True)
            top_projects = all_projects[:max_projects]
            
            print(f"📊 项目选择详情:")
            for i, p in enumerate(top_projects, 1):
                freshness_label = "🆕新项目" if p['freshness_score'] > 1.2 else "⭐成熟项目"
                print(f"  {i}. {p['name']} (stars:{p['stars']}, fresh:{p['freshness_score']:.2f}, final:{p['final_score']:.2f}) [{freshness_label}]")
            
            success = self.generate_article(top_projects)
            if success:
                print(f"🎉 分析完成！共分析 {len(top_projects)} 个项目")
                return True

        print("📝 今日无新项目需要分析")
        return False

    def calculate_freshness_score(self, project: Dict) -> float:
        """
        计算项目新鲜度分数
        新项目（7天内创建）×1.5
        近期活跃（30天内有更新）×1.2
        超过1年未更新×0.8
        """
        score = 1.0
        
        try:
            created = datetime.datetime.strptime(project['created_at'][:10], '%Y-%m-%d')
            days_since_creation = (datetime.datetime.now() - created).days
            
            if days_since_creation <= 7:
                score *= 1.5
            elif days_since_creation <= 30:
                score *= 1.2
            elif days_since_creation > 365:
                score *= 0.8
        except (ValueError, KeyError):
            pass
        
        try:
            updated = datetime.datetime.strptime(project['updated_at'][:10], '%Y-%m-%d')
            days_since_update = (datetime.datetime.now() - updated).days
            
            if days_since_update <= 7:
                score *= 1.3
            elif days_since_update <= 30:
                score *= 1.1
            elif days_since_update > 180:
                score *= 0.9
        except (ValueError, KeyError):
            pass
        
        return score

    def get_recent_article_projects(self, days: int = 3) -> Set[str]:
        """
        获取最近N天内生成的文章中包含的项目名
        用于多样性采样，避免同一批项目反复出现
        """
        recent_projects = set()
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        posts_dir = 'content/posts'
        if not os.path.exists(posts_dir):
            return recent_projects
        
        for filename in os.listdir(posts_dir):
            if not filename.endswith('.md'):
                continue
            
            # 从文件名判断日期
            # 格式: github-claude-prompts-review-YYYY-MM-DD.md
            match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
            if not match:
                continue
            
            try:
                file_date = datetime.datetime(
                    int(match.group(1)), 
                    int(match.group(2)), 
                    int(match.group(3))
                )
                if file_date >= cutoff_date:
                    filepath = os.path.join(posts_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 提取文章中的项目名（格式: ## N. project-name 或 **🔗 项目链接:** [owner/repo]）
                        # 匹配 ## N. project-name 格式
                        project_pattern = re.findall(r'## \d+\. ([^\n]+)', content)
                        for name in project_pattern:
                            # 清理标题标记
                            name = re.sub(r'\[.*?\]', '', name).strip()
                            if name:
                                recent_projects.add(name.lower())
                        
                        # 也提取URL中的项目名
                        url_pattern = re.findall(r'github\.com/([^/]+/[^/\)]+)', content)
                        for full_name in url_pattern:
                            project_name = full_name.split('/')[-1]
                            recent_projects.add(project_name.lower())
            except (ValueError, IOError):
                continue
        
        return recent_projects

    def calculate_final_score(self, project: Dict, recent_projects: Set[str]) -> float:
        """
        计算项目的最终综合分数
        = 质量分数 × 新鲜度权重 × 多样性调整
        """
        quality_score = project['analysis']['overall_score']
        freshness_score = project['freshness_score']
        
        # 多样性惩罚：最近3天出现过的项目，分数降低
        project_name_lower = project['name'].lower()
        is_in_recent = any(
            project_name_lower in recent_name or recent_name in project_name_lower
            for recent_name in recent_projects
        )
        
        diversity_multiplier = 0.5 if is_in_recent else 1.0
        
        final_score = quality_score * freshness_score * diversity_multiplier
        
        return final_score


def main():
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("⚠️  未设置GITHUB_TOKEN环境变量")

    days_back = int(os.getenv('DAYS_BACK', 30))
    max_projects = int(os.getenv('MAX_PROJECTS', 3))

    analyzer = ClaudePromptsAnalyzer(github_token)
    success = analyzer.run_analysis(days_back, max_projects)

    if not success:
        print("❌ 分析过程中出现问题")
        exit(1)

    print("✅ Claude Code项目分析完成")


if __name__ == "__main__":
    main()
