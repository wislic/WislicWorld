# WislicAIWorld 归档工作流提示词

> 本文件定义了 Claude 将 HTML 报告归档到 WislicAIWorld 的标准流程。
> 当用户说"请归档"、"归档这份报告"、"存到 WislicAIWorld"时，Claude 应遵循此流程。

---

## 站点信息

- **远程地址**：https://wislic.github.io/WislicAIWorld/
- **GitHub 仓库**：https://github.com/wislic/WislicAIWorld
- **本地路径**：`/Users/wislic/Documents/Claude/WislicAIWorld`

## 目录结构

```
WislicAIWorld/
├── index.html          ← 主站点（无需修改）
├── reports.json        ← 报告注册表（每次归档需更新）
├── archive-prompt.md   ← 本文件
├── reports/
│   ├── daily/          ← 宏观日报
│   ├── flash/          ← 盘中速览
│   ├── deep/           ← 专题研究
│   └── other/          ← 其他报告
└── README.md
```

## 分类规则

| category | 含义 | 目标文件夹 | 文件命名规则 |
|---|---|---|---|
| `daily` | 宏观日报（晨间宏观经济与大类资产日报） | `reports/daily/` | `YYYY-MM-DD.html` |
| `flash` | 盘中速览（11:30 交易时段快照） | `reports/flash/` | `YYYY-MM-DD.html` |
| `deep` | 专题研究（地缘分析、资产配置框架、行业研究等） | `reports/deep/` | `简短英文描述.html`（如 `oil-sector-2026.html`） |
| `other` | 其他（不属于以上三类的任何 HTML 报告） | `reports/other/` | `简短英文描述.html` |

## 归档流程

当用户要求归档一份 HTML 报告时，Claude 按以下步骤执行：

### Step 1：确认归档信息

向用户确认以下信息（如果从上下文能推断则直接确认，无需反复提问）：

- **报告标题**：中文标题，用于在站点显示（如"宏观日报 2026-03-29"）
- **分类**：`daily` / `flash` / `deep` / `other`
- **日期**：报告对应的日期，格式 `YYYY-MM-DD`
- **文件名**：按命名规则生成

### Step 2：生成 HTML 文件

将报告内容输出为完整的独立 HTML 文件。确保：

- 文件是完整的 `<!DOCTYPE html>` 文档
- 包含 `<meta charset="UTF-8">` 和 `<meta name="viewport">`
- 所有样式内联（`<style>` 标签），不依赖外部 CSS 文件
- 所有脚本内联（`<script>` 标签），不依赖外部 JS 文件
- 外部字体通过 Google Fonts CDN 引入（可选，非必须）
- 文件可在浏览器中独立打开，不依赖其他文件

### Step 3：输出归档文件

将 HTML 文件保存到 `/mnt/user-data/outputs/` 供用户下载。

### Step 4：输出 reports.json 更新片段

告诉用户需要在 `reports.json` 的 `"reports"` 数组**开头**插入的新条目：

```json
{
  "title": "报告标题",
  "category": "分类",
  "date": "YYYY-MM-DD",
  "file": "reports/分类/文件名.html"
}
```

### Step 5：给出终端命令

给用户一段可以直接复制粘贴的终端命令，完成文件放置、JSON 更新和 Git 推送：

```bash
# 1. 将下载的 HTML 文件移动到目标位置
mv ~/Downloads/文件名.html /Users/wislic/Documents/Claude/WislicAIWorld/reports/分类/文件名.html

# 2. 推送到 GitHub
cd /Users/wislic/Documents/Claude/WislicAIWorld
git add .
git commit -m "add: 报告标题"
git push
```

**注意**：reports.json 需要用户手动编辑或由 Claude 提供更新后的完整文件。如果用户有 Python 环境，也可用 add-report.sh 脚本自动化。

---

## 批量归档流程

当需要一次归档多份报告时：

1. 为每份报告生成 HTML 文件并输出到 `/mnt/user-data/outputs/`
2. 提供更新后的完整 `reports.json`（包含所有新增条目）
3. 给出一段合并的终端命令

---

## 示例对话

**用户**：请把刚才的布油分析报告归档到 WislicAIWorld

**Claude**：
> 确认归档信息：
> - 标题：布油突破100美元后A股走势分析
> - 分类：deep（专题研究）
> - 日期：2026-03-29
> - 文件名：oil-100-ashare.html
> - 路径：reports/deep/oil-100-ashare.html
>
> [生成并输出 HTML 文件]
>
> 请在终端执行：
> ```bash
> mv ~/Downloads/oil-100-ashare.html /Users/wislic/Documents/Claude/WislicAIWorld/reports/deep/
> cd /Users/wislic/Documents/Claude/WislicAIWorld
> # 编辑 reports.json，在 reports 数组开头添加上述条目
> git add .
> git commit -m "add: 布油突破100美元后A股走势分析"
> git push
> ```

---

## 注意事项

- 每次归档后，网站会在 1-2 分钟内自动更新（GitHub Pages 自动部署）
- reports.json 中的报告按 date 倒序排列（最新的在最前面）
- 文件名只使用小写英文字母、数字和连字符，不使用中文和空格
- 同一天可以有多份同类报告，文件名加后缀区分（如 `2026-03-29-v2.html`）
- deep 和 other 类报告的文件名应简短描述内容，便于识别
