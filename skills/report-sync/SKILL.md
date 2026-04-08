---
name: report-sync
description: 将其他 Cowork project 生成的 HTML 报告整合归档到 WislicWorld 站点。触发词："同步报告"、"归档报告"、"sync reports"、"整合报告到WislicWorld"、"有哪些报告没归档"、"把报告同步过来"。任何涉及从 Claude 文件夹扫描 HTML 报告并归入 WislicWorld 的操作都应使用此 skill。
---

# Report Sync — 跨项目报告整合到 WislicWorld

将散落在各 Cowork project 中的 HTML 报告，自动扫描、分类、归档到 WislicWorld 站点。

## 核心路径

| 角色 | 路径 |
|---|---|
| WislicWorld 站点根目录 | 当前挂载的 WislicWorld 文件夹（通常 `/mnt/WislicWorld` 或 cowork 挂载路径） |
| 报告注册表 | `{站点根}/reports.json` |
| 报告存储 | `{站点根}/reports/{category}/` |
| 报告来源（扫描目标） | 同层挂载的 Claude 文件夹下所有子目录，包括 `Projects/`、`ClaudeAnswer/`、`Scheduled/`、`LawSuit/` 等 |

## 分类规则

按文件名和内容自动判断 category：

| 关键词匹配（文件名或标题） | category | 目标文件夹 | 命名规则 |
|---|---|---|---|
| `宏观经济与大类资产日报`、`macro-daily`、`morning` | `daily` | `reports/daily/` | `YYYY-MM-DD.html` |
| `盘中速览`、`flash`、`midday`、`固收+盘中`、`market-thermometer` | `flash` | `reports/flash/` | `描述-YYYY-MM-DD.html` |
| `专题`、`框架`、`分析`、`研究`、`tracker`、`theory`、`technical`、技术分析、地缘、深度 | `deep` | `reports/deep/` | `简短英文描述.html` |
| `周报`、`weekly`、`九周期`、`cycle`、`定位` | `other` | `reports/other/` | `描述-YYYY-MM-DD.html` |
| 无法匹配 | `other` | `reports/other/` | 保留原名（转为英文小写+连字符） |

## 执行流程

### Step 1: 扫描报告来源

运行 `scripts/scan_reports.py` 扫描所有来源目录，对比 `reports.json` 中已注册文件列表，输出未归档报告清单。

```bash
python3 {skill_dir}/scripts/scan_reports.py \
  --source "{claude_folder}" \
  --target "{wislicworld_folder}" \
  --output scan_result.json
```

脚本会输出：
- 发现的 HTML 文件总数
- 已归档数量（在 reports.json 中能匹配到的）
- **待归档清单**：每条包含源路径、建议分类、建议文件名、建议标题、建议日期

### Step 2: 确认归档计划

将待归档清单展示给用户，格式：

```
发现 N 份未归档报告：

1. 宏观经济与大类资产日报_20260408.html
   → daily / 2026-04-08.html / "宏观经济与大类资产日报 2026-04-08"
   
2. 固收+盘中速览_20260407.html
   → flash / fixed-income-flash-2026-04-07.html / "固收+盘中速览 2026-04-07"

3. geoint-iran-tracker.html
   → deep / geoint-iran-tracker.html / "伊朗地缘情报追踪"

确认归档？可逐条修改分类/标题/文件名。
```

用户可以：
- 全部确认
- 排除某些文件
- 修改个别文件的分类/标题/文件名

### Step 3: 执行归档

对确认的每份报告：

1. **复制文件**到 `reports/{category}/{filename}`
2. **在 reports.json 的 reports 数组开头插入新条目**：
   ```json
   {
     "title": "报告标题",
     "category": "分类",
     "date": "YYYY-MM-DD",
     "file": "reports/分类/文件名.html"
   }
   ```
3. reports.json 按 date 倒序排列

### Step 4: 验证与汇总

- 确认所有文件已成功复制（检查文件存在且大小 > 0）
- 确认 reports.json 格式正确（用 python json.loads 验证）
- 输出归档汇总：新增 X 份，daily Y 份 / flash Z 份 / deep W 份 / other V 份
- 提示用户下一步：git add/commit/push 命令（如果有 git 仓库的话）

## 文件名转换规则

中文文件名转英文的规则：
- `宏观经济与大类资产日报_YYYYMMDD` → `YYYY-MM-DD.html`（daily 类固定格式）
- `固收+盘中速览_YYYYMMDD` → `fixed-income-flash-YYYY-MM-DD.html`
- `九周期定位更新_YYYYMMDD` → `nine-cycle-update-YYYY-MM-DD.html`
- `周期定位修正_XXX_YYYYMMDD` → `cycle-revision-XXX-YYYY-MM-DD.html`
- `market-thermometer-YYYY-MM-DD` → 保持原名
- 其他：保持原名或转为小写英文+连字符

日期提取优先级：文件名中的日期 > HTML `<title>` 中的日期 > 文件修改时间

## 注意事项

- 不要重复归档已在 reports.json 中的报告（通过文件名和标题双重比对）
- 归档时保持 HTML 文件原样，不修改内容
- 如果目标路径已存在同名文件，跳过并提醒用户
- data/ 子目录下的 daily-scans 等中间数据文件默认不归档，除非用户明确要求
- weekly-reports 子目录下的周报归档到 other 分类
