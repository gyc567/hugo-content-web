#!/usr/bin/env python3
"""
Claude Code Agent项目自动分析和评测生成器
每日抓取GitHub上最热门的Claude Code Agent项目，生成专业评测文章
"""

import requests
import json
import os
import datetime
from typing import List, Dict, Any, Set
import time
import re
import hashlib
from project_deduplicator import ProjectDeduplicator

class ClaudeAgentAnalyzer:
    def __init__(self, github_token: str = None):
        self.github_token = github_token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'SmartWallex-Analyzer/1.0'
        }
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'
        
        # 项目历史记录文件路径
        self.history_file = 'data/analyzed_projects.json'
        self.ensure_data_directory()
        
        # 初始化项目去重器
        self.deduplicator = ProjectDeduplicator(self.history_file)
    
    def ensure_data_directory(self):
        """确保data目录存在"""
        os.makedirs('data', exist_ok=True)
    

    
    def search_claude_agents(self, days_back: int = 7, max_projects: int = 3) -> List[Dict[str, Any]]:
        """搜索Claude Code Agent项目，使用去重器确保不重复已分析的项目"""
        
        # 显示已分析项目统计
        stats = self.deduplicator.get_project_statistics()
        print(f"📚 已分析项目数量: {stats['total_projects']}")
        
        # 多种搜索策略
        search_strategies = [
            self._search_by_claude_keywords,
            self._search_by_creation_date,
            self._search_by_recent_activity,
            self._search_by_trending
        ]
        
        all_projects = []
        
        for strategy in search_strategies:
            try:
                projects = strategy(days_back)
                all_projects.extend(projects)
                time.sleep(2)  # 避免API限制
            except Exception as e:
                print(f"⚠️  搜索策略执行失败: {e}")
                continue
        
        # 使用去重器进行去重和过滤
        unique_projects = {}
        new_projects = []
        
        for project in all_projects:
            repo_id = project['id']
            
            # 跳过重复项目ID
            if repo_id in unique_projects:
                continue
                
            # 使用去重器检查项目是否已分析
            if self.deduplicator.is_duplicate_project(project):
                print(f"⏭️  跳过已分析项目: {project['name']}")
                continue
            
            # 基本质量过滤
            if self._is_quality_project(project):
                unique_projects[repo_id] = project
                new_projects.append(project)
                print(f"✅ 新项目候选: {project['name']} ({project['stargazers_count']} ⭐)")
        
        # 按多个维度排序
        sorted_projects = sorted(
            new_projects,
            key=lambda x: (
                x['stargazers_count'],  # 星标数
                x['forks_count'],       # Fork数
                -self._days_since_created(x),  # 创建时间（越新越好）
                -self._days_since_updated(x)   # 更新时间（越新越好）
            ),
            reverse=True
        )
        
        print(f"🔍 找到 {len(sorted_projects)} 个新项目候选")
        
        return sorted_projects[:max_projects]
    
    def _search_by_claude_keywords(self, days_back: int) -> List[Dict[str, Any]]:
        """按Claude相关关键词搜索项目"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days_back)
        date_filter = start_date.strftime('%Y-%m-%d')
        
        claude_keywords = [
            'claude-code', 'claude-agent', 'claude-ai', 'anthropic-claude',
            'claude-api', 'claude-integration', 'claude-bot', 'claude-chatbot'
        ]
        
        projects = []
        for keyword in claude_keywords[:4]:
            projects.extend(self._search_github(f'{keyword} created:>{date_filter} stars:>2'))
        
        return projects
    
    def _search_by_creation_date(self, days_back: int) -> List[Dict[str, Any]]:
        """按创建日期搜索新项目"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days_back)
        date_filter = start_date.strftime('%Y-%m-%d')
        
        ai_keywords = [
            'ai-agent', 'llm-agent', 'chatbot', 'conversational-ai',
            'claude', 'anthropic', 'assistant', 'automation'
        ]
        
        projects = []
        for keyword in ai_keywords[:3]:
            projects.extend(self._search_github(f'{keyword} created:>{date_filter} stars:>3'))
        
        return projects
    
    def _search_by_recent_activity(self, days_back: int) -> List[Dict[str, Any]]:
        """按最近活动搜索项目"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days_back)
        date_filter = start_date.strftime('%Y-%m-%d')
        
        activity_keywords = ['claude', 'anthropic', 'ai-agent', 'llm', 'chatbot']
        
        projects = []
        for keyword in activity_keywords[:3]:
            projects.extend(self._search_github(f'{keyword} pushed:>{date_filter} stars:>3'))
        
        return projects
    
    def _search_by_trending(self, days_back: int) -> List[Dict[str, Any]]:
        """搜索趋势项目"""
        trending_keywords = ['claude-code', 'anthropic-api', 'ai-assistant', 'automation-agent', 'llm-tool']
        
        projects = []
        for keyword in trending_keywords[:3]:
            projects.extend(self._search_github(f'{keyword} stars:>2'))
        
        return projects
    
    def _search_github(self, query: str, per_page: int = 10) -> List[Dict[str, Any]]:
        """执行GitHub搜索"""
        try:
            search_url = 'https://api.github.com/search/repositories'
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': per_page
            }
            
            response = requests.get(search_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                print(f"⚠️  搜索失败: {query}, 状态码: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 搜索执行失败: {e}")
            return []
    
    def _is_quality_project(self, project: Dict[str, Any]) -> bool:
        """判断项目是否符合质量标准"""
        # 基本质量检查 - 降低门槛以适应AI agent项目
        if project['stargazers_count'] < 2:
            return False
        
        # 检查是否有描述
        if not project.get('description'):
            return False
        
        # 检查是否太老（超过1年）
        created_at = datetime.datetime.strptime(project['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        if (datetime.datetime.now() - created_at).days > 365:
            return False
        
        # 检查最近是否有更新（1年内）
        updated_at = datetime.datetime.strptime(project['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        if (datetime.datetime.now() - updated_at).days > 365:
            return False
        
        return True
    
    def _days_since_created(self, project: Dict[str, Any]) -> int:
        """计算项目创建天数"""
        created_at = datetime.datetime.strptime(project['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        return (datetime.datetime.now() - created_at).days
    
    def _days_since_updated(self, project: Dict[str, Any]) -> int:
        """计算项目最后更新天数"""
        updated_at = datetime.datetime.strptime(project['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        return (datetime.datetime.now() - updated_at).days
    
    def get_project_details(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """获取项目详细信息"""
        
        repo_url = project['url']
        
        try:
            # 获取README内容
            readme_url = f"{repo_url}/readme"
            readme_response = requests.get(readme_url, headers=self.headers)
            readme_content = ""
            
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                if readme_data.get('encoding') == 'base64':
                    import base64
                    readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
            
            # 获取最近的提交信息
            commits_url = f"{repo_url}/commits"
            commits_response = requests.get(f"{commits_url}?per_page=5", headers=self.headers)
            recent_commits = []
            
            if commits_response.status_code == 200:
                commits_data = commits_response.json()
                recent_commits = [
                    {
                        'message': commit['commit']['message'][:100],
                        'date': commit['commit']['author']['date'],
                        'author': commit['commit']['author']['name']
                    }
                    for commit in commits_data[:3]
                ]
            
            # 获取语言统计
            languages_url = f"{repo_url}/languages"
            languages_response = requests.get(languages_url, headers=self.headers)
            languages = {}
            
            if languages_response.status_code == 200:
                languages = languages_response.json()
            
            return {
                'basic_info': project,
                'readme_content': readme_content[:2000],  # 限制长度
                'recent_commits': recent_commits,
                'languages': languages,
                'topics': project.get('topics', [])
            }
            
        except Exception as e:
            print(f"获取项目详情失败: {e}")
            return {'basic_info': project}
    
    def analyze_project_category(self, project_details: Dict[str, Any]) -> str:
        """分析项目类别"""
        
        basic_info = project_details['basic_info']
        readme = project_details.get('readme_content', '').lower()
        topics = project_details.get('topics', [])
        description = basic_info.get('description', '').lower()
        
        # 关键词分类 - AI Agent相关
        categories = {
            '代码开发助手': ['code', 'developer', 'programming', 'coding', 'software', 'refactor', 'debug'],
            '内容创作工具': ['content', 'writing', 'blog', 'article', 'copywriting', 'seo', 'marketing'],
            '数据分析Agent': ['data', 'analysis', 'analytics', 'report', 'dashboard', 'visualization'],
            '自动化工作流': ['automation', 'workflow', 'task', 'process', 'integration', 'pipeline'],
            '聊天机器人': ['chat', 'conversation', 'dialog', 'messaging', 'assistant', 'bot'],
            'API集成工具': ['api', 'integration', 'connector', 'webhook', 'rest', 'graphql'],
            '研究分析助手': ['research', 'analysis', 'summarization', 'extraction', 'knowledge']
        }
        
        text_to_analyze = f"{description} {readme} {' '.join(topics)}"
        
        for category, keywords in categories.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                return category
        
        return 'AI助手工具'
    
    def generate_review_content(self, project_details: Dict[str, Any]) -> str:
        """生成评测文章内容"""
        
        basic_info = project_details['basic_info']
        category = self.analyze_project_category(project_details)
        
        # 基本信息
        name = basic_info['name']
        description = basic_info.get('description', '暂无描述')
        stars = basic_info['stargazers_count']
        forks = basic_info['forks_count']
        language = basic_info.get('language', '未知')
        created_at = basic_info['created_at'][:10]
        updated_at = basic_info['updated_at'][:10]
        homepage = basic_info.get('homepage', '')
        github_url = basic_info['html_url']
        
        # 生成文章内容
        content = f"""**📋 项目快览**: {name}是一个{category}，GitHub上{stars:,}个⭐，主要使用{language}开发

**{name}**是一个备受关注的{category}，在GitHub上已获得{stars:,}个星标，展现出强劲的社区关注度和发展潜力。该项目主要使用{language}开发，为Claude Code生态系统提供创新的AI助手解决方案。

## 🎯 项目概览

### 基本信息
- **项目名称**: {name}
- **项目类型**: {category}
- **开发语言**: {language}
- **GitHub地址**: [{github_url}]({github_url})
- **GitHub Stars**: {stars:,}
- **Fork数量**: {forks:,}
- **创建时间**: {created_at}
- **最近更新**: {updated_at}
- **官方网站**: {homepage if homepage else '暂无'}

### 项目描述
{description}

## 🛠️ 技术特点

### 开发活跃度
该项目在GitHub上表现出良好的开发活跃度：
- ⭐ **社区关注**: {stars:,}个星标显示了强劲的社区支持
- 🔄 **代码贡献**: {forks:,}个Fork表明开发者积极参与
- 📅 **持续更新**: 最近更新于{updated_at}，保持活跃开发状态

### 技术栈分析"""

        # 添加语言统计
        if 'languages' in project_details and project_details['languages']:
            content += "\n\n**主要编程语言构成**:\n"
            total_bytes = sum(project_details['languages'].values())
            for lang, bytes_count in sorted(project_details['languages'].items(), key=lambda x: x[1], reverse=True)[:5]:
                percentage = (bytes_count / total_bytes) * 100
                content += f"- {lang}: {percentage:.1f}%\n"

        # 添加最近提交信息
        if 'recent_commits' in project_details and project_details['recent_commits']:
            content += "\n\n### 最近开发动态\n"
            for commit in project_details['recent_commits']:
                commit_date = commit['date'][:10]
                content += f"- **{commit_date}**: {commit['message']} (by {commit['author']})\n"

        # 添加项目标签
        if 'topics' in project_details and project_details['topics']:
            content += f"\n\n### 🏷️ 项目标签\n"
            topics_badges = []
            for topic in project_details['topics'][:10]:
                topics_badges.append(f"`{topic}`")
            content += f"该项目被标记为: {' '.join(topics_badges)}\n"

        # 添加评测分析
        content += f"""

## 📊 项目评测

### 🎯 核心优势
1. **社区认可度高**: {stars:,}个GitHub星标证明了项目的受欢迎程度
2. **开发活跃**: 持续的代码更新显示项目处于积极开发状态
3. **技术创新**: 在{category}领域提供独特的AI助手解决方案
4. **开源透明**: 完全开源，代码可审计，增强用户信任
5. **Claude集成**: 充分利用Claude Code的强大能力，提供专业级AI助手

### ⚠️ 潜在考虑
1. **项目成熟度**: 作为相对较新的项目，需要时间验证稳定性
2. **生态建设**: 需要持续建设开发者和用户生态
3. **技术依赖**: 依赖于Claude API的稳定性和可用性
4. **学习曲线**: 可能需要一定的技术背景才能充分发挥作用

### 💡 使用建议
- **开发者**: 适合关注AI助手技术发展的开发者学习和贡献
- **技术用户**: 可以尝试集成到现有工作流中提高效率
- **研究者**: 可作为AI助手技术研究的参考案例
- **企业用户**: 建议先进行小规模测试验证实际效果

## 🔮 发展前景

基于当前的GitHub数据和社区反响，{name}展现出以下发展潜力：

1. **技术创新**: 在{category}领域的技术创新可能带来突破性进展
2. **社区增长**: 快速增长的星标数显示强劲的社区兴趣
3. **生态扩展**: 有潜力在AI助手生态系统中占据重要位置
4. **商业应用**: 技术成熟后可能产生实际的商业应用价值
5. **行业影响**: 可能推动整个AI助手行业的技术发展

## 📈 数据表现

| 指标 | 数值 | 说明 |
|------|------|------|
| GitHub Stars | {stars:,} | 社区关注度指标 |
| Fork数量 | {forks:,} | 开发者参与度 |
| 主要语言 | {language} | 技术栈核心 |
| 项目年龄 | {(datetime.datetime.now() - datetime.datetime.strptime(created_at, '%Y-%m-%d')).days}天 | 项目成熟度参考 |
| 更新频率 | {(datetime.datetime.now() - datetime.datetime.strptime(updated_at, '%Y-%m-%d')).days}天前更新 | 开发活跃度 |

---

*本评测基于GitHub公开数据分析生成，旨在为开发者社区提供有价值的AI助手项目信息。技术发展迅速，建议关注项目最新动态。*"""

        return content

def main():
    """主函数"""
    
    # 从环境变量获取参数
    days_back = int(os.getenv('DAYS_BACK', '7'))
    max_projects = int(os.getenv('MAX_PROJECTS', '3'))
    
    print(f"🔍 搜索参数: 最近 {days_back} 天, 最多 {max_projects} 个项目")
    
    # 从环境变量获取GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    
    if github_token:
        # 在GitHub Actions环境中，不显示token内容
        if os.getenv('GITHUB_ACTIONS'):
            print("✅ 使用GitHub Actions内置Token")
        else:
            print(f"✅ 已获取GitHub Token: {github_token[:8]}...")
    else:
        print("⚠️  警告: 未设置GITHUB_TOKEN环境变量，API调用可能受限")
        if not os.getenv('GITHUB_ACTIONS'):
            print("💡 提示: 请在 .env.local 文件中设置 GITHUB_TOKEN=your_token")
    
    analyzer = ClaudeAgentAnalyzer(github_token)
    
    print("🔍 开始搜索热门Claude Code Agent项目...")
    
    # 加载已分析项目历史（使用去重器）
    stats = analyzer.deduplicator.get_project_statistics()
    print(f"📚 当前已分析项目数量: {stats['total_projects']}")
    
    try:
        projects = analyzer.search_claude_agents(days_back=days_back, max_projects=max_projects)
    except Exception as e:
        print(f"❌ 搜索项目时出错: {e}")
        return
    
    if not projects:
        print("❌ 未找到符合条件的新项目")
        print("💡 提示: 所有最近的项目可能都已经分析过了")
        return
    
    print(f"✅ 找到 {len(projects)} 个新项目")
    
    # 生成今日日期用于文件名
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # 检查今日是否已生成文章（更宽松的检查）
    existing_articles = []
    content_posts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'content', 'posts')
    if os.path.exists(content_posts_dir):
        existing_articles = [f for f in os.listdir(content_posts_dir) if today in f and f.endswith('.md')]
    
    if len(existing_articles) >= 3:  # 每日最多3篇
        print(f"ℹ️  今日已存在 {len(existing_articles)} 篇文章，达到每日限制")
        return
    
    generated_count = 0
    
    for i, project in enumerate(projects, 1):
        try:
            print(f"\n📊 分析项目 {i}: {project['name']}")
            
            # 获取详细信息
            project_details = analyzer.get_project_details(project)
            
            # 生成评测内容
            review_content = analyzer.generate_review_content(project_details)
            
            # 生成文件名和标题（处理特殊字符）
            project_name = re.sub(r'[^\w\-]', '-', project['name'].lower())
            project_name = re.sub(r'-+', '-', project_name).strip('-')
            filename = f"github-claude-agent-{project_name}-review-{today}.md"
            
            # 确保文件名不重复
            counter = 1
            original_filename = filename
            while os.path.exists(os.path.join(content_posts_dir, filename)):
                name_part = original_filename.replace('.md', '')
                filename = f"{name_part}-{counter}.md"
                counter += 1
            
            title = f"GitHub热门项目评测：{project['name']} - {analyzer.analyze_project_category(project_details)}深度分析"
            
            # 处理描述中的特殊字符（TOML格式）
            description = project.get('description', '')
            if description:
                # TOML字符串转义：双引号需要转义为 \"，反斜杠需要转义为 \\
                description = description.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')[:150]
            else:
                description = f"{project['name']}项目深度评测分析"
            
            # 处理标题中的特殊字符（TOML格式）
            safe_title = title.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
            safe_project_name = project['name'].replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
            
            # 创建Hugo文章（使用正确的TOML格式）
            # 处理分类和标签中的特殊字符
            category = analyzer.analyze_project_category(project_details)
            safe_category = category.replace('\\', '\\\\').replace('"', '\\"')
            language = project.get('language', 'Unknown')
            safe_language = language.replace('\\', '\\\\').replace('"', '\\"') if language else 'Unknown'
            
            # 构建完整的描述和摘要
            if description and description != f"{project['name']}项目深度评测分析":
                # 如果有英文描述，先翻译或处理
                full_description = f"{project['name']}项目：{description}。GitHub {project['stargazers_count']:,} stars，{safe_category}领域热门开源项目深度评测。"
            else:
                full_description = f"{description}。GitHub {project['stargazers_count']:,} stars，{safe_category}领域热门开源项目深度评测。"
            full_summary = f"{safe_project_name}是一个备受关注的{safe_category}项目，在GitHub上已获得{project['stargazers_count']:,}个星标。"
            
            hugo_content = f"""+++
date = "{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')}"
draft = false
title = "{safe_title}"
description = "{full_description}"
summary = "{full_summary}"
tags = ["GitHub", "开源项目", "AI助手", "{safe_category}", "{safe_language}", "项目评测"]
categories = ["GitHub热门"]
keywords = ["{safe_project_name}评测", "GitHub AI项目", "{safe_category}工具", "开源AI项目"]
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
alt = "{safe_project_name} - {safe_category}项目评测"
caption = "GitHub热门AI项目深度分析"
relative = false
hidden = false
+++

{review_content}

---

## 📞 关于作者

**ERIC** - AI技术专家，专注于人工智能和自动化工具的研究与应用

### 🔗 联系方式与平台

- **📧 邮箱**: [gyc567@gmail.com](mailto:gyc567@gmail.com)
- **🐦 Twitter**: [@EricBlock2100](https://twitter.com/EricBlock2100)
- **💬 微信**: 360369487
- **📱 Telegram**: [https://t.me/fatoshi_block](https://t.me/fatoshi_block)
- **📢 Telegram频道**: [https://t.me/cryptochanneleric](https://t.me/cryptochanneleric)
- **👥 加密情报TG群**: [https://t.me/btcgogopen](https://t.me/btcgogopen)
- **🎥 YouTube频道**: [https://www.youtube.com/@0XBitFinance](https://www.youtube.com/@0XBitFinance)

### 🌐 相关平台

- **🌐 个人技术博客**: [https://www.topdigg.com/](https://www.topdigg.com/)
- **📖 公众号**: 比特财商

*欢迎关注我的各个平台，获取最新的AI技术分析和工具评测！*
"""
            
            # 确保目录存在
            os.makedirs(content_posts_dir, exist_ok=True)
            
            # 保存文章文件
            output_path = os.path.join(content_posts_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(hugo_content)
            
            print(f"✅ 已生成文章: {output_path}")
            generated_count += 1
            
            # 使用去重器标记项目为已分析
            analyzer.deduplicator.add_analyzed_project(project)
            print(f"📝 已标记项目为已分析: {project['name']}")
            
            # 避免API限制
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ 处理项目 {project['name']} 时出错: {e}")
            continue
    
    # 显示最终统计信息
    final_stats = analyzer.deduplicator.get_project_statistics()
    
    if generated_count > 0:
        print(f"\n🎉 完成！共生成 {generated_count} 篇评测文章")
        print(f"📊 累计已分析项目: {final_stats['total_projects']} 个")
    else:
        print(f"\n⚠️  未能生成任何文章")
        print(f"💡 建议: 尝试扩大搜索范围或等待新项目出现")

if __name__ == "__main__":
    main()