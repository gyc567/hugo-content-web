#!/usr/bin/env python3
"""
GLM-4.5 配置管理
SuperCopyCoder - 模仿，是最好的致敬。站在巨人的肩膀，站得更高

管理GLM-4.5 API的配置信息，包括API密钥、默认参数等
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class GLM4Config:
    """GLM-4.5配置管理类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "api": {
            "base_url": "https://open.bigmodel.cn/api/paas/v4/",
            "timeout": 60,
            "max_retries": 3,
            "retry_delay": 1.0
        },
        "models": {
            "default": "glm-4-plus",
            "available": [
                "glm-4-plus",
                "glm-4-0520", 
                "glm-4",
                "glm-4-air",
                "glm-4-airx",
                "glm-4-flash"
            ]
        },
        "chat": {
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 0.9,
            "stream": False
        },
        "logging": {
            "level": "INFO",
            "max_file_size": 10485760,  # 10MB
            "backup_count": 5,
            "request_log_size": 52428800,  # 50MB
            "request_backup_count": 10
        },
        "stats": {
            "auto_save": True,
            "save_interval": 100  # 每100次请求自动保存一次统计
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认为脚本目录下的glm4_config.json
        """
        self.script_dir = Path(__file__).parent
        self.config_file = Path(config_file) if config_file else self.script_dir / "glm4_config.json"
        
        # 加载配置
        self.config = self.load_config()
        
        # 获取API密钥
        self.api_key = self.get_api_key()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 合并默认配置和用户配置
                merged_config = self._merge_configs(self.DEFAULT_CONFIG.copy(), config)
                return merged_config
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载配置文件失败: {e}")
                print("使用默认配置")
                
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """合并默认配置和用户配置"""
        for key, value in user.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    default[key] = self._merge_configs(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
        return default
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 创建配置目录
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置（不包含敏感信息）
            safe_config = self.config.copy()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(safe_config, f, ensure_ascii=False, indent=2)
                
            print(f"配置已保存到: {self.config_file}")
            
        except IOError as e:
            print(f"保存配置文件失败: {e}")
    
    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        # 优先从环境变量获取
        api_key = os.getenv('GLM4_API_KEY')
        if api_key:
            return api_key
        
        # 从配置文件获取（不推荐在配置文件中存储API密钥）
        return self.config.get('api_key')
    
    def set_api_key(self, api_key: str, save_to_env: bool = True):
        """
        设置API密钥
        
        Args:
            api_key: API密钥
            save_to_env: 是否保存到环境变量（推荐）
        """
        if save_to_env:
            os.environ['GLM4_API_KEY'] = api_key
            print("API密钥已设置到环境变量")
        else:
            self.config['api_key'] = api_key
            print("API密钥已设置到配置文件（不推荐）")
    
    def get(self, key_path: str, default=None):
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，如 'api.base_url'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
    
    def set(self, key_path: str, value: Any):
        """
        设置配置值
        
        Args:
            key_path: 配置键路径，如 'api.base_url'
            value: 配置值
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        # 导航到目标位置
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        # 设置值
        config_ref[keys[-1]] = value
    
    def get_model_config(self, model: Optional[str] = None) -> Dict[str, Any]:
        """获取模型相关配置"""
        model = model or self.get('models.default')
        
        return {
            'model': model,
            'temperature': self.get('chat.temperature'),
            'max_tokens': self.get('chat.max_tokens'),
            'top_p': self.get('chat.top_p'),
            'stream': self.get('chat.stream')
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API相关配置"""
        return {
            'base_url': self.get('api.base_url'),
            'timeout': self.get('api.timeout'),
            'max_retries': self.get('api.max_retries'),
            'retry_delay': self.get('api.retry_delay'),
            'api_key': self.api_key
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志相关配置"""
        return {
            'level': self.get('logging.level'),
            'max_file_size': self.get('logging.max_file_size'),
            'backup_count': self.get('logging.backup_count'),
            'request_log_size': self.get('logging.request_log_size'),
            'request_backup_count': self.get('logging.request_backup_count')
        }
    
    def create_sample_config(self):
        """创建示例配置文件"""
        sample_config = {
            "api": {
                "base_url": "https://open.bigmodel.cn/api/paas/v4/",
                "timeout": 60,
                "max_retries": 3
            },
            "chat": {
                "temperature": 0.8,
                "max_tokens": 2048
            },
            "logging": {
                "level": "DEBUG"
            },
            "_note": "请设置环境变量GLM4_API_KEY来配置API密钥，不要在此文件中存储密钥"
        }
        
        sample_file = self.script_dir / "glm4_config.sample.json"
        
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, ensure_ascii=False, indent=2)
            
        print(f"示例配置文件已创建: {sample_file}")
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        required_keys = [
            'api.base_url',
            'models.default',
            'chat.temperature',
            'chat.max_tokens'
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                print(f"缺少必要配置: {key}")
                return False
        
        # 验证API密钥
        if not self.api_key:
            print("未设置GLM4_API_KEY环境变量")
            return False
        
        # 验证模型名称
        available_models = self.get('models.available', [])
        default_model = self.get('models.default')
        
        if default_model not in available_models:
            print(f"默认模型 {default_model} 不在可用模型列表中")
            return False
        
        return True
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("GLM-4.5 配置摘要:")
        print(f"  API Base URL: {self.get('api.base_url')}")
        print(f"  默认模型: {self.get('models.default')}")
        print(f"  Temperature: {self.get('chat.temperature')}")
        print(f"  Max Tokens: {self.get('chat.max_tokens')}")
        print(f"  Timeout: {self.get('api.timeout')}s")
        print(f"  API密钥: {'已设置' if self.api_key else '未设置'}")
        print(f"  配置文件: {self.config_file}")


def main():
    """配置管理器测试"""
    config_manager = GLM4Config()
    
    # 打印配置摘要
    config_manager.print_config_summary()
    
    # 验证配置
    if config_manager.validate_config():
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败")
    
    # 创建示例配置
    config_manager.create_sample_config()


if __name__ == "__main__":
    main()