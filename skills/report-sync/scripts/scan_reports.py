#!/usr/bin/env python3
"""
scan_reports.py — 扫描 Claude 项目文件夹中的 HTML 报告，
对比 WislicWorld/reports.json，输出未归档清单。

用法:
  python3 scan_reports.py --source <claude_folder> --target <wislicworld_folder> [--output scan_result.json]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser


# ── 分类规则 ──────────────────────────────────────────

CATEGORY_RULES = [
    # (pattern_on_filename_or_title, category)
    (r'宏观经济与大类资产日报|macro[-_]daily|morning[-_]market', 'daily'),
    (r'盘中速览|flash|midday|固收\+盘中|market[-_]thermometer', 'flash'),
    (r'周报|weekly|九周期|cycle|定位', 'other'),
    (r'专题|框架|分析|研究|tracker|theory|technical|技术分析|地缘|深度|tearsheet', 'deep'),
]

# 文件名翻译映射
FILENAME_TRANSLATIONS = {
    '宏观经济与大类资产日报': 'macro-daily',
    '固收+盘中速览': 'fixed-income-flash',
    '九周期定位更新': 'nine-cycle-update',
    '周期定位修正': 'cycle-revision',
    'AI投研团队实战研判': 'ai-research-tactical',
    'AI黄金投研团队': 'gold-research',
    '碳酸锂期货技术分析': 'lithium-carbonate-analysis',
}

# 默认跳过的路径模式
SKIP_PATTERNS = [
    r'/data/daily-scans/',
    r'/\.git/',
    r'/\.DS_Store',
    r'/node_modules/',
]


class TitleExtractor(HTMLParser):
    """从 HTML 中提取 <title> 内容"""
    def __init__(self):
        super().__init__()
        self._in_title = False
        self.title = ''

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'title':
            self._in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == 'title':
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()


def extract_title_from_html(filepath):
    """从 HTML 文件中提取标题"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(8192)  # 只读前 8KB
        parser = TitleExtractor()
        parser.feed(content)
        return parser.title if parser.title else None
    except Exception:
        return None


def extract_date(filename, html_title=None, filepath=None):
    """从各种来源提取日期"""
    # 尝试从文件名提取 YYYYMMDD
    m = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
    if m:
        return f'{m.group(1)}-{m.group(2)}-{m.group(3)}'

    # 尝试从文件名提取 YYYY-MM-DD
    m = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if m:
        return m.group(1)

    # 尝试从 HTML 标题提取
    if html_title:
        m = re.search(r'(\d{4})[.-](\d{2})[.-](\d{2})', html_title)
        if m:
            return f'{m.group(1)}-{m.group(2)}-{m.group(3)}'
        m = re.search(r'(\d{4})(\d{2})(\d{2})', html_title)
        if m:
            return f'{m.group(1)}-{m.group(2)}-{m.group(3)}'

    # 使用文件修改时间
    if filepath:
        try:
            mtime = os.path.getmtime(filepath)
            return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except Exception:
            pass

    return datetime.now().strftime('%Y-%m-%d')


def classify_report(filename, html_title=None):
    """根据文件名和标题判断分类"""
    text = f'{filename} {html_title or ""}'
    for pattern, category in CATEGORY_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return category
    return 'other'


def generate_target_filename(filename, category, date_str):
    """生成目标文件名"""
    basename = Path(filename).stem

    # daily 类：统一用日期
    if category == 'daily' and date_str:
        return f'{date_str}.html'

    # 尝试翻译中文文件名
    for cn, en in FILENAME_TRANSLATIONS.items():
        if cn in basename:
            rest = basename.replace(cn, '').strip('_- ')
            # 提取日期部分移除
            rest = re.sub(r'\d{8}', '', rest).strip('_- ')
            if date_str:
                return f'{en}-{date_str}.html'
            return f'{en}.html'

    # 已经是英文：小写 + 连字符
    if re.match(r'^[a-zA-Z0-9_\-. ]+$', basename):
        clean = re.sub(r'[_\s]+', '-', basename.lower()).strip('-')
        return f'{clean}.html'

    # 中文文件名：保持拼音化或直接用
    clean = re.sub(r'[_\s]+', '-', basename).strip('-')
    return f'{clean}.html'


def generate_title(filename, html_title, category, date_str):
    """生成显示标题"""
    if html_title and len(html_title) < 80:
        # 清理 HTML 标题
        title = re.sub(r'\s*[|·—-]\s*WislicWorld.*$', '', html_title).strip()
        if title:
            return title

    basename = Path(filename).stem
    # 去掉日期部分
    clean = re.sub(r'[_-]?\d{8}', '', basename).strip('_- ')
    if clean:
        return f'{clean} {date_str}' if date_str else clean
    return basename


def should_skip(filepath):
    """判断是否应跳过此文件"""
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, filepath):
            return True
    return False


def load_existing_reports(target_dir):
    """加载已归档报告列表"""
    reports_json = os.path.join(target_dir, 'reports.json')
    if not os.path.exists(reports_json):
        return set(), set()

    with open(reports_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 收集已注册的文件路径和标题
    registered_files = set()
    registered_titles = set()
    for r in data.get('reports', []):
        registered_files.add(r.get('file', ''))
        registered_files.add(os.path.basename(r.get('file', '')))
        registered_titles.add(r.get('title', ''))

    return registered_files, registered_titles


def scan_source(source_dir, target_dir):
    """扫描源目录中的所有 HTML 文件"""
    registered_files, registered_titles = load_existing_reports(target_dir)

    results = []
    total_html = 0
    already_archived = 0

    for root, dirs, files in os.walk(source_dir):
        # 跳过 WislicWorld 自身（避免重复扫描）
        rel = os.path.relpath(root, source_dir)
        if 'WislicWorld' in rel.split(os.sep)[:2] and 'WislicAIWorld' not in rel:
            continue

        for fname in sorted(files):
            if not fname.lower().endswith('.html'):
                continue

            filepath = os.path.join(root, fname)
            if should_skip(filepath):
                continue

            total_html += 1

            # 检查是否已归档
            html_title = extract_title_from_html(filepath)
            date_str = extract_date(fname, html_title, filepath)
            category = classify_report(fname, html_title)
            target_fname = generate_target_filename(fname, category, date_str)
            target_path = f'reports/{category}/{target_fname}'

            # 判断是否已归档
            if (target_path in registered_files or
                target_fname in registered_files or
                fname in registered_files):
                already_archived += 1
                continue

            # 通过标题匹配检查
            title = generate_title(fname, html_title, category, date_str)
            if title in registered_titles:
                already_archived += 1
                continue

            # 检查目标文件是否已存在
            target_full = os.path.join(target_dir, target_path)
            exists = os.path.exists(target_full)

            results.append({
                'source': filepath,
                'source_relative': os.path.relpath(filepath, source_dir),
                'filename': fname,
                'html_title': html_title,
                'suggested_category': category,
                'suggested_filename': target_fname,
                'suggested_title': title,
                'suggested_date': date_str,
                'target_path': target_path,
                'target_exists': exists,
                'file_size': os.path.getsize(filepath),
            })

    return {
        'total_html_found': total_html,
        'already_archived': already_archived,
        'pending': results,
        'pending_count': len(results),
        'source_dir': source_dir,
        'target_dir': target_dir,
        'scan_time': datetime.now().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description='扫描未归档的 HTML 报告')
    parser.add_argument('--source', required=True, help='报告来源目录（Claude 文件夹）')
    parser.add_argument('--target', required=True, help='WislicWorld 站点目录')
    parser.add_argument('--output', default=None, help='输出 JSON 文件路径')
    args = parser.parse_args()

    if not os.path.isdir(args.source):
        print(f'❌ 源目录不存在: {args.source}', file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(args.target):
        print(f'❌ 目标目录不存在: {args.target}', file=sys.stderr)
        sys.exit(1)

    result = scan_source(args.source, args.target)

    # 输出摘要
    print(f'\n📊 扫描完成')
    print(f'   HTML 文件总数: {result["total_html_found"]}')
    print(f'   已归档: {result["already_archived"]}')
    print(f'   待归档: {result["pending_count"]}')

    if result['pending']:
        print(f'\n📋 待归档报告:')
        for i, r in enumerate(result['pending'], 1):
            status = ' ⚠️ 目标已存在' if r['target_exists'] else ''
            print(f'   {i}. {r["source_relative"]}')
            print(f'      → {r["suggested_category"]} / {r["suggested_filename"]} / "{r["suggested_title"]}"{status}')

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f'\n💾 结果已保存到: {args.output}')

    return result


if __name__ == '__main__':
    main()
