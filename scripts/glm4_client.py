#!/usr/bin/env python3
"""
GLM-4.5 API Client with Logging
SuperCopyCoder - 模仿，是最好的致敬。站在巨人的肩膀，站得更高

This module provides a client for interacting with GLM-4.5 API
with comprehensive logging of requests, responses, and token usage.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests
from logging.handlers import RotatingFileHandler


class GLM4Client:
    """GLM-4.5 API客户端，带有详细的日志记录功能"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://open.bigmodel.cn/api/paas/v4/"):
        """
        初始化GLM-4.5客户端
        
        Args:
            api_key: GLM-4.5 API密钥
            base_url: API基础URL
        """
        self.api_key = api_key or os.getenv('GLM4_API_KEY')
        self.base_url = base_url.rstrip('/')
        
        if not self.api_key:
            raise ValueError("GLM-4.5 API密钥未设置。请设置环境变量GLM4_API_KEY或传入api_key参数")
        
        # 设置日志记录
        self._setup_logging()
        
        # 初始化统计信息
        self.stats = {
            'total_requests': 0,
            'total_tokens_consumed': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }
    
    def _setup_logging(self):
        """设置日志记录系统"""
        # 创建logs目录
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 设置主日志文件
        log_file = os.path.join(log_dir, 'glm4_client.log')
        
        # 创建logger
        self.logger = logging.getLogger('GLM4Client')
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 创建rotatingfile handler
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            
            # 创建控制台handler
            console_handler = logging.StreamHandler()
            
            # 设置日志格式
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        # 设置详细请求日志文件
        request_log_file = os.path.join(log_dir, 'glm4_requests.log')
        self.request_logger = logging.getLogger('GLM4Requests')
        self.request_logger.setLevel(logging.INFO)
        
        if not self.request_logger.handlers:
            request_handler = RotatingFileHandler(
                request_log_file,
                maxBytes=50*1024*1024,  # 50MB
                backupCount=10,
                encoding='utf-8'
            )
            request_formatter = logging.Formatter(
                '%(asctime)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            request_handler.setFormatter(request_formatter)
            self.request_logger.addHandler(request_handler)
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: str = "glm-4-plus",
                       temperature: float = 0.7,
                       max_tokens: int = 4096,
                       **kwargs) -> Dict[str, Any]:
        """
        发送聊天完成请求到GLM-4.5 API
        
        Args:
            messages: 对话消息列表
            model: 模型名称
            temperature: 随机性控制
            max_tokens: 最大输出token数
            **kwargs: 其他API参数
            
        Returns:
            API响应数据
        """
        request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # 构建请求数据
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # 记录请求开始
        self.logger.info(f"开始GLM-4.5 API请求 | RequestID: {request_id}")
        self._log_request_details(request_id, request_data)
        
        try:
            # 发送API请求
            response = self._make_api_request(request_data)
            
            # 记录响应
            self._log_response_details(request_id, response)
            
            # 更新统计信息
            self._update_stats(response, success=True)
            
            self.logger.info(f"GLM-4.5 API请求成功 | RequestID: {request_id}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"GLM-4.5 API请求失败 | RequestID: {request_id} | Error: {str(e)}")
            self._update_stats({}, success=False)
            raise
    
    def _make_api_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送API请求"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}/chat/completions"
        
        response = requests.post(
            url,
            headers=headers,
            json=request_data,
            timeout=60
        )
        
        response.raise_for_status()
        return response.json()
    
    def _log_request_details(self, request_id: str, request_data: Dict[str, Any]):
        """记录详细的请求信息"""
        log_entry = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'REQUEST',
            'model': request_data.get('model'),
            'temperature': request_data.get('temperature'),
            'max_tokens': request_data.get('max_tokens'),
            'message_count': len(request_data.get('messages', [])),
            'messages': request_data.get('messages', []),
            'other_params': {k: v for k, v in request_data.items() 
                           if k not in ['model', 'messages', 'temperature', 'max_tokens']}
        }
        
        self.request_logger.info(f"REQUEST | {json.dumps(log_entry, ensure_ascii=False, indent=2)}")
    
    def _log_response_details(self, request_id: str, response_data: Dict[str, Any]):
        """记录详细的响应信息"""
        usage = response_data.get('usage', {})
        choices = response_data.get('choices', [])
        
        log_entry = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'RESPONSE',
            'model': response_data.get('model'),
            'response_id': response_data.get('id'),
            'choices_count': len(choices),
            'choices': choices,
            'token_usage': {
                'prompt_tokens': usage.get('prompt_tokens', 0),
                'completion_tokens': usage.get('completion_tokens', 0),
                'total_tokens': usage.get('total_tokens', 0)
            },
            'created': response_data.get('created'),
            'object': response_data.get('object')
        }
        
        self.request_logger.info(f"RESPONSE | {json.dumps(log_entry, ensure_ascii=False, indent=2)}")
        
        # 单独记录token使用情况
        self.logger.info(f"Token使用 | RequestID: {request_id} | "
                        f"输入: {usage.get('prompt_tokens', 0)} | "
                        f"输出: {usage.get('completion_tokens', 0)} | "
                        f"总计: {usage.get('total_tokens', 0)}")
    
    def _update_stats(self, response_data: Dict[str, Any], success: bool = True):
        """更新统计信息"""
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
            usage = response_data.get('usage', {})
            self.stats['total_input_tokens'] += usage.get('prompt_tokens', 0)
            self.stats['total_output_tokens'] += usage.get('completion_tokens', 0)
            self.stats['total_tokens_consumed'] += usage.get('total_tokens', 0)
        else:
            self.stats['failed_requests'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def save_stats(self, filename: Optional[str] = None):
        """保存统计信息到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"glm4_stats_{timestamp}.json"
        
        stats_dir = os.path.join(os.path.dirname(__file__), 'logs')
        stats_file = os.path.join(stats_dir, filename)
        
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'session_info': {
                'api_base_url': self.base_url,
                'has_api_key': bool(self.api_key)
            }
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"统计信息已保存到: {stats_file}")


def main():
    """测试GLM-4.5客户端"""
    try:
        # 创建客户端实例
        client = GLM4Client()
        
        # 测试对话
        messages = [
            {"role": "system", "content": "你是SuperCopyCoder的AI助手，专门帮助开发者找到最优质的代码资源和AI工具。"},
            {"role": "user", "content": "请介绍一下SuperCopyCoder平台的主要功能和价值。"}
        ]
        
        print("正在调用GLM-4.5 API...")
        response = client.chat_completion(messages)
        
        # 输出响应
        if 'choices' in response and len(response['choices']) > 0:
            content = response['choices'][0]['message']['content']
            print(f"\nGLM-4.5响应:")
            print(content)
        
        # 显示统计信息
        stats = client.get_stats()
        print(f"\n统计信息:")
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求: {stats['successful_requests']}")
        print(f"消耗Token: {stats['total_tokens_consumed']}")
        
        # 保存统计信息
        client.save_stats()
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()