---

## 🔄 WislicWorld 自动归档

每次生成 HTML 报告后，必须自动将报告归档到 WislicWorld 站点。这是强制步骤，不需要用户额外确认。

### 归档路径发现

按以下优先级查找 WislicWorld 站点目录：
1. 当前挂载目录中是否有 `WislicWorld/` 文件夹（查找 `reports.json` 文件确认）
2. 同级挂载目录中是否有 `WislicWorld/` 文件夹
3. 如果找不到，将报告保存到当前输出目录并提示用户：「报告已生成，但未找到 WislicWorld 挂载目录，请手动归档或在下次会话中挂载 WislicWorld 文件夹。」

### 分类规则

根据报告内容自动判断分类：

| 报告类型 | category | 目标文件夹 | 文件命名 |
|---|---|---|---|
| 宏观日报（晨间日报） | `daily` | `reports/daily/` | `YYYY-MM-DD.html` |
| 盘中速览 / 市场温度计 | `flash` | `reports/flash/` | `描述-YYYY-MM-DD.html` |
| 专题研究 / 框架分析 / 深度报告 | `deep` | `reports/deep/` | `英文简述.html` |
| 周报 / 周期更新 / 其他 | `other` | `reports/other/` | `描述-YYYY-MM-DD.html` |

### 文件命名转换

- 文件名只用小写英文字母、数字、连字符，不用中文和空格
- `宏观经济与大类资产日报` → `YYYY-MM-DD.html`（daily 类统一格式）
- `固收+盘中速览` → `fixed-income-flash-YYYY-MM-DD.html`
- `市场温度计` → `market-thermometer-YYYY-MM-DD.html`
- `九周期定位更新` → `nine-cycle-update-YYYY-MM-DD.html`
- `周期定位修正` → `cycle-revision-topic-YYYY-MM-DD.html`
- `周报` → `weekly-macro-WXX-YYYY.html`（XX为周数）
- 其他：取报告主题的英文缩写 + 日期

### 归档执行步骤

生成 HTML 报告后，立即执行以下操作：

**Step 1** — 确定分类和文件名（根据上表自动判断，无需询问用户）

**Step 2** — 复制 HTML 文件到目标路径：
`cp "生成的报告.html" "{WislicWorld}/reports/{category}/{filename}"`

**Step 3** — 用 Python 更新 reports.json（在 reports 数组中插入新条目，按日期倒序排列）：

```python
import json
reports_json = "{WislicWorld}/reports.json"
with open(reports_json, 'r') as f:
    data = json.load(f)
new_entry = {
    "title": "报告中文标题",
    "category": "分类",
    "date": "YYYY-MM-DD",
    "file": "reports/分类/文件名.html"
}
data['reports'].insert(0, new_entry)
data['reports'].sort(key=lambda x: x.get('date', ''), reverse=True)
with open(reports_json, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

**Step 4** — 验证：确认文件已复制且大小 > 0，确认 reports.json 格式正确（json.loads 不报错）

**Step 5** — 在报告输出末尾附加一行归档确认：
> ✅ 已归档到 WislicWorld → {category}/{filename}

### 防重复

归档前检查：
- `reports.json` 中是否已有相同 `file` 路径的条目
- 目标文件是否已存在

如果重复，跳过归档并提示「该报告已归档」。

### 归档失败处理

如果归档失败（路径不存在、权限不足等），不要中断报告生成流程。将报告正常输出给用户，并在末尾提示归档失败原因。
