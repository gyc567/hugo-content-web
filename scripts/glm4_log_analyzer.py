#!/usr/bin/env python3
"""
GLM-4.5 日志分析工具
GitHot - GitHub热门项目评测

分析GLM-4.5 API调用日志，生成统计报告和使用分析
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import argparse


class GLM4LogAnalyzer:
    """GLM-4.5日志分析器"""
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        初始化日志分析器
        
        Args:
            log_dir: 日志目录路径
        """
        self.script_dir = Path(__file__).parent
        self.log_dir = Path(log_dir) if log_dir else self.script_dir / 'logs'
        
        # 确保日志目录存在
        self.log_dir.mkdir(exist_ok=True)
        
        # 日志文件路径
        self.main_log = self.log_dir / 'glm4_client.log'
        self.request_log = self.log_dir / 'glm4_requests.log'
        
        # 统计数据
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'models_used': {},
            'daily_usage': {},
            'hourly_usage': {},
            'average_response_time': 0,
            'token_costs': {},
            'error_types': {}
        }
    
    def analyze_logs(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        分析日志文件
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            分析结果字典
        """
        print(f"开始分析日志... 日志目录: {self.log_dir}")
        
        # 重置统计数据
        self._reset_stats()
        
        # 解析日期范围
        date_filter = self._parse_date_range(start_date, end_date)
        
        # 分析请求日志
        if self.request_log.exists():
            self._analyze_request_log(date_filter)
        else:
            print(f"请求日志文件不存在: {self.request_log}")
        
        # 分析主日志
        if self.main_log.exists():
            self._analyze_main_log(date_filter)
        else:
            print(f"主日志文件不存在: {self.main_log}")
        
        # 计算派生统计数据
        self._calculate_derived_stats()
        
        return self.stats
    
    def _reset_stats(self):
        """重置统计数据"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'models_used': {},
            'daily_usage': {},
            'hourly_usage': {},
            'average_response_time': 0,
            'token_costs': {},
            'error_types': {},
            'request_details': []
        }
    
    def _parse_date_range(self, start_date: Optional[str], end_date: Optional[str]) -> Optional[Tuple[datetime, datetime]]:
        """解析日期范围"""
        if not start_date and not end_date:
            return None
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else datetime.min
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) if end_date else datetime.max
            return (start, end)
        except ValueError as e:
            print(f"日期格式错误: {e}")
            return None
    
    def _analyze_request_log(self, date_filter: Optional[Tuple[datetime, datetime]]):
        """分析请求日志"""
        print("分析请求日志...")
        
        try:
            with open(self.request_log, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        self._process_request_log_line(line, date_filter)
                    except Exception as e:
                        print(f"处理请求日志第{line_num}行时出错: {e}")
                        
        except Exception as e:
            print(f"读取请求日志失败: {e}")
    
    def _process_request_log_line(self, line: str, date_filter: Optional[Tuple[datetime, datetime]]):
        """处理单行请求日志"""
        line = line.strip()
        if not line:
            return
        
        # 解析日志行
        parts = line.split(' | ', 2)
        if len(parts) < 3:
            return
        
        timestamp_str, log_type, content = parts
        
        # 解析时间戳
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return
        
        # 应用日期过滤器
        if date_filter:
            start_date, end_date = date_filter
            if not (start_date <= timestamp < end_date):
                return
        
        # 处理请求或响应
        if log_type == 'REQUEST':
            self._process_request_entry(timestamp, content)
        elif log_type == 'RESPONSE':
            self._process_response_entry(timestamp, content)
    
    def _process_request_entry(self, timestamp: datetime, content: str):
        """处理请求条目"""
        try:
            if content.startswith('REQUEST | '):
                json_str = content[10:]  # 去掉 'REQUEST | ' 前缀
                data = json.loads(json_str)
                
                # 记录请求信息
                self.stats['total_requests'] += 1
                
                # 按日期统计
                date_key = timestamp.strftime('%Y-%m-%d')
                self.stats['daily_usage'][date_key] = self.stats['daily_usage'].get(date_key, 0) + 1
                
                # 按小时统计
                hour_key = timestamp.strftime('%H')
                self.stats['hourly_usage'][hour_key] = self.stats['hourly_usage'].get(hour_key, 0) + 1
                
                # 模型使用统计
                model = data.get('model', 'unknown')
                self.stats['models_used'][model] = self.stats['models_used'].get(model, 0) + 1
                
        except (json.JSONDecodeError, KeyError) as e:
            # 忽略解析错误
            pass
    
    def _process_response_entry(self, timestamp: datetime, content: str):
        """处理响应条目"""
        try:
            if content.startswith('RESPONSE | '):
                json_str = content[11:]  # 去掉 'RESPONSE | ' 前缀
                data = json.loads(json_str)
                
                # 成功请求计数
                self.stats['successful_requests'] += 1
                
                # Token使用统计
                token_usage = data.get('token_usage', {})
                self.stats['input_tokens'] += token_usage.get('prompt_tokens', 0)
                self.stats['output_tokens'] += token_usage.get('completion_tokens', 0)
                self.stats['total_tokens'] += token_usage.get('total_tokens', 0)
                
                # 保存请求详情
                self.stats['request_details'].append({
                    'timestamp': timestamp.isoformat(),
                    'request_id': data.get('request_id'),
                    'model': data.get('model'),
                    'token_usage': token_usage,
                    'choices_count': data.get('choices_count', 0)
                })
                
        except (json.JSONDecodeError, KeyError):
            # 忽略解析错误
            pass
    
    def _analyze_main_log(self, date_filter: Optional[Tuple[datetime, datetime]]):
        """分析主日志"""
        print("分析主日志...")
        
        try:
            with open(self.main_log, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        self._process_main_log_line(line, date_filter)
                    except Exception as e:
                        print(f"处理主日志第{line_num}行时出错: {e}")
                        
        except Exception as e:
            print(f"读取主日志失败: {e}")
    
    def _process_main_log_line(self, line: str, date_filter: Optional[Tuple[datetime, datetime]]):
        """处理单行主日志"""
        line = line.strip()
        if not line:
            return
        
        # 解析错误日志
        if 'ERROR' in line and 'GLM-4.5 API请求失败' in line:
            self.stats['failed_requests'] += 1
            
            # 提取错误类型
            error_match = re.search(r'Error: (.+?)(?:\s|$)', line)
            if error_match:
                error_type = error_match.group(1)
                self.stats['error_types'][error_type] = self.stats['error_types'].get(error_type, 0) + 1
    
    def _calculate_derived_stats(self):
        """计算派生统计数据"""
        # 计算成功率
        if self.stats['total_requests'] > 0:
            self.stats['success_rate'] = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
        else:
            self.stats['success_rate'] = 0
        
        # 计算平均token使用
        if self.stats['successful_requests'] > 0:
            self.stats['avg_input_tokens'] = self.stats['input_tokens'] / self.stats['successful_requests']
            self.stats['avg_output_tokens'] = self.stats['output_tokens'] / self.stats['successful_requests']
            self.stats['avg_total_tokens'] = self.stats['total_tokens'] / self.stats['successful_requests']
        else:
            self.stats['avg_input_tokens'] = 0
            self.stats['avg_output_tokens'] = 0
            self.stats['avg_total_tokens'] = 0
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        生成分析报告
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            报告内容
        """
        report_lines = []
        
        # 标题
        report_lines.append("GLM-4.5 API使用分析报告")
        report_lines.append("=" * 50)
        report_lines.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # 基本统计
        report_lines.append("📊 基本统计:")
        report_lines.append(f"  总请求数: {self.stats['total_requests']:,}")
        report_lines.append(f"  成功请求: {self.stats['successful_requests']:,}")
        report_lines.append(f"  失败请求: {self.stats['failed_requests']:,}")
        report_lines.append(f"  成功率: {self.stats['success_rate']:.2f}%")
        report_lines.append("")
        
        # Token使用统计
        report_lines.append("🎯 Token使用统计:")
        report_lines.append(f"  总Token消耗: {self.stats['total_tokens']:,}")
        report_lines.append(f"  输入Token: {self.stats['input_tokens']:,}")
        report_lines.append(f"  输出Token: {self.stats['output_tokens']:,}")
        report_lines.append(f"  平均输入Token: {self.stats['avg_input_tokens']:.1f}")
        report_lines.append(f"  平均输出Token: {self.stats['avg_output_tokens']:.1f}")
        report_lines.append(f"  平均总Token: {self.stats['avg_total_tokens']:.1f}")
        report_lines.append("")
        
        # 模型使用统计
        if self.stats['models_used']:
            report_lines.append("🤖 模型使用统计:")
            for model, count in sorted(self.stats['models_used'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / self.stats['total_requests']) * 100
                report_lines.append(f"  {model}: {count:,} ({percentage:.1f}%)")
            report_lines.append("")
        
        # 每日使用统计
        if self.stats['daily_usage']:
            report_lines.append("📅 每日使用统计:")
            for date, count in sorted(self.stats['daily_usage'].items()):
                report_lines.append(f"  {date}: {count:,} 请求")
            report_lines.append("")
        
        # 每小时使用统计
        if self.stats['hourly_usage']:
            report_lines.append("🕐 每小时使用统计:")
            for hour in sorted(self.stats['hourly_usage'].keys(), key=int):
                count = self.stats['hourly_usage'][hour]
                report_lines.append(f"  {hour}:00: {count:,} 请求")
            report_lines.append("")
        
        # 错误统计
        if self.stats['error_types']:
            report_lines.append("❌ 错误统计:")
            for error, count in sorted(self.stats['error_types'].items(), key=lambda x: x[1], reverse=True):
                report_lines.append(f"  {error}: {count:,} 次")
            report_lines.append("")
        
        # 生成报告内容
        report_content = "\n".join(report_lines)
        
        # 保存到文件
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"报告已保存到: {output_file}")
            except Exception as e:
                print(f"保存报告失败: {e}")
        
        return report_content
    
    def export_stats_json(self, output_file: Optional[str] = None):
        """导出统计数据为JSON"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.log_dir / f"glm4_analysis_{timestamp}.json"
        
        analysis_data = {
            'timestamp': datetime.now().isoformat(),
            'log_directory': str(self.log_dir),
            'stats': self.stats,
            'summary': {
                'total_requests': self.stats['total_requests'],
                'successful_requests': self.stats['successful_requests'],
                'success_rate': self.stats['success_rate'],
                'total_tokens': self.stats['total_tokens'],
                'most_used_model': max(self.stats['models_used'].items(), key=lambda x: x[1])[0] if self.stats['models_used'] else None
            }
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            print(f"统计数据已导出到: {output_file}")
        except Exception as e:
            print(f"导出统计数据失败: {e}")
    
    def clean_old_logs(self, days: int = 30):
        """清理旧日志文件"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        for log_file in self.log_dir.glob('*.log*'):
            try:
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_mtime < cutoff_date:
                    log_file.unlink()
                    cleaned_count += 1
                    print(f"已删除旧日志文件: {log_file}")
            except Exception as e:
                print(f"删除日志文件失败 {log_file}: {e}")
        
        print(f"清理完成，共删除 {cleaned_count} 个旧日志文件")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='GLM-4.5日志分析工具')
    parser.add_argument('--log-dir', help='日志目录路径')
    parser.add_argument('--start-date', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--output', help='报告输出文件')
    parser.add_argument('--export-json', help='导出JSON统计文件')
    parser.add_argument('--clean-logs', type=int, metavar='DAYS', help='清理N天前的旧日志')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = GLM4LogAnalyzer(args.log_dir)
    
    # 清理旧日志
    if args.clean_logs:
        analyzer.clean_old_logs(args.clean_logs)
        return
    
    # 分析日志
    stats = analyzer.analyze_logs(args.start_date, args.end_date)
    
    # 生成报告
    report = analyzer.generate_report(args.output)
    print("\n" + report)
    
    # 导出JSON统计
    if args.export_json:
        analyzer.export_stats_json(args.export_json)


if __name__ == "__main__":
    main()