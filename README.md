# WislicAIWorld

AI 研究报告归档网站 — 集中管理和浏览 Claude 生成的 HTML 报告。

## ✨ 功能

- **分类归档**：宏观日报 / 盘中速览 / 专题研究 / 其他（可扩展）
- **深色 / 浅色主题**：一键切换，偏好自动保存
- **快速搜索**：⌘K 快捷键，按标题 / 日期 / 类型检索
- **内嵌预览**：iframe 预览报告，支持新窗口打开
- **移动端适配**：响应式布局，手机也能用
- **零依赖部署**：纯静态 HTML，无需后端

## 📁 目录结构

```
WislicAIWorld/
├── index.html          ← 主站点
├── reports.json        ← 报告注册表（核心配置）
├── reports/
│   ├── daily/          ← 宏观日报
│   ├── flash/          ← 盘中速览
│   ├── deep/           ← 专题研究
│   └── other/          ← 其他报告
└── README.md
```

## 🚀 部署到 GitHub Pages

### 首次部署

```bash
# 1. 进入项目目录
cd /Users/wislic/Documents/Claude/WislicAIWorld

# 2. 初始化 Git
git init
git add .
git commit -m "🚀 init WislicAIWorld"

# 3. 在 GitHub 创建仓库 WislicAIWorld（不要勾选 README）

# 4. 关联远程仓库并推送
git remote add origin https://github.com/你的用户名/WislicAIWorld.git
git branch -M main
git push -u origin main

# 5. 开启 GitHub Pages
#    GitHub 仓库 → Settings → Pages → Source: main branch → Save
#    等待 1-2 分钟，访问 https://你的用户名.github.io/WislicAIWorld/
```

### 日常更新

```bash
# 1. 把 Claude 生成的 HTML 文件放入对应文件夹
#    例如：reports/daily/2026-03-30.html

# 2. 在 reports.json 中添加记录

# 3. 推送更新
git add .
git commit -m "add: 宏观日报 2026-03-30"
git push
```

## 📝 添加新报告

在 `reports.json` 中添加一条记录：

```json
{
  "title": "报告标题",
  "category": "daily",
  "date": "2026-03-30",
  "file": "reports/daily/2026-03-30.html"
}
```

**category 可选值：**

| 值 | 含义 | 文件夹 |
|---|---|---|
| `daily` | 宏观日报 | `reports/daily/` |
| `flash` | 盘中速览 | `reports/flash/` |
| `deep` | 专题研究 | `reports/deep/` |
| `other` | 其他 | `reports/other/` |

## 🎨 扩展新分类

如需添加新分类（如"策略周报"），只需：

1. 在 `index.html` 的 `CATEGORIES` 对象中添加：
```js
strategy: { label: '策略', tagClass: 'rt-strategy', breadcrumb: '策略周报' },
```

2. 在侧边栏 HTML 中添加对应的 `nav-item`

3. 创建 `reports/strategy/` 文件夹

4. 在 CSS 中添加标签样式 `.rt-strategy`

## ⌨️ 快捷键

| 快捷键 | 功能 |
|---|---|
| `⌘K` / `Ctrl+K` | 聚焦搜索 |
| `Esc` | 关闭预览 / 收起搜索 |
