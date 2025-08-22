# 本地开发指南

## 启动开发服务器

### 方法1：使用开发配置（推荐）
```bash
hugo server -D --config hugo.dev.toml
```

### 方法2：指定端口
```bash
hugo server -D --port 1314
```

### 方法3：使用环境变量覆盖 baseURL
```bash
hugo server -D --baseURL "http://localhost:1313/"
```

## 访问地址
开发服务器启动后，可以通过以下地址访问：
- 主页面: `http://localhost:1313/` (或指定的端口)
- 文章页面: `http://localhost:1313/posts/github-claude-agent-xxx-review-2025-08-22/`

## 配置说明

### 生产环境配置 (`hugo.toml`)
- `baseURL = "https://your-domain.com"` - 生产环境域名
- 启用 Monetag 广告
- 启用 robots.txt

### 开发环境配置 (`hugo.dev.toml`)  
- `baseURL = "http://localhost:1313/"` - 本地开发地址
- 禁用 Monetag 广告
- 禁用 robots.txt
- 添加 development 关键词

## 常见问题

### 问题：链接显示错误的域名（ww25.your-domain.com）
**解决方案**: 使用开发配置启动服务器：
```bash
hugo server -D --config hugo.dev.toml
```

### 问题：端口被占用
**解决方案**: 使用其他端口：
```bash
hugo server -D --port 1314
```

### 问题：Hugo 构建错误
**解决方案**: 清理并重新构建：
```bash
rm -rf public/
hugo --minify
```

## 自动化工作流

GitHub Actions 工作流已配置为每日自动运行：
- 文件: `.github/workflows/daily-claude-agent-analysis.yml`
- 时间: 每天 UTC 16:00 (北京时间 00:00)
- 功能: 自动搜索 Claude Agent 项目并生成文章

## 测试

运行功能测试：
```bash
cd scripts/
python test-analyzer.py
```

## 部署

生产环境部署前，请确保：
1. 更新 `hugo.toml` 中的 `baseURL` 为实际域名
2. 配置正确的 Monetag Site ID
3. 设置环境变量 `GITHUB_TOKEN` 用于 API 访问