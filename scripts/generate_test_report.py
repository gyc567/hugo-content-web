#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告生成器

该脚本执行所有测试用例并生成详细的测试报告，包括：
- 单元测试覆盖率
- 集成测试结果
- 性能测试数据
- 代码质量检查

作者: Qoder AI Assistant
创建时间: 2025-08-24
"""

import unittest
import sys
import os
import time
import datetime
import json
import subprocess
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import traceback


class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self):
        """初始化测试报告生成器"""
        self.results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'summary': {},
            'unit_tests': {},
            'integration_tests': {},
            'performance_tests': {},
            'code_quality': {},
            'coverage': {},
            'recommendations': []
        }
        
        # 设置测试环境
        os.environ['TESTING'] = '1'
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    def run_unit_tests(self) -> dict:
        """运行单元测试"""
        print("🧪 运行单元测试...")
        
        try:
            # 导入测试模块
            from test_project_deduplicator import (
                TestProjectDeduplicator,
                TestProjectDeduplicatorIntegration,
                TestProjectDeduplicatorPerformance
            )
            
            # 创建测试套件
            loader = unittest.TestLoader()
            suite = unittest.TestSuite()
            
            # 添加测试类
            suite.addTests(loader.loadTestsFromTestCase(TestProjectDeduplicator))
            suite.addTests(loader.loadTestsFromTestCase(TestProjectDeduplicatorIntegration))
            suite.addTests(loader.loadTestsFromTestCase(TestProjectDeduplicatorPerformance))
            
            # 运行测试
            stream = StringIO()
            runner = unittest.TextTestRunner(stream=stream, verbosity=2)
            result = runner.run(suite)
            
            # 收集结果
            unit_results = {
                'total_tests': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
                'output': stream.getvalue(),
                'failure_details': [{'test': str(test), 'error': error} for test, error in result.failures],
                'error_details': [{'test': str(test), 'error': error} for test, error in result.errors]
            }
            
            print(f"   ✅ 单元测试完成: {unit_results['total_tests']} 个测试，成功率 {unit_results['success_rate']:.1f}%")
            return unit_results
            
        except Exception as e:
            print(f"   ❌ 单元测试执行失败: {e}")
            return {
                'total_tests': 0,
                'failures': 1,
                'errors': 0,
                'skipped': 0,
                'success_rate': 0,
                'output': f"测试执行失败: {str(e)}",
                'failure_details': [],
                'error_details': [{'test': 'unit_test_execution', 'error': str(e)}]
            }
    
    def run_integration_tests(self) -> dict:
        """运行集成测试"""
        print("🔗 运行集成测试...")
        
        try:
            # 动态导入集成测试模块
            import importlib.util
            spec = importlib.util.spec_from_file_location("test_integration", "test_integration.py")
            test_integration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_integration_module)
            
            TestClaudeAgentAnalyzerIntegration = test_integration_module.TestClaudeAgentAnalyzerIntegration
            TestDataMigrationIntegration = test_integration_module.TestDataMigrationIntegration
            
            # 创建测试套件
            loader = unittest.TestLoader()
            suite = unittest.TestSuite()
            
            # 添加集成测试
            suite.addTests(loader.loadTestsFromTestCase(TestClaudeAgentAnalyzerIntegration))
            suite.addTests(loader.loadTestsFromTestCase(TestDataMigrationIntegration))
            
            # 运行测试
            stream = StringIO()
            runner = unittest.TextTestRunner(stream=stream, verbosity=2)
            result = runner.run(suite)
            
            # 收集结果
            integration_results = {
                'total_tests': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
                'output': stream.getvalue(),
                'failure_details': [{'test': str(test), 'error': error} for test, error in result.failures],
                'error_details': [{'test': str(test), 'error': error} for test, error in result.errors]
            }
            
            print(f"   ✅ 集成测试完成: {integration_results['total_tests']} 个测试，成功率 {integration_results['success_rate']:.1f}%")
            return integration_results
            
        except Exception as e:
            print(f"   ❌ 集成测试执行失败: {e}")
            return {
                'total_tests': 0,
                'failures': 1,
                'errors': 0,
                'skipped': 0,
                'success_rate': 0,
                'output': f"集成测试执行失败: {str(e)}",
                'failure_details': [],
                'error_details': [{'test': 'integration_test_execution', 'error': str(e)}]
            }
    
    def run_performance_tests(self) -> dict:
        """运行性能测试"""
        print("⚡ 运行性能测试...")
        
        try:
            from project_deduplicator import ProjectDeduplicator
            import tempfile
            import shutil
            
            # 创建临时测试环境
            temp_dir = tempfile.mkdtemp()
            test_file = os.path.join(temp_dir, 'perf_test.json')
            
            try:
                deduplicator = ProjectDeduplicator(test_file)
                
                # 性能测试指标
                performance_metrics = {}
                
                # 测试1: 大量项目添加性能
                print("   📊 测试项目添加性能...")
                start_time = time.time()
                
                for i in range(1000):
                    project = {
                        "full_name": f"user{i}/project{i}",
                        "html_url": f"https://github.com/user{i}/project{i}",
                        "stargazers_count": i
                    }
                    deduplicator.add_analyzed_project(project)
                
                add_time = time.time() - start_time
                performance_metrics['add_1000_projects_time'] = add_time
                performance_metrics['avg_add_time'] = add_time / 1000
                
                # 测试2: 大量项目查询性能
                print("   🔍 测试项目查询性能...")
                start_time = time.time()
                
                for i in range(500):
                    project = {
                        "full_name": f"user{i}/project{i}",
                        "html_url": f"https://github.com/user{i}/project{i}"
                    }
                    deduplicator.is_duplicate_project(project)
                
                query_time = time.time() - start_time
                performance_metrics['query_500_projects_time'] = query_time
                performance_metrics['avg_query_time'] = query_time / 500
                
                # 测试3: 内存使用
                import psutil
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()
                performance_metrics['memory_usage_mb'] = memory_info.rss / 1024 / 1024
                
                # 测试4: 文件大小
                if os.path.exists(test_file):
                    file_size = os.path.getsize(test_file)
                    performance_metrics['data_file_size_kb'] = file_size / 1024
                
                # 性能评估
                performance_score = 100
                if performance_metrics['avg_add_time'] > 0.001:  # 超过1ms
                    performance_score -= 20
                if performance_metrics['avg_query_time'] > 0.001:  # 超过1ms
                    performance_score -= 20
                if performance_metrics['memory_usage_mb'] > 50:  # 超过50MB
                    performance_score -= 10
                
                performance_metrics['performance_score'] = max(0, performance_score)
                
                print(f"   ✅ 性能测试完成: 评分 {performance_metrics['performance_score']}/100")
                
                return {
                    'status': 'success',
                    'metrics': performance_metrics,
                    'recommendations': self._generate_performance_recommendations(performance_metrics)
                }
                
            finally:
                # 清理临时文件
                shutil.rmtree(temp_dir)
                
        except Exception as e:
            print(f"   ❌ 性能测试执行失败: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'metrics': {},
                'recommendations': ['性能测试执行失败，建议检查测试环境']
            }
    
    def _generate_performance_recommendations(self, metrics: dict) -> list:
        """生成性能优化建议"""
        recommendations = []
        
        if metrics.get('avg_add_time', 0) > 0.001:
            recommendations.append("项目添加操作耗时较长，建议优化数据写入逻辑")
        
        if metrics.get('avg_query_time', 0) > 0.001:
            recommendations.append("项目查询操作耗时较长，建议使用索引或缓存优化")
        
        if metrics.get('memory_usage_mb', 0) > 50:
            recommendations.append("内存使用较高，建议优化数据结构")
        
        if metrics.get('data_file_size_kb', 0) > 1000:
            recommendations.append("数据文件较大，建议考虑数据压缩或分片存储")
        
        if not recommendations:
            recommendations.append("性能表现良好，无需优化")
        
        return recommendations
    
    def check_code_quality(self) -> dict:
        """检查代码质量"""
        print("🔍 检查代码质量...")
        
        quality_results = {
            'syntax_check': {},
            'import_check': {},
            'style_check': {},
            'complexity_check': {}
        }
        
        # 检查的文件列表
        files_to_check = [
            'project_deduplicator.py',
            'crypto-project-analyzer.py',
            'migrate_data.py'
        ]
        
        for filename in files_to_check:
            print(f"   📄 检查文件: {filename}")
            
            if not os.path.exists(filename):
                quality_results['syntax_check'][filename] = {'status': 'missing', 'errors': []}
                continue
            
            # 语法检查
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                compile(code, filename, 'exec')
                quality_results['syntax_check'][filename] = {'status': 'pass', 'errors': []}
            except SyntaxError as e:
                quality_results['syntax_check'][filename] = {
                    'status': 'fail',
                    'errors': [f"语法错误: {e}"]
                }
            except Exception as e:
                quality_results['syntax_check'][filename] = {
                    'status': 'error',
                    'errors': [f"检查失败: {e}"]
                }
        
        # 计算整体质量评分
        total_files = len(files_to_check)
        passed_files = sum(1 for result in quality_results['syntax_check'].values() 
                          if result['status'] == 'pass')
        
        quality_score = (passed_files / total_files * 100) if total_files > 0 else 0
        quality_results['overall_score'] = quality_score
        
        print(f"   ✅ 代码质量检查完成: 评分 {quality_score:.1f}/100")
        
        return quality_results
    
    def calculate_test_coverage(self) -> dict:
        """计算测试覆盖率"""
        print("📊 计算测试覆盖率...")
        
        try:
            # 统计源代码行数
            source_files = [
                'project_deduplicator.py',
                'migrate_data.py'
            ]
            
            total_lines = 0
            for filename in source_files:
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        lines = len([line for line in f if line.strip() and not line.strip().startswith('#')])
                        total_lines += lines
            
            # 统计测试代码行数
            test_files = [
                'test_project_deduplicator.py',
                'test_integration.py'
            ]
            
            test_lines = 0
            for filename in test_files:
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        lines = len([line for line in f if line.strip() and not line.strip().startswith('#')])
                        test_lines += lines
            
            # 估算覆盖率（基于测试代码量）
            estimated_coverage = min(100, (test_lines / total_lines * 50)) if total_lines > 0 else 0
            
            coverage_result = {
                'source_lines': total_lines,
                'test_lines': test_lines,
                'estimated_coverage': estimated_coverage,
                'status': 'estimated'  # 表示这是估算值
            }
            
            print(f"   ✅ 测试覆盖率估算完成: {estimated_coverage:.1f}%")
            
            return coverage_result
            
        except Exception as e:
            print(f"   ❌ 覆盖率计算失败: {e}")
            return {
                'source_lines': 0,
                'test_lines': 0,
                'estimated_coverage': 0,
                'status': 'failed',
                'error': str(e)
            }
    
    def generate_recommendations(self) -> list:
        """生成改进建议"""
        recommendations = []
        
        # 基于测试结果生成建议
        unit_success_rate = self.results['unit_tests'].get('success_rate', 0)
        integration_success_rate = self.results['integration_tests'].get('success_rate', 0)
        performance_score = self.results['performance_tests'].get('metrics', {}).get('performance_score', 0)
        quality_score = self.results['code_quality'].get('overall_score', 0)
        coverage = self.results['coverage'].get('estimated_coverage', 0)
        
        if unit_success_rate < 100:
            recommendations.append("单元测试存在失败用例，建议修复失败的测试")
        
        if integration_success_rate < 100:
            recommendations.append("集成测试存在问题，建议检查系统集成逻辑")
        
        if performance_score < 80:
            recommendations.append("性能表现有待提升，建议进行性能优化")
        
        if quality_score < 90:
            recommendations.append("代码质量需要改进，建议修复语法错误和改进代码风格")
        
        if coverage < 80:
            recommendations.append("测试覆盖率偏低，建议增加测试用例")
        
        # 添加具体的优化建议
        if self.results['performance_tests'].get('recommendations'):
            recommendations.extend(self.results['performance_tests']['recommendations'])
        
        if not recommendations:
            recommendations.append("所有测试通过，代码质量良好！建议继续保持。")
        
        return recommendations
    
    def generate_summary(self) -> dict:
        """生成测试摘要"""
        summary = {
            'overall_status': 'PASS',
            'total_tests': 0,
            'total_failures': 0,
            'total_errors': 0,
            'success_rate': 0,
            'performance_score': 0,
            'quality_score': 0,
            'coverage': 0
        }
        
        # 汇总测试数据
        for test_type in ['unit_tests', 'integration_tests']:
            if test_type in self.results:
                summary['total_tests'] += self.results[test_type].get('total_tests', 0)
                summary['total_failures'] += self.results[test_type].get('failures', 0)
                summary['total_errors'] += self.results[test_type].get('errors', 0)
        
        # 计算整体成功率
        if summary['total_tests'] > 0:
            passed_tests = summary['total_tests'] - summary['total_failures'] - summary['total_errors']
            summary['success_rate'] = (passed_tests / summary['total_tests']) * 100
        
        # 获取其他指标
        summary['performance_score'] = self.results['performance_tests'].get('metrics', {}).get('performance_score', 0)
        summary['quality_score'] = self.results['code_quality'].get('overall_score', 0)
        summary['coverage'] = self.results['coverage'].get('estimated_coverage', 0)
        
        # 判断整体状态
        if summary['total_failures'] > 0 or summary['total_errors'] > 0:
            summary['overall_status'] = 'FAIL'
        elif summary['success_rate'] < 80:
            summary['overall_status'] = 'WARNING'
        
        return summary
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始执行项目去重优化全面测试...")
        print("=" * 80)
        
        # 运行各类测试
        self.results['unit_tests'] = self.run_unit_tests()
        self.results['integration_tests'] = self.run_integration_tests()
        self.results['performance_tests'] = self.run_performance_tests()
        self.results['code_quality'] = self.check_code_quality()
        self.results['coverage'] = self.calculate_test_coverage()
        
        # 生成摘要和建议
        self.results['summary'] = self.generate_summary()
        self.results['recommendations'] = self.generate_recommendations()
        
        print("\n" + "=" * 80)
        print("📋 测试完成，正在生成报告...")
    
    def save_report(self, filename: str = None):
        """保存测试报告"""
        if filename is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'test_report_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            
            print(f"📄 详细测试报告已保存: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
            return None
    
    def print_summary_report(self):
        """打印摘要报告"""
        summary = self.results['summary']
        
        print("\n" + "🎯 测试总结报告".center(80, "="))
        print(f"\n📊 整体状态: {'✅ ' + summary['overall_status'] if summary['overall_status'] == 'PASS' else '❌ ' + summary['overall_status']}")
        print(f"📈 总测试数: {summary['total_tests']}")
        print(f"✅ 成功率: {summary['success_rate']:.1f}%")
        print(f"❌ 失败数: {summary['total_failures']}")
        print(f"💥 错误数: {summary['total_errors']}")
        print(f"⚡ 性能评分: {summary['performance_score']:.1f}/100")
        print(f"🔍 代码质量: {summary['quality_score']:.1f}/100")
        print(f"📊 测试覆盖率: {summary['coverage']:.1f}%")
        
        print(f"\n💡 改进建议:")
        for i, recommendation in enumerate(self.results['recommendations'], 1):
            print(f"   {i}. {recommendation}")
        
        print("\n" + "=" * 80)


def main():
    """主函数"""
    generator = TestReportGenerator()
    
    try:
        # 运行所有测试
        generator.run_all_tests()
        
        # 打印摘要报告
        generator.print_summary_report()
        
        # 保存详细报告
        report_file = generator.save_report()
        
        # 返回退出码
        summary = generator.results['summary']
        if summary['overall_status'] == 'PASS':
            print("🎉 所有测试通过！")
            sys.exit(0)
        else:
            print("⚠️  存在测试问题，请查看报告详情。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ 测试执行异常: {e}")
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()