#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目去重管理器模块

该模块提供项目去重功能，确保每个GitHub项目只被分析一次。
遵循KISS原则，保持代码简洁和高内聚低耦合。

作者: Qoder AI Assistant
创建时间: 2025-08-24
"""

import os
import json
import hashlib
import re
import datetime
from typing import Dict, Set, Any, Optional
from urllib.parse import urlparse


class ProjectDeduplicator:
    """项目去重管理器 - 负责检查和管理项目重复性"""
    
    def __init__(self, history_file_path: str):
        """
        初始化去重器
        
        Args:
            history_file_path: 历史记录文件路径
        """
        self.history_file_path = history_file_path
        self._ensure_directory()
        self._analyzed_projects = self._load_analyzed_projects()
    
    def _ensure_directory(self) -> None:
        """确保历史文件目录存在"""
        directory = os.path.dirname(self.history_file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
    
    def normalize_github_url(self, github_url: str) -> str:
        """
        标准化GitHub URL
        
        Args:
            github_url: 原始GitHub URL
            
        Returns:
            标准化的GitHub仓库标识符 (owner/repo)
            
        Examples:
            https://github.com/owner/repo -> owner/repo
            https://github.com/owner/repo.git -> owner/repo
            git@github.com:owner/repo.git -> owner/repo
            https://api.github.com/repos/owner/repo -> owner/repo
        """
        if not github_url or not isinstance(github_url, str):
            return github_url
        
        # 移除前后空白
        url = github_url.strip()
        
        # 处理SSH格式 git@github.com:owner/repo.git
        ssh_pattern = r'git@github\.com:([^/]+/[^/]+)(?:\.git)?'
        ssh_match = re.match(ssh_pattern, url)
        if ssh_match:
            return ssh_match.group(1)
        
        # 处理HTTPS格式
        try:
            parsed = urlparse(url)
            if parsed.hostname == 'github.com' or parsed.hostname == 'api.github.com':
                path = parsed.path.strip('/')
                
                # 处理 api.github.com/repos/owner/repo 格式
                if path.startswith('repos/'):
                    path = path[6:]  # 移除 'repos/' 前缀
                
                # 移除 .git 后缀
                if path.endswith('.git'):
                    path = path[:-4]
                
                # 验证格式为 owner/repo
                if '/' in path and len(path.split('/')) >= 2:
                    parts = path.split('/')
                    return f"{parts[0]}/{parts[1]}"
        except Exception:
            # 解析失败，返回原始URL
            pass
        
        return github_url
    
    def generate_project_hash(self, project_info: Dict[str, Any]) -> str:
        """
        生成项目唯一哈希标识
        
        Args:
            project_info: 项目信息字典
            
        Returns:
            项目的SHA256哈希标识符
        """
        # 提取关键标识信息
        identifier_parts = []
        
        # 优先使用 full_name
        if 'full_name' in project_info and project_info['full_name']:
            identifier_parts.append(project_info['full_name'].lower())
        
        # 使用标准化的GitHub URL
        if 'html_url' in project_info and project_info['html_url']:
            normalized_url = self.normalize_github_url(project_info['html_url'])
            identifier_parts.append(normalized_url.lower())
        
        # 使用项目ID作为备用标识
        if 'id' in project_info:
            identifier_parts.append(str(project_info['id']))
        
        # 生成哈希
        combined_identifier = '|'.join(identifier_parts)
        return hashlib.sha256(combined_identifier.encode('utf-8')).hexdigest()
    
    def _get_project_identifier(self, project: Dict[str, Any]) -> str:
        """
        获取项目标准化标识符
        
        Args:
            project: 项目信息字典
            
        Returns:
            标准化的项目标识符
        """
        # 优先使用 full_name
        if 'full_name' in project and project['full_name']:
            return project['full_name'].lower()
        
        # 使用标准化URL
        if 'html_url' in project and project['html_url']:
            normalized = self.normalize_github_url(project['html_url'])
            if normalized and normalized != project['html_url']:
                return normalized.lower()
        
        # 备用方案：使用owner/name组合
        owner = project.get('owner', {}).get('login', 'unknown')
        name = project.get('name', 'unknown')
        return f"{owner}/{name}".lower()
    
    def is_duplicate_project(self, project: Dict[str, Any]) -> bool:
        """
        检查项目是否为重复项目
        
        Args:
            project: GitHub API返回的项目信息
            
        Returns:
            True: 项目已被分析过
            False: 项目未被分析过
        """
        project_identifier = self._get_project_identifier(project)
        return project_identifier in self._analyzed_projects
    
    def add_analyzed_project(self, project: Dict[str, Any]) -> None:
        """
        将项目添加到已分析列表
        
        Args:
            project: 项目信息字典
        """
        project_identifier = self._get_project_identifier(project)
        project_hash = self.generate_project_hash(project)
        
        # 添加项目记录
        self._analyzed_projects[project_identifier] = {
            'added_date': datetime.datetime.now().isoformat(),
            'project_hash': project_hash,
            'github_url': project.get('html_url', ''),
            'stars_when_analyzed': project.get('stargazers_count', 0)
        }
        
        # 保存到文件
        self._save_analyzed_projects()
    
    def get_project_statistics(self) -> Dict[str, Any]:
        """
        获取项目统计信息
        
        Returns:
            包含统计信息的字典
        """
        total_projects = len(self._analyzed_projects)
        
        # 按日期统计
        date_stats = {}
        for project_data in self._analyzed_projects.values():
            if isinstance(project_data, dict) and 'added_date' in project_data:
                date = project_data['added_date'][:10]  # YYYY-MM-DD
                date_stats[date] = date_stats.get(date, 0) + 1
        
        return {
            'total_projects': total_projects,
            'projects_by_date': date_stats,
            'last_updated': datetime.datetime.now().isoformat()
        }
    
    def _load_analyzed_projects(self) -> Dict[str, Any]:
        """
        加载已分析的项目历史记录
        
        Returns:
            已分析项目字典
        """
        try:
            if os.path.exists(self.history_file_path):
                with open(self.history_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理旧格式数据（列表格式）
                    if 'analyzed_projects' in data:
                        if isinstance(data['analyzed_projects'], list):
                            # 迁移旧格式数据
                            return self._migrate_from_list_format(data['analyzed_projects'])
                        elif isinstance(data['analyzed_projects'], dict):
                            return data['analyzed_projects']
                    
                    return {}
            return {}
        except Exception as e:
            print(f"⚠️  加载项目历史记录失败: {e}")
            return {}
    
    def _migrate_from_list_format(self, old_data: list) -> Dict[str, Any]:
        """
        从旧的列表格式迁移数据到新的字典格式
        
        Args:
            old_data: 旧格式的项目列表
            
        Returns:
            新格式的项目字典
        """
        migrated_data = {}
        current_time = datetime.datetime.now().isoformat()
        
        for project_key in old_data:
            if isinstance(project_key, str):
                migrated_data[project_key] = {
                    'added_date': current_time,
                    'project_hash': hashlib.sha256(project_key.encode('utf-8')).hexdigest(),
                    'github_url': f"https://github.com/{project_key}",
                    'stars_when_analyzed': 0,
                    'migrated_from_v1': True
                }
        
        print(f"✅ 已迁移 {len(migrated_data)} 个项目记录到新格式")
        return migrated_data
    
    def _save_analyzed_projects(self) -> None:
        """保存已分析的项目历史记录"""
        try:
            data = {
                'version': '2.0',
                'last_updated': datetime.datetime.now().isoformat(),
                'total_projects': len(self._analyzed_projects),
                'analyzed_projects': self._analyzed_projects
            }
            
            with open(self.history_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"⚠️  保存项目历史记录失败: {e}")


if __name__ == "__main__":
    # 简单的演示用法
    deduplicator = ProjectDeduplicator("test_history.json")
    
    # 测试项目
    test_project = {
        "full_name": "browser-use/browser-use",
        "html_url": "https://github.com/browser-use/browser-use",
        "stargazers_count": 890
    }
    
    print(f"项目是否重复: {deduplicator.is_duplicate_project(test_project)}")
    
    if not deduplicator.is_duplicate_project(test_project):
        deduplicator.add_analyzed_project(test_project)
        print("已添加项目到分析历史")
    
    print(f"统计信息: {deduplicator.get_project_statistics()}")