#!/usr/bin/env python3
"""
sync_reports.py — 根据确认后的归档计划，执行文件复制和 reports.json 更新。

用法:
  python3 sync_reports.py --plan sync_plan.json --target <wislicworld_folder>

sync_plan.json 格式（由 scan_reports.py 的 pending 列表筛选后生成）:
[
  {
    "source": "/absolute/path/to/file.html",
    "category": "daily",
    "filename": "2026-04-08.html",
    "title": "宏观经济与大类资产日报 2026-04-08",
    "date": "2026-04-08"
  }
]
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime


def execute_sync(plan_file, target_dir):
    """执行归档同步"""
    with open(plan_file, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    reports_json_path = os.path.join(target_dir, 'reports.json')

    # 加载现有 reports.json
    with open(reports_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = {'success': [], 'skipped': [], 'errors': []}
    new_entries = []

    for item in plan:
        source = item['source']
        category = item['category']
        filename = item['filename']
        title = item['title']
        date = item['date']

        target_subdir = os.path.join(target_dir, 'reports', category)
        target_file = os.path.join(target_subdir, filename)
        relative_path = f'reports/{category}/{filename}'

        # 检查源文件
        if not os.path.exists(source):
            results['errors'].append({
                'file': filename, 'reason': f'源文件不存在: {source}'
            })
            continue

        # 检查目标是否已存在
        if os.path.exists(target_file):
            results['skipped'].append({
                'file': filename, 'reason': '目标文件已存在'
            })
            continue

        # 确保目标目录存在
        os.makedirs(target_subdir, exist_ok=True)

        # 复制文件
        try:
            shutil.copy2(source, target_file)

            # 验证复制成功
            if os.path.exists(target_file) and os.path.getsize(target_file) > 0:
                results['success'].append({
                    'file': filename,
                    'category': category,
                    'title': title,
                    'path': relative_path,
                })

                new_entries.append({
                    'title': title,
                    'category': category,
                    'date': date,
                    'file': relative_path,
                })
            else:
                results['errors'].append({
                    'file': filename, 'reason': '复制后文件为空或不存在'
                })
        except Exception as e:
            results['errors'].append({
                'file': filename, 'reason': str(e)
            })

    # 更新 reports.json
    if new_entries:
        # 插入到数组开头
        data['reports'] = new_entries + data.get('reports', [])

        # 按日期倒序排列
        data['reports'].sort(key=lambda x: x.get('date', ''), reverse=True)

        # 写入
        with open(reports_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 验证 JSON 格式
        with open(reports_json_path, 'r', encoding='utf-8') as f:
            json.load(f)  # 如果格式错误会抛异常

    # 输出汇总
    print(f'\n✅ 归档完成')
    print(f'   成功: {len(results["success"])} 份')
    if results['skipped']:
        print(f'   跳过: {len(results["skipped"])} 份')
    if results['errors']:
        print(f'   失败: {len(results["errors"])} 份')

    # 按分类统计
    cat_counts = {}
    for s in results['success']:
        cat = s['category']
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    if cat_counts:
        parts = [f'{v} → {k}' for k, v in sorted(cat_counts.items())]
        print(f'   分类: {" / ".join(parts)}')

    if results['success']:
        print(f'\n📝 已更新 reports.json，新增 {len(results["success"])} 条记录')

    if results['errors']:
        print(f'\n⚠️ 以下文件归档失败:')
        for e in results['errors']:
            print(f'   - {e["file"]}: {e["reason"]}')

    return results


def main():
    parser = argparse.ArgumentParser(description='执行报告归档同步')
    parser.add_argument('--plan', required=True, help='归档计划 JSON 文件')
    parser.add_argument('--target', required=True, help='WislicWorld 站点目录')
    args = parser.parse_args()

    if not os.path.isfile(args.plan):
        print(f'❌ 计划文件不存在: {args.plan}', file=sys.stderr)
        sys.exit(1)

    results = execute_sync(args.plan, args.target)

    # 返回状态码
    if results['errors']:
        sys.exit(1)
    return 0


if __name__ == '__main__':
    main()
