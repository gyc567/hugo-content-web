# GLM-4.5 大模型调用与日志系统

GitHot - GitHub热门项目评测

## 📋 功能概述

本系统提供了完整的GLM-4.5大模型调用功能，包括：

- ✅ **API调用客户端** - 支持GLM-4.5所有模型的调用
- ✅ **详细日志记录** - 完整记录请求、响应和Token消耗
- ✅ **配置管理** - 灵活的配置文件和环境变量管理
- ✅ **日志分析工具** - 统计分析API使用情况和成本
- ✅ **错误处理** - 完善的错误处理和重试机制
- ✅ **使用示例** - 丰富的使用示例和最佳实践

## 🚀 快速开始

### 1. 安装依赖

```bash
cd scripts
pip install -r requirements.txt
```

### 2. 设置API密钥

```bash
# 设置环境变量（推荐方式）
export GLM4_API_KEY="your_api_key_here"

# 或者在.bashrc/.zshrc中永久设置
echo 'export GLM4_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. 基本使用

```python
from glm4_client import GLM4Client

# 创建客户端
client = GLM4Client()

# 发送请求
messages = [
    {"role": "user", "content": "请介绍一下Python的特点"}
]

response = client.chat_completion(messages)
print(response['choices'][0]['message']['content'])
```

### 4. 运行示例

```bash
python glm4_example.py
```

## 📁 文件结构

```
scripts/
├── glm4_client.py          # GLM-4.5 API客户端
├── glm4_config.py          # 配置管理器
├── glm4_log_analyzer.py    # 日志分析工具
├── glm4_example.py         # 使用示例
├── GLM4_README.md          # 本文档
├── requirements.txt        # Python依赖
├── logs/                   # 日志目录
│   ├── glm4_client.log     # 主日志文件
│   ├── glm4_requests.log   # 详细请求日志
│   └── glm4_stats_*.json   # 统计数据文件
└── glm4_config.json        # 配置文件（可选）
```

## 🔧 详细功能说明

### GLM4Client - API客户端

主要功能：
- 支持所有GLM-4.5模型（glm-4-plus, glm-4-flash等）
- 自动日志记录和统计
- 错误处理和重试机制
- Token使用统计

```python
from glm4_client import GLM4Client

client = GLM4Client()

# 基本调用
response = client.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model="glm-4-plus",
    temperature=0.7,
    max_tokens=2048
)

# 获取统计信息
stats = client.get_stats()
print(f"总请求数: {stats['total_requests']}")
print(f"Token消耗: {stats['total_tokens_consumed']}")
```

### GLM4Config - 配置管理

管理API密钥、默认参数等配置：

```python
from glm4_config import GLM4Config

config = GLM4Config()

# 获取配置
model_config = config.get_model_config()
api_config = config.get_api_config()

# 设置配置
config.set('chat.temperature', 0.8)
config.save_config()

# 验证配置
if config.validate_config():
    print("配置有效")
```

### GLM4LogAnalyzer - 日志分析

分析API使用情况和生成统计报告：

```python
from glm4_log_analyzer import GLM4LogAnalyzer

analyzer = GLM4LogAnalyzer()

# 分析日志
stats = analyzer.analyze_logs(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# 生成报告
report = analyzer.generate_report("monthly_report.txt")

# 导出统计数据
analyzer.export_stats_json("stats.json")
```

## 📊 日志格式说明

### 主日志文件 (glm4_client.log)

格式：`时间戳 | 日志级别 | 函数名:行号 | 消息内容`

示例：
```
2024-01-15 10:30:15 | INFO | chat_completion:85 | 开始GLM-4.5 API请求 | RequestID: 20240115_103015_123456
2024-01-15 10:30:16 | INFO | _log_response_details:145 | Token使用 | RequestID: 20240115_103015_123456 | 输入: 25 | 输出: 150 | 总计: 175
2024-01-15 10:30:16 | INFO | chat_completion:95 | GLM-4.5 API请求成功 | RequestID: 20240115_103015_123456
```

### 详细请求日志 (glm4_requests.log)

包含完整的请求和响应数据（JSON格式）：

```json
2024-01-15 10:30:15 | REQUEST | {
  "request_id": "20240115_103015_123456",
  "timestamp": "2024-01-15T10:30:15.123456",
  "type": "REQUEST",
  "model": "glm-4-plus",
  "temperature": 0.7,
  "max_tokens": 2048,
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "请介绍一下Python"
    }
  ]
}

2024-01-15 10:30:16 | RESPONSE | {
  "request_id": "20240115_103015_123456",
  "timestamp": "2024-01-15T10:30:16.789012",
  "type": "RESPONSE",
  "model": "glm-4-plus",
  "response_id": "chatcmpl-123456",
  "choices_count": 1,
  "choices": [...],
  "token_usage": {
    "prompt_tokens": 25,
    "completion_tokens": 150,
    "total_tokens": 175
  }
}
```

## 📈 使用统计和分析

### 统计数据包含：

- **基本统计**：总请求数、成功/失败次数、成功率
- **Token使用**：输入/输出/总Token数、平均使用量
- **模型使用**：各模型的使用频率和分布
- **时间分析**：每日/每小时使用统计
- **错误分析**：错误类型和频率统计

### 生成分析报告：

```bash
# 分析所有日志
python glm4_log_analyzer.py

# 分析指定时间范围
python glm4_log_analyzer.py --start-date 2024-01-01 --end-date 2024-01-31

# 生成报告文件
python glm4_log_analyzer.py --output monthly_report.txt

# 导出JSON统计
python glm4_log_analyzer.py --export-json stats.json

# 清理旧日志（保留30天）
python glm4_log_analyzer.py --clean-logs 30
```

## ⚙️ 配置选项

### 环境变量

- `GLM4_API_KEY` - GLM-4.5 API密钥（必需）

### 配置文件 (glm4_config.json)

```json
{
  "api": {
    "base_url": "https://open.bigmodel.cn/api/paas/v4/",
    "timeout": 60,
    "max_retries": 3,
    "retry_delay": 1.0
  },
  "models": {
    "default": "glm-4-plus",
    "available": ["glm-4-plus", "glm-4-flash", "glm-4-air"]
  },
  "chat": {
    "temperature": 0.7,
    "max_tokens": 4096,
    "top_p": 0.9,
    "stream": false
  },
  "logging": {
    "level": "INFO",
    "max_file_size": 10485760,
    "backup_count": 5
  }
}
```

## 🚨 错误处理

系统包含完善的错误处理机制：

### 常见错误类型：

1. **API密钥错误** - `401 Unauthorized`
2. **请求频率限制** - `429 Too Many Requests`
3. **请求参数错误** - `400 Bad Request`
4. **网络连接错误** - `ConnectionError`
5. **响应超时** - `TimeoutError`

### 错误处理策略：

- 自动重试（可配置重试次数和延迟）
- 详细错误日志记录
- 错误统计和分析
- 用户友好的错误消息

## 💰 成本控制

### Token使用监控：

- 实时记录每次请求的Token消耗
- 累计统计总Token使用量
- 按模型分类统计使用情况
- 生成成本分析报告

### 使用建议：

1. **选择合适的模型**：
   - `glm-4-flash`：速度快，成本低，适合简单任务
   - `glm-4-plus`：功能强大，适合复杂任务
   - `glm-4-air`：轻量级，适合批量处理

2. **优化Token使用**：
   - 合理设置`max_tokens`参数
   - 使用简洁的提示词
   - 避免重复的上下文信息

3. **监控使用情况**：
   - 定期查看日志分析报告
   - 设置使用量预警
   - 分析成本效益

## 🔐 安全注意事项

1. **API密钥保护**：
   - 使用环境变量存储API密钥
   - 不要在代码中硬编码密钥
   - 不要将密钥提交到版本控制系统

2. **日志安全**：
   - 日志文件可能包含敏感信息
   - 定期清理旧日志文件
   - 控制日志文件的访问权限

3. **网络安全**：
   - 使用HTTPS协议
   - 验证SSL证书
   - 考虑使用代理或VPN

## 📚 最佳实践

### 1. 合理使用模型

```python
# 简单任务使用快速模型
response = client.chat_completion(
    messages, 
    model="glm-4-flash",
    temperature=0.3
)

# 复杂任务使用强力模型
response = client.chat_completion(
    messages, 
    model="glm-4-plus",
    temperature=0.7
)
```

### 2. 系统提示词优化

```python
system_prompt = """
你是GitHot的AI助手，专门帮助开发者发现优质的GitHub热门项目。
请遵循以下规则：
1. 提供准确、实用的信息
2. 包含具体的代码示例或项目链接
3. 保持回答简洁明了
4. 重点关注开源和免费资源
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_question}
]
```

### 3. 错误处理

```python
try:
    response = client.chat_completion(messages)
    # 处理成功响应
except Exception as e:
    # 记录错误并提供fallback
    logger.error(f"API调用失败: {e}")
    # 实现降级策略
```

### 4. 批量处理

```python
# 批量处理时使用较小的温度值和token限制
for question in questions:
    response = client.chat_completion(
        messages=[{"role": "user", "content": question}],
        model="glm-4-flash",
        temperature=0.3,
        max_tokens=1024
    )
```

## 🛠 故障排除

### 常见问题及解决方案：

1. **API密钥未设置**
   ```bash
   export GLM4_API_KEY="your_key_here"
   ```

2. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置
   - 考虑使用代理

3. **权限错误**
   - 检查API密钥是否有效
   - 确认账户余额充足
   - 验证API调用权限

4. **日志文件过大**
   ```bash
   python glm4_log_analyzer.py --clean-logs 30
   ```

### 调试模式：

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 使用配置文件设置
config = GLM4Config()
config.set('logging.level', 'DEBUG')
```

## 📞 技术支持

如有问题或建议，请联系：

- **邮箱**: gyc567@gmail.com
- **Twitter**: @EricBlock2100
- **Telegram**: https://t.me/fatoshi_block

---

**GitHot** - GitHub热门项目评测。