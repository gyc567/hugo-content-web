#!/usr/bin/env python3
"""
GitHub Repo Evaluator - 七维度项目评估器
基于 github-repo-evaluator 评分体系，对 GitHub 项目进行快速评估
"""

import requests
import datetime
import re
from typing import Dict, List, Any, Tuple


class GitHubRepoEvaluator:
    """GitHub 仓库七维度评估器"""

    def __init__(self, headers: Dict[str, str] = None):
        self.headers = headers or {}

    def evaluate(self, project_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        对项目进行全面评估
        返回: {dimensions, total_score, decision, decision_reason}
        """
        basic_info = project_details.get('basic_info', {})
        readme = project_details.get('readme_content', '') or ''
        releases = project_details.get('releases', [])
        issues = project_details.get('issues', [])
        discussions = project_details.get('discussions', [])

        dimensions = []
        total_score = 0

        # 1. 用途清晰度
        status, reason = self._evaluate_clarity(readme, basic_info)
        dimensions.append({'name': '用途清晰度', 'status': status, 'reason': reason})
        total_score += self._score(status)

        # 2. 版本状态
        status, reason = self._evaluate_releases(releases)
        dimensions.append({'name': '版本状态', 'status': status, 'reason': reason})
        total_score += self._score(status)

        # 3. 维护状态
        status, reason = self._evaluate_maintenance(basic_info)
        dimensions.append({'name': '维护状态', 'status': status, 'reason': reason})
        total_score += self._score(status)

        # 4. 问题响应
        status, reason = self._evaluate_issues(issues)
        dimensions.append({'name': '问题响应', 'status': status, 'reason': reason})
        total_score += self._score(status)

        # 5. 热度可信度
        status, reason = self._evaluate_popularity(basic_info)
        dimensions.append({'name': '热度可信度', 'status': status, 'reason': reason})
        total_score += self._score(status)

        # 6. 需求真实度
        status, reason = self._evaluate_demand(issues, discussions)
        dimensions.append({'name': '需求真实度', 'status': status, 'reason': reason})
        total_score += self._score(status)

        # 7. 商业可行性
        status, reason = self._evaluate_monetization(basic_info, readme)
        dimensions.append({'name': '商业可行性', 'status': status, 'reason': reason})
        total_score += self._score(status)

        decision, reason = self._make_decision(total_score, dimensions)

        return {
            'dimensions': dimensions,
            'total_score': total_score,
            'decision': decision,
            'decision_reason': reason
        }

    def _score(self, status: str) -> int:
        if status == 'pass':
            return 1
        elif status == 'warn':
            return 0
        return -1

    def _status_icon(self, status: str) -> str:
        return {'pass': '✅', 'warn': '⚠️', 'fail': '❌'}.get(status, '⚠️')

    def _evaluate_clarity(self, readme: str, basic_info: Dict) -> Tuple[str, str]:
        """评估用途清晰度"""
        readme_lower = readme.lower()
        has_demo = any(k in readme_lower for k in ['demo', 'screenshot', 'preview', 'example', '.gif', 'png', 'jpg'])
        has_install = any(k in readme_lower for k in ['install', 'getting started', 'usage', 'quick start', 'how to'])
        has_what = any(k in readme_lower for k in ['what is', 'purpose', 'description of'])

        if has_what and (has_demo or has_install):
            return 'pass', 'README 清晰说明项目用途，含演示或安装说明'
        elif has_what or has_install:
            return 'warn', 'README 说明了用途，但缺少演示或安装说明'
        elif readme and len(readme) > 200:
            return 'warn', 'README 内容存在但用途不够明确'
        return 'fail', 'README 缺失或内容过少，无法了解项目用途'

    def _evaluate_releases(self, releases: List[Dict]) -> Tuple[str, str]:
        """评估版本状态"""
        if not releases:
            return 'fail', '无正式版本发布，只有源码'

        latest = releases[0] if releases else {}
        tag = latest.get('tag_name', '')
        has_version = bool(re.search(r'\d+\.\d+', tag))

        if has_version:
            return 'pass', f'最新版本: {tag}，有正式版本号'
        return 'warn', f'有发布记录但版本号不标准: {tag}'

    def _evaluate_maintenance(self, basic_info: Dict) -> Tuple[str, str]:
        """评估维护状态"""
        updated_at = basic_info.get('updated_at', '')
        if not updated_at:
            return 'warn', '无法获取更新时间'

        try:
            updated_date = datetime.datetime.strptime(updated_at, '%Y-%m-%dT%H:%M:%SZ')
            days_ago = (datetime.datetime.now() - updated_date).days

            if days_ago <= 30:
                return 'pass', f'最近 {days_ago} 天内有更新'
            elif days_ago <= 180:
                return 'warn', f'最近 {days_ago} 天有更新，6 个月内保持维护'
            elif days_ago <= 365:
                return 'warn', f'已 {days_ago} 天未更新，但一年内有过更新'
            return 'fail', f'超过一年未更新 ({days_ago} 天)'
        except Exception:
            return 'warn', '无法解析更新时间'

    def _evaluate_issues(self, issues: List[Dict]) -> Tuple[str, str]:
        """评估问题响应"""
        open_count = sum(1 for i in issues if i.get('state') == 'open')
        closed_count = sum(1 for i in issues if i.get('state') == 'closed')

        if open_count == 0:
            return 'pass', '无待处理问题，维护状态良好'
        elif closed_count > open_count:
            return 'pass', f'问题处理积极 (已关闭 {closed_count}，待处理 {open_count})'
        elif closed_count > 0:
            return 'warn', f'有 {open_count} 个待处理问题，部分已关闭'
        return 'warn', f'有 {open_count} 个待处理问题'

    def _evaluate_popularity(self, basic_info: Dict) -> Tuple[str, str]:
        """评估热度可信度"""
        stars = basic_info.get('stargazers_count', 0)
        forks = basic_info.get('forks_count', 0)
        fork_ratio = forks / stars if stars > 0 else 0

        if stars >= 100 and fork_ratio >= 0.05:
            return 'pass', f'Stars {stars:,}，Fork率 {fork_ratio:.0%}，热度真实可信'
        elif stars >= 50:
            return 'warn', f'Stars {stars:,}，热度尚可但需进一步验证'
        return 'warn', f'Stars {stars:,}，作为参考热度指标'

    def _evaluate_demand(self, issues: List[Dict], discussions: List[Dict]) -> Tuple[str, str]:
        """评估需求真实度"""
        total = len(issues) + len(discussions)

        if total == 0:
            return 'warn', '无 Issues 或 Discussions，无法判断需求'

        has_detailed = any(
            len((i.get('title') or '') + (i.get('body') or '')) > 50
            for i in issues[:5]
        )

        if has_detailed or total >= 5:
            return 'pass', f'存在 {total} 条真实用户需求/讨论'
        return 'warn', f'有 {total} 条记录，但内容较简短'

    def _evaluate_monetization(self, basic_info: Dict, readme: str) -> Tuple[str, str]:
        """评估商业可行性"""
        readme_lower = readme.lower()
        homepage = basic_info.get('homepage', '')

        has_deploy = any(k in readme_lower for k in ['deploy', 'docker', 'hosting', 'cloud', 'one-click'])
        has_template = any(k in readme_lower for k in ['template', 'starter', 'boilerplate', '免费', 'free'])
        has_pricing = any(k in readme_lower for k in ['pricing', 'paid', 'pro', 'enterprise', 'license'])

        if has_deploy:
            return 'pass', '提供部署方案，有变现路径'
        elif has_template or has_pricing:
            return 'warn', '有模板或版本区分，有一定商业可行性'
        elif homepage:
            return 'warn', '有官方网站，可进一步了解商业模式'
        return 'warn', '无明显商业信息'

    def _make_decision(self, total_score: int, dimensions: List[Dict]) -> Tuple[str, str]:
        """基于总分做出决策"""
        if total_score >= 3:
            reason = '项目在多数维度表现良好，值得下载使用'
        elif total_score >= 1:
            reason = '项目有一定潜力，但需进一步观察'
        else:
            reason = '项目存在较多不确定性，建议谨慎或关闭'

        decision_map = {
            (3, True): '下载',
            (2, True): '下载',
            (1, True): '观望',
            (0, True): '观望',
            (-1, True): '关掉',
            (-99, False): '观望'
        }

        for (threshold, condition), decision in decision_map.items():
            if condition and total_score >= threshold:
                return decision, reason

        return '观望', reason

    def render_markdown(self, result: Dict[str, Any], project_name: str = '') -> str:
        """将评估结果渲染为 Markdown 格式"""
        lines = ['## 🔍 GitHub Repo 七维度评估', '']

        # 表头
        lines.append('| 维度 | 状态 | 依据 |')
        lines.append('|-----|------|-----|')

        for dim in result['dimensions']:
            icon = self._status_icon(dim['status'])
            lines.append(f"| {dim['name']} | {icon} | {dim['reason']} |")

        lines.append('')
        lines.append(f'**七维度评分**: {result["total_score"]}/7')
        lines.append('')

        # 最终决策
        decision = result['decision']
        icon = {'下载': '✅', '观望': '⚠️', '关掉': '❌'}.get(decision, '⚠️')
        lines.append(f'## 🎯 最终决策')
        lines.append('')
        lines.append(f'{icon} **{decision}**')
        lines.append('')
        lines.append(f'理由: {result["decision_reason"]}')
        lines.append('')
        lines.append('---')

        return '\n'.join(lines)

    def fetch_extra_data(self, repo_url: str) -> Dict[str, Any]:
        """获取评估所需的额外数据（releases, issues, discussions）"""
        result = {'releases': [], 'issues': [], 'discussions': []}

        try:
            releases_resp = requests.get(
                f'{repo_url}/releases', headers=self.headers, timeout=10
            )
            if releases_resp.status_code == 200:
                result['releases'] = releases_resp.json()[:5]
        except Exception:
            pass

        try:
            issues_resp = requests.get(
                f'{repo_url}/issues',
                headers=self.headers,
                params={'state': 'all', 'per_page': 30},
                timeout=10
            )
            if issues_resp.status_code == 200:
                result['issues'] = issues_resp.json()
        except Exception:
            pass

        try:
            discussions_resp = requests.get(
                f'{repo_url}/discussions', headers=self.headers, timeout=10
            )
            if discussions_resp.status_code == 200:
                result['discussions'] = discussions_resp.json().get('data', [])[:10]
        except Exception:
            pass

        return result
