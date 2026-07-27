#!/usr/bin/env python3
"""
GitHub工作流验证脚本
GitHot - GitHub热门项目评测

检查GitHub Actions工作流文件的语法和配置正确性
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re


class WorkflowValidator:
    """GitHub工作流验证器"""
    
    def __init__(self, workflows_dir: str = None):
        """
        初始化验证器
        
        Args:
            workflows_dir: 工作流目录路径
        """
        self.script_dir = Path(__file__).parent
        self.repo_root = self.script_dir.parent
        self.workflows_dir = Path(workflows_dir) if workflows_dir else self.repo_root / '.github' / 'workflows'
        
        self.validation_results = []
        self.issues = []
        self.warnings = []
    
    def validate_all_workflows(self) -> Dict[str, Any]:
        """验证所有工作流文件"""
        print(f"🔍 开始验证工作流文件 - 目录: {self.workflows_dir}")
        
        if not self.workflows_dir.exists():
            self.issues.append(f"工作流目录不存在: {self.workflows_dir}")
            return self._create_summary()
        
        # 查找所有YAML文件
        workflow_files = list(self.workflows_dir.glob('*.yml')) + list(self.workflows_dir.glob('*.yaml'))
        
        if not workflow_files:
            self.warnings.append("未找到任何工作流文件")
            return self._create_summary()
        
        print(f"找到 {len(workflow_files)} 个工作流文件")
        
        # 验证每个文件
        for workflow_file in workflow_files:
            self._validate_single_workflow(workflow_file)
        
        return self._create_summary()
    
    def _validate_single_workflow(self, file_path: Path):
        """验证单个工作流文件"""
        print(f"\n📄 验证文件: {file_path.name}")
        
        result = {
            'file': file_path.name,
            'path': str(file_path),
            'valid_yaml': False,
            'valid_structure': False,
            'issues': [],
            'warnings': [],
            'summary': {}
        }
        
        try:
            # 读取并解析YAML
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                workflow_data = yaml.safe_load(content)
            
            result['valid_yaml'] = True
            print("  ✅ YAML语法有效")
            
            # 验证工作流结构
            self._validate_workflow_structure(workflow_data, result)
            
            # 验证具体配置
            self._validate_workflow_config(workflow_data, result)
            
            # 验证引用的脚本
            self._validate_referenced_scripts(workflow_data, result)
            
        except yaml.YAMLError as e:
            result['issues'].append(f"YAML语法错误: {e}")
            print(f"  ❌ YAML语法错误: {e}")
        except Exception as e:
            result['issues'].append(f"读取文件失败: {e}")
            print(f"  ❌ 文件读取失败: {e}")
        
        self.validation_results.append(result)
    
    def _validate_workflow_structure(self, workflow: Dict[str, Any], result: Dict[str, Any]):
        """验证工作流基本结构"""
        # YAML解析器会将'on'解析为True（布尔值），需要特殊处理
        has_name = 'name' in workflow
        has_on = 'on' in workflow or True in workflow  # 'on' 可能被解析为布尔值
        has_jobs = 'jobs' in workflow
        
        if not has_name:
            result['issues'].append("缺少必需字段: name")
            return
        if not has_on:
            result['issues'].append("缺少必需字段: on")
            return
        if not has_jobs:
            result['issues'].append("缺少必需字段: jobs")
            return
        
        result['valid_structure'] = True
        # 获取'on'配置（可能被解析为True）
        on_config = workflow.get('on', workflow.get(True, {}))
        
        result['summary'] = {
            'name': workflow.get('name'),
            'triggers': self._extract_triggers(on_config),
            'jobs_count': len(workflow.get('jobs', {})),
            'job_names': list(workflow.get('jobs', {}).keys())
        }
        
        print(f"  ✅ 工作流结构有效")
        print(f"    - 名称: {result['summary']['name']}")
        print(f"    - 触发条件: {', '.join(result['summary']['triggers'])}")
        print(f"    - 作业数量: {result['summary']['jobs_count']}")
    
    def _extract_triggers(self, on_config: Any) -> List[str]:
        """提取触发条件"""
        triggers = []
        
        if isinstance(on_config, dict):
            for key in on_config.keys():
                if key == 'schedule':
                    cron_jobs = on_config[key]
                    if isinstance(cron_jobs, list):
                        for job in cron_jobs:
                            if isinstance(job, dict) and 'cron' in job:
                                triggers.append(f"schedule({job['cron']})")
                elif key == 'push':
                    triggers.append('push')
                elif key == 'pull_request':
                    triggers.append('pull_request')
                elif key == 'workflow_dispatch':
                    triggers.append('manual')
                else:
                    triggers.append(key)
        elif isinstance(on_config, str):
            triggers.append(on_config)
        
        return triggers
    
    def _validate_workflow_config(self, workflow: Dict[str, Any], result: Dict[str, Any]):
        """验证工作流配置"""
        jobs = workflow.get('jobs', {})
        
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                result['issues'].append(f"作业 {job_name} 配置格式错误")
                continue
            
            # 检查必需字段
            if 'runs-on' not in job_config:
                result['issues'].append(f"作业 {job_name} 缺少 runs-on 字段")
            
            # 检查步骤
            steps = job_config.get('steps', [])
            if not steps:
                result['warnings'].append(f"作业 {job_name} 没有定义步骤")
            else:
                self._validate_job_steps(job_name, steps, result)
            
            # 检查权限设置
            permissions = job_config.get('permissions')
            if permissions:
                self._validate_permissions(job_name, permissions, result)
    
    def _validate_job_steps(self, job_name: str, steps: List[Dict[str, Any]], result: Dict[str, Any]):
        """验证作业步骤"""
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                result['issues'].append(f"作业 {job_name} 的步骤 {i+1} 格式错误")
                continue
            
            # 检查步骤名称
            if 'name' not in step:
                result['warnings'].append(f"作业 {job_name} 的步骤 {i+1} 缺少名称")
            
            # 检查动作或运行命令
            if 'uses' not in step and 'run' not in step:
                result['issues'].append(f"作业 {job_name} 的步骤 {i+1} 缺少 uses 或 run 字段")
    
    def _validate_permissions(self, job_name: str, permissions: Any, result: Dict[str, Any]):
        """验证权限设置"""
        if isinstance(permissions, dict):
            for perm, value in permissions.items():
                if value not in ['read', 'write', 'none']:
                    result['warnings'].append(f"作业 {job_name} 的权限 {perm} 值可能无效: {value}")
    
    def _validate_referenced_scripts(self, workflow: Dict[str, Any], result: Dict[str, Any]):
        """验证引用的脚本文件"""
        jobs = workflow.get('jobs', {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            
            for step in steps:
                if 'run' in step:
                    run_command = step['run']
                    self._check_script_references(job_name, step.get('name', 'unnamed'), run_command, result)
    
    def _check_script_references(self, job_name: str, step_name: str, run_command: str, result: Dict[str, Any]):
        """检查运行命令中引用的脚本"""
        # 查找Python脚本引用
        python_scripts = re.findall(r'python\s+scripts/([^\s]+\.py)', run_command)
        
        for script in python_scripts:
            script_path = self.repo_root / 'scripts' / script
            if not script_path.exists():
                result['issues'].append(f"作业 {job_name} 步骤 '{step_name}' 引用的脚本不存在: scripts/{script}")
            else:
                print(f"    ✅ 找到引用脚本: scripts/{script}")
    
    def test_python_scripts(self) -> Dict[str, Any]:
        """测试工作流中引用的Python脚本"""
        print(f"\n🐍 测试Python脚本功能...")
        
        script_results = {}
        
        # 测试主要脚本
        scripts_to_test = [
            ('check-syntax.py', self._test_syntax_checker),
            ('crypto-project-analyzer.py', self._test_crypto_analyzer),
            ('claude_prompts_analyzer.py', self._test_prompts_analyzer)
        ]
        
        for script_name, test_func in scripts_to_test:
            script_path = self.repo_root / 'scripts' / script_name
            print(f"\n📄 测试脚本: {script_name}")
            
            if not script_path.exists():
                script_results[script_name] = {
                    'exists': False,
                    'error': f"脚本文件不存在: {script_path}"
                }
                print(f"  ❌ 文件不存在")
                continue
            
            try:
                result = test_func(script_path)
                script_results[script_name] = result
            except Exception as e:
                script_results[script_name] = {
                    'exists': True,
                    'error': str(e)
                }
                print(f"  ❌ 测试失败: {e}")
        
        return script_results
    
    def _test_syntax_checker(self, script_path: Path) -> Dict[str, Any]:
        """测试语法检查器"""
        import subprocess
        
        try:
            # 只做语法检查，不实际运行
            result = subprocess.run([
                'python', '-m', 'py_compile', str(script_path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("  ✅ 语法检查通过")
                return {'exists': True, 'syntax_valid': True}
            else:
                print(f"  ❌ 语法错误: {result.stderr}")
                return {'exists': True, 'syntax_valid': False, 'error': result.stderr}
                
        except subprocess.TimeoutExpired:
            return {'exists': True, 'syntax_valid': False, 'error': 'Timeout during syntax check'}
    
    def _test_crypto_analyzer(self, script_path: Path) -> Dict[str, Any]:
        """测试加密项目分析器"""
        return self._test_script_import(script_path, 'crypto-project-analyzer')
    
    def _test_prompts_analyzer(self, script_path: Path) -> Dict[str, Any]:
        """测试提示词分析器"""
        return self._test_script_import(script_path, 'claude_prompts_analyzer')
    
    def _test_script_import(self, script_path: Path, module_name: str) -> Dict[str, Any]:
        """测试脚本导入和基本结构"""
        import subprocess
        import sys
        
        try:
            # 测试脚本导入
            test_code = f'''
import sys
sys.path.insert(0, "{self.repo_root / 'scripts'}")

try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("{module_name}", "{script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print("IMPORT_SUCCESS")
    
    # 检查是否有main函数
    if hasattr(module, 'main'):
        print("HAS_MAIN")
    else:
        print("NO_MAIN")
        
except Exception as e:
    print(f"IMPORT_ERROR: {{e}}")
'''
            
            result = subprocess.run([
                sys.executable, '-c', test_code
            ], capture_output=True, text=True, timeout=30)
            
            output = result.stdout.strip()
            
            if 'IMPORT_SUCCESS' in output:
                has_main = 'HAS_MAIN' in output
                print(f"  ✅ 导入成功 {'(有main函数)' if has_main else '(无main函数)'}")
                return {
                    'exists': True,
                    'importable': True,
                    'has_main': has_main,
                    'syntax_valid': True
                }
            else:
                error_info = output if output else result.stderr
                print(f"  ❌ 导入失败: {error_info}")
                return {
                    'exists': True,
                    'importable': False,
                    'error': error_info
                }
                
        except subprocess.TimeoutExpired:
            return {'exists': True, 'importable': False, 'error': 'Import test timeout'}
        except Exception as e:
            return {'exists': True, 'importable': False, 'error': str(e)}
    
    def simulate_workflow_execution(self) -> Dict[str, Any]:
        """模拟工作流执行环境"""
        print(f"\n🎭 模拟工作流执行环境...")
        
        simulation_results = {}
        
        # 检查环境变量
        env_check = self._check_environment_variables()
        simulation_results['environment'] = env_check
        
        # 检查依赖项
        deps_check = self._check_dependencies()
        simulation_results['dependencies'] = deps_check
        
        # 检查文件结构
        structure_check = self._check_file_structure()
        simulation_results['file_structure'] = structure_check
        
        # 测试关键命令
        commands_check = self._test_key_commands()
        simulation_results['commands'] = commands_check
        
        return simulation_results
    
    def _check_environment_variables(self) -> Dict[str, Any]:
        """检查环境变量"""
        print("  📋 检查环境变量...")
        
        required_vars = ['GITHUB_TOKEN', 'GITHUB_ACTIONS']
        optional_vars = ['DAYS_BACK', 'MAX_PROJECTS']
        
        env_status = {
            'required': {},
            'optional': {},
            'all_required_present': True
        }
        
        for var in required_vars:
            is_set = var in os.environ
            env_status['required'][var] = is_set
            if not is_set:
                env_status['all_required_present'] = False
                print(f"    ⚠️  缺少必需环境变量: {var}")
            else:
                print(f"    ✅ 找到环境变量: {var}")
        
        for var in optional_vars:
            env_status['optional'][var] = var in os.environ
            if var in os.environ:
                print(f"    ✅ 找到可选环境变量: {var}")
        
        return env_status
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """检查Python依赖"""
        print("  📦 检查Python依赖...")
        
        requirements_file = self.repo_root / 'scripts' / 'requirements.txt'
        deps_status = {'requirements_file_exists': False, 'dependencies': {}}
        
        if not requirements_file.exists():
            print(f"    ❌ requirements.txt 文件不存在")
            return deps_status
        
        deps_status['requirements_file_exists'] = True
        
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                requirements = f.read().strip()
            
            # 提取包名
            import re
            packages = []
            for line in requirements.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # 提取包名（去掉版本要求）
                    match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                    if match:
                        packages.append(match.group(1))
            
            # 检查每个包是否可导入
            for package in packages:
                try:
                    __import__(package)
                    deps_status['dependencies'][package] = True
                    print(f"    ✅ {package} - 已安装")
                except ImportError:
                    deps_status['dependencies'][package] = False
                    print(f"    ❌ {package} - 未安装")
                    
        except Exception as e:
            print(f"    ❌ 读取requirements.txt失败: {e}")
        
        return deps_status
    
    def _check_file_structure(self) -> Dict[str, Any]:
        """检查文件结构"""
        print("  📁 检查文件结构...")
        
        required_paths = [
            'scripts/',
            'content/',
            'content/posts/',
            'data/',
            'themes/',
            'hugo.toml'
        ]
        
        structure_status = {}
        all_present = True
        
        for path in required_paths:
            full_path = self.repo_root / path
            exists = full_path.exists()
            structure_status[path] = exists
            
            if exists:
                print(f"    ✅ {path}")
            else:
                print(f"    ❌ {path} - 不存在")
                all_present = False
        
        structure_status['all_required_present'] = all_present
        return structure_status
    
    def _test_key_commands(self) -> Dict[str, Any]:
        """测试关键命令"""
        print("  🔧 测试关键命令...")
        
        commands = {
            'python': ['python', '--version'],
            'hugo': ['hugo', 'version'],
            'git': ['git', '--version']
        }
        
        command_results = {}
        
        for name, cmd in commands.items():
            try:
                import subprocess
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    command_results[name] = {'available': True, 'version': version}
                    print(f"    ✅ {name}: {version}")
                else:
                    command_results[name] = {'available': False, 'error': result.stderr.strip()}
                    print(f"    ❌ {name}: {result.stderr.strip()}")
                    
            except subprocess.TimeoutExpired:
                command_results[name] = {'available': False, 'error': 'Timeout'}
                print(f"    ❌ {name}: 超时")
            except FileNotFoundError:
                command_results[name] = {'available': False, 'error': 'Command not found'}
                print(f"    ❌ {name}: 命令未找到")
            except Exception as e:
                command_results[name] = {'available': False, 'error': str(e)}
                print(f"    ❌ {name}: {e}")
        
        return command_results
    
    def _create_summary(self) -> Dict[str, Any]:
        """创建验证摘要"""
        total_files = len(self.validation_results)
        valid_files = sum(1 for r in self.validation_results if r['valid_yaml'] and r['valid_structure'])
        total_issues = sum(len(r['issues']) for r in self.validation_results)
        total_warnings = sum(len(r['warnings']) for r in self.validation_results)
        
        return {
            'summary': {
                'total_files': total_files,
                'valid_files': valid_files,
                'total_issues': total_issues,
                'total_warnings': total_warnings,
                'success_rate': (valid_files / total_files * 100) if total_files > 0 else 0
            },
            'files': self.validation_results,
            'global_issues': self.issues,
            'global_warnings': self.warnings
        }
    
    def generate_report(self, output_file: str = None) -> str:
        """生成测试报告"""
        # 执行所有测试
        workflow_validation = self.validate_all_workflows()
        script_tests = self.test_python_scripts()
        simulation = self.simulate_workflow_execution()
        
        # 生成报告
        report_lines = []
        
        # 标题
        report_lines.append("GitHub 工作流全面测试报告")
        report_lines.append("=" * 50)
        report_lines.append(f"测试时间: {os.popen('date').read().strip()}")
        report_lines.append(f"测试目录: {self.workflows_dir}")
        report_lines.append("")
        
        # 工作流验证结果
        report_lines.append("📋 工作流文件验证")
        report_lines.append("-" * 30)
        summary = workflow_validation['summary']
        report_lines.append(f"总文件数: {summary['total_files']}")
        report_lines.append(f"有效文件: {summary['valid_files']}")
        report_lines.append(f"成功率: {summary['success_rate']:.1f}%")
        report_lines.append(f"问题总数: {summary['total_issues']}")
        report_lines.append(f"警告总数: {summary['total_warnings']}")
        report_lines.append("")
        
        # 详细文件信息
        for file_result in workflow_validation['files']:
            status = "✅" if file_result['valid_yaml'] and file_result['valid_structure'] else "❌"
            report_lines.append(f"{status} {file_result['file']}")
            
            if file_result['summary']:
                s = file_result['summary']
                report_lines.append(f"  名称: {s['name']}")
                report_lines.append(f"  触发: {', '.join(s['triggers'])}")
                report_lines.append(f"  作业: {s['jobs_count']} 个")
            
            if file_result['issues']:
                for issue in file_result['issues']:
                    report_lines.append(f"  ❌ {issue}")
            
            if file_result['warnings']:
                for warning in file_result['warnings']:
                    report_lines.append(f"  ⚠️  {warning}")
            
            report_lines.append("")
        
        # Python脚本测试结果
        report_lines.append("🐍 Python脚本测试")
        report_lines.append("-" * 30)
        
        for script_name, result in script_tests.items():
            if result.get('exists', False):
                if result.get('syntax_valid', False) and result.get('importable', True):
                    status = "✅"
                else:
                    status = "❌"
            else:
                status = "❌"
            
            report_lines.append(f"{status} {script_name}")
            
            if 'error' in result:
                report_lines.append(f"  错误: {result['error']}")
            elif result.get('importable', False):
                report_lines.append(f"  导入: 成功")
                if result.get('has_main', False):
                    report_lines.append(f"  main函数: 存在")
            
        report_lines.append("")
        
        # 环境模拟结果
        report_lines.append("🎭 环境模拟测试")
        report_lines.append("-" * 30)
        
        # 环境变量
        env_result = simulation['environment']
        missing_required = [var for var, present in env_result['required'].items() if not present]
        if missing_required:
            report_lines.append(f"❌ 缺少必需环境变量: {', '.join(missing_required)}")
        else:
            report_lines.append("✅ 所有必需环境变量已设置")
        
        # 依赖项
        deps_result = simulation['dependencies']
        if deps_result['requirements_file_exists']:
            missing_deps = [pkg for pkg, installed in deps_result['dependencies'].items() if not installed]
            if missing_deps:
                report_lines.append(f"❌ 缺少Python依赖: {', '.join(missing_deps)}")
            else:
                report_lines.append("✅ 所有Python依赖已安装")
        else:
            report_lines.append("❌ requirements.txt 文件不存在")
        
        # 文件结构
        structure_result = simulation['file_structure']
        if structure_result['all_required_present']:
            report_lines.append("✅ 文件结构完整")
        else:
            missing_paths = [path for path, exists in structure_result.items() if not exists and path != 'all_required_present']
            report_lines.append(f"❌ 缺少文件/目录: {', '.join(missing_paths)}")
        
        # 命令可用性
        commands_result = simulation['commands']
        unavailable_commands = [name for name, result in commands_result.items() if not result['available']]
        if unavailable_commands:
            report_lines.append(f"❌ 命令不可用: {', '.join(unavailable_commands)}")
        else:
            report_lines.append("✅ 所有必需命令可用")
        
        report_lines.append("")
        
        # 总体评估
        report_lines.append("📊 总体评估")
        report_lines.append("-" * 30)
        
        total_checks = 4  # 工作流、脚本、环境、命令
        passed_checks = 0
        
        if summary['success_rate'] >= 100:
            passed_checks += 1
        
        if all(r.get('exists', False) and r.get('syntax_valid', False) for r in script_tests.values()):
            passed_checks += 1
        
        if env_result['all_required_present']:
            passed_checks += 1
        
        if not unavailable_commands:
            passed_checks += 1
        
        overall_score = (passed_checks / total_checks) * 100
        
        if overall_score >= 90:
            grade = "🌟 优秀"
        elif overall_score >= 70:
            grade = "✅ 良好"
        elif overall_score >= 50:
            grade = "⚠️  一般"
        else:
            grade = "❌ 需要改进"
        
        report_lines.append(f"整体评分: {overall_score:.1f}% - {grade}")
        report_lines.append(f"通过检查: {passed_checks}/{total_checks}")
        
        report_content = "\n".join(report_lines)
        
        # 保存报告
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"\n📄 报告已保存到: {output_file}")
            except Exception as e:
                print(f"\n❌ 保存报告失败: {e}")
        
        return report_content


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub工作流验证工具')
    parser.add_argument('--workflows-dir', help='工作流目录路径')
    parser.add_argument('--output', help='输出报告文件路径')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    
    args = parser.parse_args()
    
    # 创建验证器
    validator = WorkflowValidator(args.workflows_dir)
    
    # 生成报告
    if args.format == 'json':
        # JSON格式输出
        workflow_validation = validator.validate_all_workflows()
        script_tests = validator.test_python_scripts()
        simulation = validator.simulate_workflow_execution()
        
        json_result = {
            'workflow_validation': workflow_validation,
            'script_tests': script_tests,
            'simulation': simulation
        }
        
        output = json.dumps(json_result, ensure_ascii=False, indent=2)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)
    else:
        # 文本格式输出
        report = validator.generate_report(args.output)
        if not args.output:
            print(report)


if __name__ == "__main__":
    main()

import requests
import json
import os
from datetime import datetime, timedelta

def check_workflow_status():
    """检查GitHub Actions工作流状态"""
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("⚠️  未设置GITHUB_TOKEN环境变量")
        return
    
    # 这里需要替换为实际的仓库信息
    owner = "your-username"  # 替换为实际用户名
    repo = "smartwallex-hugo"  # 替换为实际仓库名
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print("🔍 检查GitHub Actions工作流状态...")
    print("=" * 50)
    
    # 获取工作流列表
    workflows_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows"
    
    try:
        response = requests.get(workflows_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ 获取工作流列表失败: {response.status_code}")
            return
        
        workflows = response.json()['workflows']
        
        for workflow in workflows:
            workflow_name = workflow['name']
            workflow_id = workflow['id']
            state = workflow['state']
            
            print(f"\n📋 工作流: {workflow_name}")
            print(f"   状态: {'✅ 活跃' if state == 'active' else '❌ 非活跃'}")
            
            # 获取最近的运行记录
            runs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
            runs_response = requests.get(f"{runs_url}?per_page=5", headers=headers)
            
            if runs_response.status_code == 200:
                runs = runs_response.json()['workflow_runs']
                
                if runs:
                    latest_run = runs[0]
                    status = latest_run['status']
                    conclusion = latest_run['conclusion']
                    created_at = datetime.fromisoformat(latest_run['created_at'].replace('Z', '+00:00'))
                    
                    print(f"   最近运行: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   运行状态: {get_status_emoji(status, conclusion)} {status}")
                    if conclusion:
                        print(f"   运行结果: {get_conclusion_emoji(conclusion)} {conclusion}")
                    
                    # 显示最近5次运行的统计
                    success_count = sum(1 for run in runs if run['conclusion'] == 'success')
                    failure_count = sum(1 for run in runs if run['conclusion'] == 'failure')
                    
                    print(f"   最近5次: ✅ {success_count} 成功, ❌ {failure_count} 失败")
                else:
                    print("   最近运行: 无运行记录")
            else:
                print(f"   ⚠️  获取运行记录失败: {runs_response.status_code}")
    
    except Exception as e:
        print(f"❌ 检查失败: {e}")

def get_status_emoji(status, conclusion):
    """获取状态表情符号"""
    if status == 'completed':
        if conclusion == 'success':
            return '✅'
        elif conclusion == 'failure':
            return '❌'
        elif conclusion == 'cancelled':
            return '⏹️'
        else:
            return '⚠️'
    elif status == 'in_progress':
        return '🔄'
    elif status == 'queued':
        return '⏳'
    else:
        return '❓'

def get_conclusion_emoji(conclusion):
    """获取结论表情符号"""
    emoji_map = {
        'success': '✅',
        'failure': '❌',
        'cancelled': '⏹️',
        'skipped': '⏭️',
        'timed_out': '⏰',
        'action_required': '🔔'
    }
    return emoji_map.get(conclusion, '❓')

def show_usage():
    """显示使用说明"""
    print("📋 GitHub Actions 工作流状态检查工具")
    print("=" * 50)
    print("使用方法:")
    print("1. 设置环境变量: export GITHUB_TOKEN=your_token")
    print("2. 修改脚本中的owner和repo变量")
    print("3. 运行: python scripts/check-workflows.py")
    print()
    print("功能:")
    print("- 检查所有工作流的状态")
    print("- 显示最近的运行记录")
    print("- 统计成功/失败次数")

if __name__ == "__main__":
    if not os.getenv('GITHUB_TOKEN'):
        show_usage()
    else:
        check_workflow_status()