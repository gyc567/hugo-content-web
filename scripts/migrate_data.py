#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本

该脚本用于将现有的项目历史数据从v1格式（列表）迁移到v2格式（字典），
确保与新的ProjectDeduplicator系统兼容。

作者: Qoder AI Assistant
创建时间: 2025-08-24
"""

import os
import json
import datetime
import hashlib
import shutil
from typing import Dict, Any, List
from project_deduplicator import ProjectDeduplicator


class DataMigrator:
    """数据迁移工具类"""
    
    def __init__(self, history_file_path: str):
        """
        初始化数据迁移工具
        
        Args:
            history_file_path: 历史文件路径
        """
        self.history_file_path = history_file_path
        self.backup_file_path = f"{history_file_path}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def backup_original_data(self) -> bool:
        """
        备份原始数据文件
        
        Returns:
            备份是否成功
        """
        try:
            if os.path.exists(self.history_file_path):
                shutil.copy2(self.history_file_path, self.backup_file_path)
                print(f"✅ 已备份原始数据到: {self.backup_file_path}")
                return True
            else:
                print("ℹ️  原始数据文件不存在，无需备份")
                return True
        except Exception as e:
            print(f"❌ 备份数据失败: {e}")
            return False
    
    def detect_data_format(self) -> str:
        """
        检测当前数据格式版本
        
        Returns:
            数据格式版本: 'v1', 'v2', 'empty', 'invalid'
        """
        try:
            if not os.path.exists(self.history_file_path):
                return 'empty'
            
            with open(self.history_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否为v2格式
            if 'version' in data and data.get('version') == '2.0':
                return 'v2'
            
            # 检查是否为v1格式（包含analyzed_projects列表）
            if 'analyzed_projects' in data:
                if isinstance(data['analyzed_projects'], list):
                    return 'v1'
                elif isinstance(data['analyzed_projects'], dict):
                    return 'v2'
            
            # 旧的简单格式（只有项目列表）
            if isinstance(data, list):
                return 'v1_simple'
            
            return 'invalid'
            
        except json.JSONDecodeError:
            print("❌ 数据文件JSON格式无效")
            return 'invalid'
        except Exception as e:
            print(f"❌ 检测数据格式失败: {e}")
            return 'invalid'
    
    def migrate_v1_to_v2(self) -> bool:
        """
        将v1格式数据迁移到v2格式
        
        Returns:
            迁移是否成功
        """
        try:
            with open(self.history_file_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            # 提取项目列表
            if isinstance(old_data, list):
                # 简单列表格式
                project_list = old_data
            elif isinstance(old_data, dict) and 'analyzed_projects' in old_data:
                # 复杂v1格式
                project_list = old_data['analyzed_projects']
            else:
                print("❌ 无法识别的v1数据格式")
                return False
            
            # 转换为v2格式
            current_time = datetime.datetime.now().isoformat()
            v2_data = {
                'version': '2.0',
                'last_updated': current_time,
                'total_projects': len(project_list),
                'analyzed_projects': {},
                'migration_info': {
                    'migrated_from_v1': True,
                    'migration_date': current_time,
                    'original_backup': self.backup_file_path
                }
            }
            
            # 转换每个项目记录
            for project_key in project_list:
                if isinstance(project_key, str) and project_key.strip():
                    project_hash = hashlib.sha256(project_key.encode('utf-8')).hexdigest()
                    v2_data['analyzed_projects'][project_key] = {
                        'added_date': current_time,
                        'project_hash': project_hash,
                        'github_url': f"https://github.com/{project_key}",
                        'stars_when_analyzed': 0,
                        'migrated_from_v1': True
                    }
            
            # 保存新格式数据
            with open(self.history_file_path, 'w', encoding='utf-8') as f:
                json.dump(v2_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功迁移 {len(project_list)} 个项目记录到v2格式")
            return True
            
        except Exception as e:
            print(f"❌ 迁移数据失败: {e}")
            return False
    
    def validate_migration(self) -> bool:
        """
        验证迁移结果
        
        Returns:
            验证是否通过
        """
        try:
            # 使用ProjectDeduplicator验证新格式
            deduplicator = ProjectDeduplicator(self.history_file_path)
            stats = deduplicator.get_project_statistics()
            
            print(f"📊 迁移后统计:")
            print(f"   - 总项目数: {stats['total_projects']}")
            print(f"   - 最后更新: {stats['last_updated']}")
            
            # 验证数据完整性
            if stats['total_projects'] > 0:
                print("✅ 迁移验证通过")
                return True
            else:
                print("⚠️  迁移后数据为空，可能存在问题")
                return False
                
        except Exception as e:
            print(f"❌ 迁移验证失败: {e}")
            return False
    
    def run_migration(self) -> bool:
        """
        执行完整的迁移流程
        
        Returns:
            迁移是否成功
        """
        print("🔄 开始数据迁移流程...")
        
        # 检测当前数据格式
        format_version = self.detect_data_format()
        print(f"📋 检测到数据格式: {format_version}")
        
        if format_version == 'v2':
            print("✅ 数据已经是v2格式，无需迁移")
            return True
        
        if format_version == 'empty':
            print("ℹ️  数据文件为空，创建新的v2格式文件")
            deduplicator = ProjectDeduplicator(self.history_file_path)
            stats = deduplicator.get_project_statistics()
            print(f"✅ 已创建新的v2格式文件，项目数: {stats['total_projects']}")
            return True
        
        if format_version == 'invalid':
            print("❌ 数据格式无效，无法迁移")
            return False
        
        # 备份原始数据
        if not self.backup_original_data():
            print("❌ 备份失败，终止迁移")
            return False
        
        # 执行迁移
        if format_version in ['v1', 'v1_simple']:
            if not self.migrate_v1_to_v2():
                print("❌ 迁移失败")
                return False
        
        # 验证迁移结果
        if not self.validate_migration():
            print("❌ 迁移验证失败")
            return False
        
        print("🎉 数据迁移完成！")
        return True
    
    def rollback_migration(self) -> bool:
        """
        回滚迁移，恢复备份数据
        
        Returns:
            回滚是否成功
        """
        try:
            if os.path.exists(self.backup_file_path):
                shutil.copy2(self.backup_file_path, self.history_file_path)
                print(f"✅ 已从备份恢复数据: {self.backup_file_path}")
                return True
            else:
                print("❌ 备份文件不存在，无法回滚")
                return False
        except Exception as e:
            print(f"❌ 回滚失败: {e}")
            return False


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='项目历史数据迁移工具')
    parser.add_argument('--file', '-f', 
                       default='data/analyzed_projects.json',
                       help='历史数据文件路径 (默认: data/analyzed_projects.json)')
    parser.add_argument('--check', '-c', action='store_true',
                       help='仅检查数据格式，不执行迁移')
    parser.add_argument('--rollback', '-r', action='store_true',
                       help='回滚到备份数据')
    parser.add_argument('--force', action='store_true',
                       help='强制执行迁移（跳过确认）')
    
    args = parser.parse_args()
    
    # 确保data目录存在
    os.makedirs(os.path.dirname(args.file), exist_ok=True)
    
    migrator = DataMigrator(args.file)
    
    if args.rollback:
        print("🔄 执行回滚操作...")
        if migrator.rollback_migration():
            print("✅ 回滚成功")
        else:
            print("❌ 回滚失败")
        return
    
    if args.check:
        print("🔍 检查数据格式...")
        format_version = migrator.detect_data_format()
        print(f"📋 当前数据格式: {format_version}")
        
        if format_version == 'v2':
            print("✅ 数据格式正确，无需迁移")
        elif format_version in ['v1', 'v1_simple']:
            print("⚠️  需要迁移到v2格式")
        elif format_version == 'empty':
            print("ℹ️  数据文件为空")
        else:
            print("❌ 数据格式无效")
        return
    
    # 执行迁移
    print("=" * 50)
    print("🚀 项目去重优化 - 数据迁移工具")
    print("=" * 50)
    
    if not args.force:
        print("⚠️  注意: 此操作将修改项目历史数据文件")
        print(f"📁 目标文件: {args.file}")
        confirm = input("是否继续? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ 用户取消操作")
            return
    
    success = migrator.run_migration()
    
    if success:
        print("\n✅ 迁移完成！新的去重系统已启用。")
        print("💡 提示: 现在可以运行项目分析器，重复项目将被自动过滤。")
    else:
        print("\n❌ 迁移失败！请检查错误信息。")
        print("💡 提示: 如需恢复，请使用 --rollback 参数。")


if __name__ == "__main__":
    main()