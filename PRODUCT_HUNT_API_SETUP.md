# Product Hunt API 配置指南

## 获取 API Token

### 方式一：Developer Token（推荐）
1. 访问 https://api.producthunt.com/v2/docs
2. 点击 "Sign in with Product Hunt" 
3. 登录后，在右上角点击你的头像
4. 选择 "Developer Settings"
5. 创建新的应用，获取 Developer Token

### 方式二：OAuth API Key
1. 在 Developer Settings 中创建 OAuth 应用
2. 设置 callback URL: `http://localhost:8000/auth/callback`
3. 获取 Client ID 和 Client Secret
4. 使用 OAuth 流程获取 access token

## 配置环境变量

编辑 `.env` 文件：

```bash
# 使用 Developer Token（推荐）
PRODUCT_HUNT_DEVELOPER_TOKEN=your_actual_developer_token_here

# 或者使用 OAuth API Key
PRODUCT_HUNT_API_KEY=your_actual_api_key_here

# API 基础URL（可选）
PRODUCT_HUNT_BASE_URL=https://api.producthunt.com/v2/api/graphql
```

## 验证配置

配置完成后运行测试：

```bash
python scripts/producthunt_analyzer.py
```

成功配置后应该看到：
```
✅ Product Hunt API已配置，使用: Developer Token
🚀 通过Product Hunt API获取今日热门产品...
✅ API成功获取到 3 个今日产品
```

## API 限制

- **请求频率**: 每分钟最多 60 次请求
- **每日限制**: 具体限制取决于你的应用类型
- **数据范围**: 可以获取公开的产品信息
- **认证**: Bearer Token 认证

## 故障排除

### 401 错误
- 检查 token 是否正确
- 确认 token 没有过期
- 验证应用权限设置

### 403 错误
- 检查请求频率
- 确认应用状态正常
- 验证 API 权限

### 网络问题
- 检查网络连接
- 确认防火墙设置
- 验证 DNS 解析

## 数据结构

API 返回的产品数据包含：
- `name`: 产品名称
- `tagline`: 产品标语
- `description`: 详细描述
- `votesCount`: 投票数
- `url`: Product Hunt 链接
- `website`: 官方网站
- `topics`: 产品分类标签
- `thumbnail`: 产品图片
- `createdAt`: 发布时间

## 备用方案

如果 API 不可用，系统会自动：
1. 尝试网页抓取
2. 使用智能备用数据源
3. 确保去重功能正常工作