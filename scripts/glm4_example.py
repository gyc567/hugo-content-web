#!/usr/bin/env python3
"""
GLM-4.5 使用示例
GitHot - GitHub热门项目评测

演示如何使用GLM-4.5客户端进行API调用和日志记录
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# 添加脚本目录到Python路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from glm4_client import GLM4Client
from glm4_config import GLM4Config
from glm4_log_analyzer import GLM4LogAnalyzer


def example_basic_chat():
    """基本聊天示例"""
    print("🤖 基本聊天示例")
    print("-" * 50)
    
    try:
        # 创建客户端
        client = GLM4Client()
        
        # 简单对话
        messages = [
            {"role": "user", "content": "请简单介绍一下Python编程语言的特点"}
        ]
        
        print("发送请求中...")
        response = client.chat_completion(messages, temperature=0.7)
        
        # 输出响应
        if response.get('choices'):
            content = response['choices'][0]['message']['content']
            print(f"\nGLM-4.5回复:\n{content}")
        
        # 显示token使用情况
        usage = response.get('usage', {})
        print(f"\nToken使用情况:")
        print(f"  输入Token: {usage.get('prompt_tokens', 0)}")
        print(f"  输出Token: {usage.get('completion_tokens', 0)}")
        print(f"  总Token: {usage.get('total_tokens', 0)}")
        
    except Exception as e:
        print(f"错误: {e}")


def example_system_prompt():
    """系统提示词示例"""
    print("\n🎯 系统提示词示例")
    print("-" * 50)
    
    try:
        client = GLM4Client()
        
        # 带系统提示词的对话
        messages = [
            {
                "role": "system", 
                "content": "你是GitHot的AI助手，专门帮助开发者发现优质的GitHub热门项目和编程资源。你的回答应该专业、实用，并且能够提供具体的代码示例或项目推荐。"
            },
            {
                "role": "user", 
                "content": "我想学习如何使用Python进行网页爬虫，能推荐一些好的开源项目吗？"
            }
        ]
        
        print("发送带系统提示词的请求...")
        response = client.chat_completion(
            messages, 
            model="glm-4-plus",
            temperature=0.8,
            max_tokens=2048
        )
        
        if response.get('choices'):
            content = response['choices'][0]['message']['content']
            print(f"\nGitHot助手回复:\n{content}")
        
    except Exception as e:
        print(f"错误: {e}")


def example_multiple_requests():
    """批量请求示例"""
    print("\n📊 批量请求示例")
    print("-" * 50)
    
    try:
        client = GLM4Client()
        
        # 准备多个问题
        questions = [
            "什么是RESTful API？",
            "Docker的主要优势是什么？",
            "如何优化数据库查询性能？",
            "什么是微服务架构？",
            "Git的分支管理最佳实践是什么？"
        ]
        
        responses = []
        total_tokens = 0
        
        for i, question in enumerate(questions, 1):
            print(f"处理问题 {i}/{len(questions)}: {question}")
            
            messages = [
                {"role": "system", "content": "你是一个技术专家，请用简洁明了的方式回答技术问题。"},
                {"role": "user", "content": question}
            ]
            
            response = client.chat_completion(
                messages, 
                model="glm-4-flash",  # 使用快速模型
                temperature=0.5,
                max_tokens=1024
            )
            
            if response.get('choices'):
                content = response['choices'][0]['message']['content']
                usage = response.get('usage', {})
                
                responses.append({
                    'question': question,
                    'answer': content,
                    'tokens': usage.get('total_tokens', 0)
                })
                
                total_tokens += usage.get('total_tokens', 0)
                print(f"  回复长度: {len(content)} 字符")
                print(f"  Token使用: {usage.get('total_tokens', 0)}")
        
        print(f"\n批量处理完成:")
        print(f"  总问题数: {len(questions)}")
        print(f"  成功处理: {len(responses)}")
        print(f"  总Token消耗: {total_tokens}")
        
        # 获取客户端统计信息
        stats = client.get_stats()
        print(f"  客户端统计: {stats}")
        
    except Exception as e:
        print(f"错误: {e}")


def example_config_usage():
    """配置管理示例"""
    print("\n⚙️  配置管理示例")
    print("-" * 50)
    
    # 创建配置管理器
    config = GLM4Config()
    
    # 显示当前配置
    print("当前配置:")
    config.print_config_summary()
    
    # 验证配置
    if config.validate_config():
        print("\n✅ 配置验证通过")
    else:
        print("\n❌ 配置验证失败")
        print("请设置GLM4_API_KEY环境变量")
    
    # 获取特定配置
    model_config = config.get_model_config()
    print(f"\n模型配置: {model_config}")
    
    api_config = config.get_api_config()
    print(f"API配置: {api_config}")
    
    # 创建示例配置文件
    config.create_sample_config()


def example_log_analysis():
    """日志分析示例"""
    print("\n📋 日志分析示例")
    print("-" * 50)
    
    try:
        # 创建日志分析器
        analyzer = GLM4LogAnalyzer()
        
        # 分析日志
        print("开始分析日志文件...")
        stats = analyzer.analyze_logs()
        
        # 生成报告
        report = analyzer.generate_report()
        print("分析完成，生成报告:")
        print(report)
        
        # 导出统计数据
        timestamp = analyzer.stats.get('timestamp', 'unknown')
        json_file = f"glm4_stats_example.json"
        analyzer.export_stats_json(json_file)
        
    except Exception as e:
        print(f"日志分析错误: {e}")


def example_error_handling():
    """错误处理示例"""
    print("\n🚨 错误处理示例")
    print("-" * 50)
    
    # 测试无效API密钥
    try:
        # 临时设置无效的API密钥
        original_key = os.environ.get('GLM4_API_KEY')
        os.environ['GLM4_API_KEY'] = 'invalid_key_for_testing'
        
        client = GLM4Client()
        
        messages = [{"role": "user", "content": "这是一个测试请求"}]
        
        response = client.chat_completion(messages)
        print("意外成功了？这不应该发生")
        
    except Exception as e:
        print(f"预期的错误: {type(e).__name__}: {e}")
        
    finally:
        # 恢复原始API密钥
        if original_key:
            os.environ['GLM4_API_KEY'] = original_key
        else:
            os.environ.pop('GLM4_API_KEY', None)


def main():
    """主函数"""
    print("GLM-4.5 客户端使用示例")
    print("=" * 60)
    
    # 检查API密钥
    if not os.getenv('GLM4_API_KEY'):
        print("⚠️  警告: 未设置GLM4_API_KEY环境变量")
        print("某些示例可能无法正常运行")
        print()
    
    # 运行各种示例
    examples = [
        ("配置管理", example_config_usage),
        ("基本聊天", example_basic_chat),
        ("系统提示词", example_system_prompt),
        ("批量请求", example_multiple_requests),
        ("错误处理", example_error_handling),
        ("日志分析", example_log_analysis)
    ]
    
    for name, func in examples:
        try:
            func()
        except KeyboardInterrupt:
            print(f"\n用户中断了 {name} 示例")
            break
        except Exception as e:
            print(f"\n{name} 示例执行出错: {e}")
        
        print("\n" + "="*60)
    
    print("所有示例执行完毕！")


if __name__ == "__main__":
    main()