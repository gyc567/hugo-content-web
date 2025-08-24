#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试模块

该模块提供ClaudeAgentAnalyzer与ProjectDeduplicator集成功能的端到端测试，
验证去重功能在实际场景中的工作效果。

作者: Qoder AI Assistant
创建时间: 2025-08-24
"""

import unittest
import tempfile
import os
import json
import shutil
import sys
from unittest.mock import patch, Mock, MagicMock
import datetime

# 添加scripts目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 动态导入分析器模块（处理文件名中的连字符）
import importlib.util
spec = importlib.util.spec_from_file_location("crypto_project_analyzer", "crypto-project-analyzer.py")
crypto_analyzer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crypto_analyzer_module)
ClaudeAgentAnalyzer = crypto_analyzer_module.ClaudeAgentAnalyzer
from project_deduplicator import ProjectDeduplicator


class TestClaudeAgentAnalyzerIntegration(unittest.TestCase):
    """ClaudeAgentAnalyzer与ProjectDeduplicator集成测试类"""
    
    def setUp(self):
        """集成测试前置准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_history_file = os.path.join(self.temp_dir, 'integration_history.json')
        
        # 模拟GitHub token
        os.environ['GITHUB_TOKEN'] = 'test_token_12345'
        
        # 创建测试用的分析器实例
        self.analyzer = ClaudeAgentAnalyzer()
        # 替换历史文件路径为测试文件
        self.analyzer.history_file = self.test_history_file
        self.analyzer.deduplicator = ProjectDeduplicator(self.test_history_file)
    
    def tearDown(self):
        """集成测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # 清理环境变量
        if 'GITHUB_TOKEN' in os.environ:
            del os.environ['GITHUB_TOKEN']
    
    def create_mock_project(self, name: str, full_name: str, stars: int = 100) -> dict:
        """创建模拟项目数据"""
        return {
            "id": hash(full_name) % 1000000,  # 简单的ID生成
            "name": name,
            "full_name": full_name,
            "html_url": f"https://github.com/{full_name}",
            "description": f"Test project {name}",
            "stargazers_count": stars,
            "forks_count": stars // 10,
            "language": "Python",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-08-24T00:00:00Z",
            "topics": ["ai", "agent", "claude"],
            "owner": {"login": full_name.split('/')[0]}
        }
    
    @patch('requests.get')
    def test_search_claude_agents_with_deduplication(self, mock_get):
        """测试带去重的项目搜索功能"""
        # 准备模拟数据
        test_projects = [
            self.create_mock_project("claude-code", "anthropics/claude-code", 1000),
            self.create_mock_project("browser-use", "browser-use/browser-use", 800),
            self.create_mock_project("new-project", "newuser/new-project", 500),
        ]
        
        # 预先添加一个已分析项目
        existing_project = test_projects[0]  # claude-code
        self.analyzer.deduplicator.add_analyzed_project(existing_project)
        
        # 模拟GitHub API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": test_projects}
        mock_get.return_value = mock_response
        
        # 执行搜索
        results = self.analyzer.search_claude_agents(days_back=7, max_projects=3)
        
        # 验证结果
        self.assertEqual(len(results), 2)  # 应该过滤掉1个重复项目
        
        # 验证重复项目被过滤
        result_names = [p['name'] for p in results]
        self.assertNotIn('claude-code', result_names)  # 已分析项目应被过滤
        self.assertIn('browser-use', result_names)     # 新项目应包含
        self.assertIn('new-project', result_names)     # 新项目应包含
    
    def test_deduplicator_integration_with_analyzer(self):
        """测试去重器与分析器的完整集成"""
        # 测试项目
        test_project = self.create_mock_project("test-project", "testuser/test-project", 200)
        
        # 第一次检查 - 应该是新项目
        self.assertFalse(self.analyzer.deduplicator.is_duplicate_project(test_project))
        
        # 添加到已分析列表
        self.analyzer.deduplicator.add_analyzed_project(test_project)
        
        # 第二次检查 - 应该被识别为重复项目
        self.assertTrue(self.analyzer.deduplicator.is_duplicate_project(test_project))
        
        # 验证统计信息
        stats = self.analyzer.deduplicator.get_project_statistics()
        self.assertEqual(stats['total_projects'], 1)
    
    def test_url_normalization_in_deduplication(self):
        """测试URL标准化在去重中的应用"""
        # 创建具有不同URL格式但实际相同的项目
        project1 = {
            "id": 123,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "html_url": "https://github.com/owner/test-repo",
            "stargazers_count": 50
        }
        
        project2 = {
            "id": 124,  # 不同ID
            "name": "test-repo",
            "full_name": "owner/test-repo",  # 相同full_name
            "html_url": "https://github.com/owner/test-repo.git",  # 不同URL格式
            "stargazers_count": 55
        }
        
        # 添加第一个项目
        self.analyzer.deduplicator.add_analyzed_project(project1)
        
        # 第二个项目应被识别为重复（尽管URL格式不同）
        self.assertTrue(self.analyzer.deduplicator.is_duplicate_project(project2))
    
    def test_case_insensitive_deduplication(self):
        """测试大小写不敏感的去重"""
        project1 = self.create_mock_project("Test-Project", "Owner/Test-Project", 100)
        project2 = self.create_mock_project("test-project", "owner/test-project", 120)
        
        # 添加第一个项目
        self.analyzer.deduplicator.add_analyzed_project(project1)
        
        # 第二个项目应被识别为重复（大小写不敏感）
        self.assertTrue(self.analyzer.deduplicator.is_duplicate_project(project2))
    
    @patch('requests.get')
    def test_end_to_end_deduplication_workflow(self, mock_get):
        """测试端到端去重工作流程"""
        # 准备测试数据
        test_projects = [
            self.create_mock_project("project-1", "user1/project-1", 1000),
            self.create_mock_project("project-2", "user2/project-2", 800),
            self.create_mock_project("project-1", "user1/project-1", 1050),  # 重复项目
        ]
        
        # 模拟多次API调用
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": test_projects}
        mock_get.return_value = mock_response
        
        # 第一次搜索
        results1 = self.analyzer.search_claude_agents(days_back=7, max_projects=3)
        self.assertEqual(len(results1), 2)  # 应该去重，只返回2个唯一项目
        
        # 模拟分析过程 - 将找到的项目标记为已分析
        for project in results1:
            self.analyzer.deduplicator.add_analyzed_project(project)
        
        # 第二次搜索 - 应该返回空结果（所有项目都已分析）
        results2 = self.analyzer.search_claude_agents(days_back=7, max_projects=3)
        self.assertEqual(len(results2), 0)  # 所有项目都应被过滤
        
        # 验证统计信息
        stats = self.analyzer.deduplicator.get_project_statistics()
        self.assertEqual(stats['total_projects'], 2)
    
    def test_data_persistence_across_instances(self):
        """测试数据在不同实例间的持久化"""
        # 第一个分析器实例
        analyzer1 = ClaudeAgentAnalyzer()
        analyzer1.history_file = self.test_history_file
        analyzer1.deduplicator = ProjectDeduplicator(self.test_history_file)
        
        test_project = self.create_mock_project("persist-test", "user/persist-test", 300)
        
        # 使用第一个实例添加项目
        analyzer1.deduplicator.add_analyzed_project(test_project)
        
        # 创建第二个分析器实例
        analyzer2 = ClaudeAgentAnalyzer()
        analyzer2.history_file = self.test_history_file
        analyzer2.deduplicator = ProjectDeduplicator(self.test_history_file)
        
        # 第二个实例应该能识别已分析的项目
        self.assertTrue(analyzer2.deduplicator.is_duplicate_project(test_project))
    
    def test_error_handling_in_integration(self):
        """测试集成过程中的错误处理"""
        # 测试无效项目数据
        invalid_project = {}
        
        # 应该不会抛出异常
        try:
            is_duplicate = self.analyzer.deduplicator.is_duplicate_project(invalid_project)
            self.assertFalse(is_duplicate)  # 无效项目应返回False
        except Exception as e:
            self.fail(f"处理无效项目数据时抛出异常: {e}")
        
        # 测试部分数据缺失的项目
        partial_project = {
            "id": 999,
            "name": "partial-project"
            # 缺少 full_name 和 html_url
        }
        
        try:
            self.analyzer.deduplicator.add_analyzed_project(partial_project)
            is_duplicate = self.analyzer.deduplicator.is_duplicate_project(partial_project)
            self.assertTrue(is_duplicate)
        except Exception as e:
            self.fail(f"处理部分数据项目时抛出异常: {e}")
    
    def test_performance_with_large_dataset(self):
        """测试大数据集性能"""
        import time
        
        # 生成100个测试项目
        large_dataset = []
        for i in range(100):
            project = self.create_mock_project(f"project-{i}", f"user{i}/project-{i}", i * 10)
            large_dataset.append(project)
            self.analyzer.deduplicator.add_analyzed_project(project)
        
        # 测试查询性能
        start_time = time.time()
        
        for project in large_dataset[:50]:  # 测试50次查询
            self.analyzer.deduplicator.is_duplicate_project(project)
        
        end_time = time.time()
        avg_query_time = (end_time - start_time) / 50
        
        # 每次查询应在合理时间内完成（10ms以内）
        self.assertLess(avg_query_time, 0.01, f"平均查询时间 {avg_query_time:.4f}s 过长")
        
        # 验证数据正确性
        stats = self.analyzer.deduplicator.get_project_statistics()
        self.assertEqual(stats['total_projects'], 100)


class TestDataMigrationIntegration(unittest.TestCase):
    """数据迁移集成测试类"""
    
    def setUp(self):
        """迁移测试前置准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'migration_test.json')
    
    def tearDown(self):
        """迁移测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_v1_to_v2_migration_integration(self):
        """测试v1到v2数据迁移集成"""
        from migrate_data import DataMigrator
        
        # 创建v1格式数据
        v1_data = {
            "last_updated": "2025-08-23T16:05:41.388501",
            "total_projects": 3,
            "analyzed_projects": [
                "anthropics/claude-code",
                "browser-use/browser-use",
                "google-gemini/gemini-cli"
            ]
        }
        
        # 写入v1格式文件
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump(v1_data, f)
        
        # 执行迁移
        migrator = DataMigrator(self.test_file)
        success = migrator.run_migration()
        self.assertTrue(success)
        
        # 验证迁移后可以使用ProjectDeduplicator
        deduplicator = ProjectDeduplicator(self.test_file)
        
        # 验证已迁移的项目
        test_project = {
            "full_name": "anthropics/claude-code",
            "html_url": "https://github.com/anthropics/claude-code"
        }
        
        self.assertTrue(deduplicator.is_duplicate_project(test_project))
        
        # 验证统计信息
        stats = deduplicator.get_project_statistics()
        self.assertEqual(stats['total_projects'], 3)


if __name__ == '__main__':
    # 运行集成测试
    print("🚀 运行项目去重优化集成测试...")
    print("=" * 60)
    
    # 设置测试环境
    os.environ['TESTING'] = '1'
    
    # 运行测试
    unittest.main(verbosity=2)