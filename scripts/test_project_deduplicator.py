#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProjectDeduplicator单元测试模块

该模块提供ProjectDeduplicator类的完整单元测试，确保100%测试覆盖率。
测试包括正常情况、边缘情况和异常情况。

作者: Qoder AI Assistant
创建时间: 2025-08-24
"""

import unittest
import tempfile
import os
import json
import hashlib
import shutil
from unittest.mock import patch, mock_open
import datetime
import sys

# 添加scripts目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project_deduplicator import ProjectDeduplicator


class TestProjectDeduplicator(unittest.TestCase):
    """ProjectDeduplicator单元测试类"""
    
    def setUp(self):
        """测试前置准备"""
        # 创建临时目录和文件
        self.temp_dir = tempfile.mkdtemp()
        self.test_history_file = os.path.join(self.temp_dir, 'test_history.json')
        self.deduplicator = ProjectDeduplicator(self.test_history_file)
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    # URL标准化测试
    def test_normalize_github_url_standard_https(self):
        """测试标准HTTPS GitHub URL格式化"""
        test_cases = [
            ("https://github.com/owner/repo", "owner/repo"),
            ("https://github.com/owner/repo.git", "owner/repo"),
            ("https://github.com/OWNER/REPO", "OWNER/REPO"),
            ("https://github.com/owner/repo/", "owner/repo"),
        ]
        
        for input_url, expected in test_cases:
            with self.subTest(input_url=input_url):
                result = self.deduplicator.normalize_github_url(input_url)
                self.assertEqual(result, expected)
    
    def test_normalize_github_url_ssh_format(self):
        """测试SSH格式GitHub URL标准化"""
        test_cases = [
            ("git@github.com:owner/repo.git", "owner/repo"),
            ("git@github.com:owner/repo", "owner/repo"),
            ("git@github.com:Owner/Repo.git", "Owner/Repo"),
        ]
        
        for input_url, expected in test_cases:
            with self.subTest(input_url=input_url):
                result = self.deduplicator.normalize_github_url(input_url)
                self.assertEqual(result, expected)
    
    def test_normalize_github_url_api_format(self):
        """测试GitHub API URL格式标准化"""
        test_cases = [
            ("https://api.github.com/repos/owner/repo", "owner/repo"),
            ("https://api.github.com/repos/owner/repo.git", "owner/repo"),
        ]
        
        for input_url, expected in test_cases:
            with self.subTest(input_url=input_url):
                result = self.deduplicator.normalize_github_url(input_url)
                self.assertEqual(result, expected)
    
    def test_normalize_github_url_edge_cases(self):
        """测试边缘情况URL格式化"""
        edge_cases = [
            ("", ""),
            (None, None),
            ("invalid-url", "invalid-url"),
            ("https://gitlab.com/owner/repo", "https://gitlab.com/owner/repo"),
            ("http://github.com/owner/repo", "owner/repo"),
            ("   https://github.com/owner/repo   ", "owner/repo"),
        ]
        
        for input_url, expected in edge_cases:
            with self.subTest(input_url=input_url):
                result = self.deduplicator.normalize_github_url(input_url)
                self.assertEqual(result, expected)
    
    def test_normalize_github_url_invalid_types(self):
        """测试无效类型输入"""
        invalid_inputs = [123, [], {}, True]
        
        for invalid_input in invalid_inputs:
            with self.subTest(invalid_input=invalid_input):
                result = self.deduplicator.normalize_github_url(invalid_input)
                self.assertEqual(result, invalid_input)
    
    # 项目哈希生成测试
    def test_generate_project_hash_with_full_name(self):
        """测试使用full_name生成项目哈希"""
        project1 = {
            "full_name": "owner/repo",
            "html_url": "https://github.com/owner/repo",
            "id": 123456
        }
        
        project2 = {
            "full_name": "owner/repo",
            "html_url": "https://github.com/owner/repo",
            "id": 123456
        }
        
        hash1 = self.deduplicator.generate_project_hash(project1)
        hash2 = self.deduplicator.generate_project_hash(project2)
        
        # 相同项目应生成相同哈希
        self.assertEqual(hash1, hash2)
        # 哈希应为64位SHA256
        self.assertEqual(len(hash1), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in hash1))
    
    def test_generate_project_hash_without_full_name(self):
        """测试无full_name时使用URL生成哈希"""
        project = {
            "html_url": "https://github.com/owner/repo",
            "id": 123456
        }
        
        hash_result = self.deduplicator.generate_project_hash(project)
        
        self.assertEqual(len(hash_result), 64)
        self.assertIsInstance(hash_result, str)
    
    def test_generate_project_hash_minimal_info(self):
        """测试最少信息情况下的哈希生成"""
        project = {"id": 123456}
        
        hash_result = self.deduplicator.generate_project_hash(project)
        
        self.assertEqual(len(hash_result), 64)
        self.assertIsInstance(hash_result, str)
    
    def test_generate_project_hash_empty_project(self):
        """测试空项目信息的哈希生成"""
        project = {}
        
        hash_result = self.deduplicator.generate_project_hash(project)
        
        self.assertEqual(len(hash_result), 64)
        self.assertIsInstance(hash_result, str)
    
    # 项目标识符获取测试
    def test_get_project_identifier_with_full_name(self):
        """测试使用full_name获取项目标识符"""
        project = {
            "full_name": "Owner/Repo",
            "html_url": "https://github.com/Owner/Repo"
        }
        
        identifier = self.deduplicator._get_project_identifier(project)
        self.assertEqual(identifier, "owner/repo")
    
    def test_get_project_identifier_with_url_only(self):
        """测试仅使用URL获取项目标识符"""
        project = {
            "html_url": "https://github.com/owner/repo"
        }
        
        identifier = self.deduplicator._get_project_identifier(project)
        self.assertEqual(identifier, "owner/repo")
    
    def test_get_project_identifier_with_owner_name(self):
        """测试使用owner和name获取标识符"""
        project = {
            "owner": {"login": "owner"},
            "name": "repo"
        }
        
        identifier = self.deduplicator._get_project_identifier(project)
        self.assertEqual(identifier, "owner/repo")
    
    def test_get_project_identifier_fallback(self):
        """测试标识符获取的备用方案"""
        project = {}
        
        identifier = self.deduplicator._get_project_identifier(project)
        self.assertEqual(identifier, "unknown/unknown")
    
    # 重复检查测试
    def test_is_duplicate_project_new_project(self):
        """测试新项目检测"""
        project = {
            "full_name": "owner/new-repo",
            "html_url": "https://github.com/owner/new-repo"
        }
        
        # 新项目不应该重复
        self.assertFalse(self.deduplicator.is_duplicate_project(project))
    
    def test_is_duplicate_project_existing_project(self):
        """测试已存在项目检测"""
        project = {
            "full_name": "browser-use/browser-use",
            "html_url": "https://github.com/browser-use/browser-use"
        }
        
        # 首次添加
        self.deduplicator.add_analyzed_project(project)
        
        # 再次检查应返回重复
        self.assertTrue(self.deduplicator.is_duplicate_project(project))
    
    def test_is_duplicate_project_case_insensitive(self):
        """测试大小写不敏感的重复检测"""
        project1 = {
            "full_name": "Owner/Repo",
            "html_url": "https://github.com/Owner/Repo"
        }
        
        project2 = {
            "full_name": "owner/repo",
            "html_url": "https://github.com/owner/repo"
        }
        
        # 添加第一个项目
        self.deduplicator.add_analyzed_project(project1)
        
        # 第二个项目应被识别为重复（大小写不敏感）
        self.assertTrue(self.deduplicator.is_duplicate_project(project2))
    
    # 添加已分析项目测试
    def test_add_analyzed_project_success(self):
        """测试成功添加已分析项目"""
        project = {
            "full_name": "test/project",
            "html_url": "https://github.com/test/project",
            "stargazers_count": 100
        }
        
        # 添加项目
        self.deduplicator.add_analyzed_project(project)
        
        # 验证项目已被记录
        self.assertTrue(self.deduplicator.is_duplicate_project(project))
        
        # 验证统计信息
        stats = self.deduplicator.get_project_statistics()
        self.assertEqual(stats['total_projects'], 1)
    
    def test_add_analyzed_project_with_file_persistence(self):
        """测试添加项目后的文件持久化"""
        project = {
            "full_name": "persistent/project",
            "html_url": "https://github.com/persistent/project",
            "stargazers_count": 50
        }
        
        # 添加项目
        self.deduplicator.add_analyzed_project(project)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(self.test_history_file))
        
        # 验证文件内容
        with open(self.test_history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('analyzed_projects', data)
            self.assertIn('persistent/project', data['analyzed_projects'])
    
    # 统计信息测试
    def test_get_project_statistics_empty(self):
        """测试空项目列表的统计信息"""
        stats = self.deduplicator.get_project_statistics()
        
        self.assertEqual(stats['total_projects'], 0)
        self.assertEqual(stats['projects_by_date'], {})
        self.assertIn('last_updated', stats)
    
    def test_get_project_statistics_with_projects(self):
        """测试有项目时的统计信息"""
        projects = [
            {
                "full_name": "test/project1",
                "html_url": "https://github.com/test/project1",
                "stargazers_count": 10
            },
            {
                "full_name": "test/project2", 
                "html_url": "https://github.com/test/project2",
                "stargazers_count": 20
            }
        ]
        
        for project in projects:
            self.deduplicator.add_analyzed_project(project)
        
        stats = self.deduplicator.get_project_statistics()
        
        self.assertEqual(stats['total_projects'], 2)
        self.assertGreater(len(stats['projects_by_date']), 0)
    
    # 数据加载和保存测试
    def test_load_analyzed_projects_empty_file(self):
        """测试加载空文件"""
        # 删除文件确保为空
        if os.path.exists(self.test_history_file):
            os.remove(self.test_history_file)
        
        deduplicator = ProjectDeduplicator(self.test_history_file)
        
        # 应该初始化为空字典
        self.assertEqual(len(deduplicator._analyzed_projects), 0)
    
    def test_load_analyzed_projects_invalid_json(self):
        """测试加载无效JSON文件"""
        # 写入无效JSON
        with open(self.test_history_file, 'w') as f:
            f.write("invalid json content")
        
        deduplicator = ProjectDeduplicator(self.test_history_file)
        
        # 应该返回空字典
        self.assertEqual(len(deduplicator._analyzed_projects), 0)
    
    # 数据迁移测试
    def test_migrate_from_list_format(self):
        """测试从旧列表格式迁移数据"""
        old_data = [
            "anthropics/claude-code",
            "browser-use/browser-use",
            "google-gemini/gemini-cli"
        ]
        
        migrated = self.deduplicator._migrate_from_list_format(old_data)
        
        # 验证迁移结果
        self.assertEqual(len(migrated), 3)
        for project_key in old_data:
            self.assertIn(project_key, migrated)
            self.assertIn('added_date', migrated[project_key])
            self.assertIn('project_hash', migrated[project_key])
            self.assertIn('migrated_from_v1', migrated[project_key])
    
    def test_load_with_old_list_format(self):
        """测试加载旧列表格式数据"""
        old_format_data = {
            "last_updated": "2025-08-23T16:05:41.388501",
            "total_projects": 2,
            "analyzed_projects": [
                "anthropics/claude-code",
                "browser-use/browser-use"
            ]
        }
        
        # 写入旧格式数据
        with open(self.test_history_file, 'w', encoding='utf-8') as f:
            json.dump(old_format_data, f)
        
        # 重新加载应该自动迁移
        deduplicator = ProjectDeduplicator(self.test_history_file)
        
        # 验证数据已迁移
        self.assertEqual(len(deduplicator._analyzed_projects), 2)
        self.assertIn("anthropics/claude-code", deduplicator._analyzed_projects)
        self.assertIn("browser-use/browser-use", deduplicator._analyzed_projects)
    
    def test_load_with_new_dict_format(self):
        """测试加载新字典格式数据"""
        new_format_data = {
            "version": "2.0",
            "last_updated": "2025-08-24T10:00:00.000000",
            "total_projects": 1,
            "analyzed_projects": {
                "test/project": {
                    "added_date": "2025-08-24T10:00:00.000000",
                    "project_hash": "abcd1234",
                    "github_url": "https://github.com/test/project",
                    "stars_when_analyzed": 100
                }
            }
        }
        
        # 写入新格式数据
        with open(self.test_history_file, 'w', encoding='utf-8') as f:
            json.dump(new_format_data, f)
        
        deduplicator = ProjectDeduplicator(self.test_history_file)
        
        # 验证数据正确加载
        self.assertEqual(len(deduplicator._analyzed_projects), 1)
        self.assertIn("test/project", deduplicator._analyzed_projects)
    
    # 文件保存测试
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_save_analyzed_projects_permission_error(self, mock_open):
        """测试保存文件时权限错误"""
        project = {
            "full_name": "test/project",
            "html_url": "https://github.com/test/project"
        }
        
        # 应该不会抛出异常，而是打印警告
        self.deduplicator.add_analyzed_project(project)
        
        # 验证项目仍在内存中
        self.assertTrue(self.deduplicator.is_duplicate_project(project))
    
    # 目录创建测试
    def test_ensure_directory_creation(self):
        """测试确保目录创建"""
        nested_path = os.path.join(self.temp_dir, 'nested', 'deep', 'path', 'history.json')
        
        deduplicator = ProjectDeduplicator(nested_path)
        
        # 验证目录已创建
        self.assertTrue(os.path.exists(os.path.dirname(nested_path)))
    
    def test_ensure_directory_no_directory(self):
        """测试文件路径无目录的情况"""
        simple_filename = 'simple_history.json'
        
        # 不应该抛出异常
        deduplicator = ProjectDeduplicator(simple_filename)
        
        self.assertIsInstance(deduplicator, ProjectDeduplicator)


class TestProjectDeduplicatorIntegration(unittest.TestCase):
    """ProjectDeduplicator集成测试类"""
    
    def setUp(self):
        """集成测试前置准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_history_file = os.path.join(self.temp_dir, 'integration_history.json')
        self.deduplicator = ProjectDeduplicator(self.test_history_file)
    
    def tearDown(self):
        """集成测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 测试项目列表
        test_projects = [
            {
                "full_name": "anthropics/claude-code",
                "html_url": "https://github.com/anthropics/claude-code",
                "stargazers_count": 1000
            },
            {
                "full_name": "browser-use/browser-use",
                "html_url": "https://github.com/browser-use/browser-use",
                "stargazers_count": 500
            },
            {
                "full_name": "anthropics/claude-code",  # 重复项目
                "html_url": "https://github.com/anthropics/claude-code",
                "stargazers_count": 1050
            }
        ]
        
        added_count = 0
        skipped_count = 0
        
        for project in test_projects:
            if not self.deduplicator.is_duplicate_project(project):
                self.deduplicator.add_analyzed_project(project)
                added_count += 1
            else:
                skipped_count += 1
        
        # 验证结果
        self.assertEqual(added_count, 2)  # 只添加了两个唯一项目
        self.assertEqual(skipped_count, 1)  # 跳过了一个重复项目
        
        # 验证统计信息
        stats = self.deduplicator.get_project_statistics()
        self.assertEqual(stats['total_projects'], 2)
        
        # 验证文件持久化
        self.assertTrue(os.path.exists(self.test_history_file))
        
        # 重新加载验证持久化
        new_deduplicator = ProjectDeduplicator(self.test_history_file)
        self.assertEqual(len(new_deduplicator._analyzed_projects), 2)


class TestProjectDeduplicatorPerformance(unittest.TestCase):
    """ProjectDeduplicator性能测试类"""
    
    def setUp(self):
        """性能测试前置准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_history_file = os.path.join(self.temp_dir, 'performance_history.json')
        self.deduplicator = ProjectDeduplicator(self.test_history_file)
    
    def tearDown(self):
        """性能测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        import time
        
        # 生成1000个测试项目
        test_projects = []
        for i in range(1000):
            project = {
                "full_name": f"owner/repo-{i}",
                "html_url": f"https://github.com/owner/repo-{i}",
                "stargazers_count": i * 10
            }
            test_projects.append(project)
            self.deduplicator.add_analyzed_project(project)
        
        # 测试查询性能
        start_time = time.time()
        
        for project in test_projects[:100]:  # 测试100次查询
            self.deduplicator.is_duplicate_project(project)
        
        end_time = time.time()
        avg_query_time = (end_time - start_time) / 100
        
        # 每次查询应在10ms内完成（宽松标准）
        self.assertLess(avg_query_time, 0.01, f"平均查询时间 {avg_query_time:.4f}s 超过了 0.01s 的限制")
        
        # 验证数据正确性
        stats = self.deduplicator.get_project_statistics()
        self.assertEqual(stats['total_projects'], 1000)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)