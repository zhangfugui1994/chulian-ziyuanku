#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人人电影网(rirdynb.com) 影视资源批量抓取脚本
从已抓取的HTML文件中解析并转换数据
"""

import json
import re
import os
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

BASE_DIR = r'E:\主线\主线\正在做的\初恋资源库'
SCRAPE_DIR = os.path.join(BASE_DIR, '_scrape')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'resources.json')

class RrdynbParser(HTMLParser):
    """解析人人电影网HTML"""
    
    def __init__(self):
        super().__init__()
        self.in_link = False
        self.in_li = False
        self.current_href = ''
        self.current_title = ''
        self.current_text = ''
        self.records = []
        self.list_stack = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'a':
            href = attrs_dict.get('href', '')
            if '/plus/view.php?aid=' in href or '/movie/' in href or '/dianshiju/' in href:
                self.in_link = True
                self.current_href = href
                self.current_title = ''
                self.current_text = ''
                
        if tag == 'li' and self.in_link:
            self.in_li = True
            
    def handle_endtag(self, tag):
        if tag == 'a' and self.in_link:
            self.in_link = False
            # 尝试提取标题
            title = self.current_title.strip()
            if title and len(title) > 2:
                record = self.parse_record(title, self.current_href)
                if record:
                    self.records.append(record)
                    
        if tag == 'li' and self.in_li:
            self.in_li = False
            
    def handle_data(self, data):
        if self.in_link:
            text = data.strip()
            if text:
                self.current_text += text
                if not self.current_title:
                    self.current_title = text
                    
    def parse_record(self, title, url):
        """解析单条记录"""
        # 清理标题（去除《》等符号）
        clean_title = title.replace('《', '').replace('》', '').replace('百度云网盘夸', '').replace('百度云', '').strip()
        
        # 提取年份
        year_match = re.search(r'\((\d{4})\)', clean_title)
        year = year_match.group(1) if year_match else ''
        
        # 生成ID
        id_part = re.sub(r'[^\u4e00-\u9fa5a-z0-9]', '-', clean_title.lower())
        id_part = re.sub(r'-+', '-', id_part).strip('-')
        rid = f"rrdy-{id_part[:20]}-{year}"
        
        # 判断类型
        if '/movie/' in url or '电影' in title:
            category = '华语电影'
        elif '/dianshiju/' in url:
            category = '国产剧'
        else:
            category = '其他'
            
        return {
            'id': rid,
            'title': clean_title.split('(')[0].strip(),
            'year': year,
            'category': category,
            'url': url,
            'raw_title': title
        }


def parse_html_file(filepath):
    """解析单个HTML文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    parser = RrdynbParser()
    parser.feed(html)
    return parser.records


def extract_links_from_html(filepath):
    """使用正则提取链接和标题"""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    records = []
    
    # 匹配视频详情页链接
    pattern = r'<a\s+[^>]*href="(/plus/view\.php\?aid=\d+|/movie/\d+/[^"]+|/dianshiju/\d+/[^"]+)"[^>]*>(.*?)</a>'
    matches = re.findall(pattern, html, re.DOTALL)
    
    seen = set()
    for href, title_html in matches:
        # 清理HTML标签获取纯文本
        plain_title = re.sub(r'<[^>]+>', '', title_html).strip()
        plain_title = re.sub(r'\s+', ' ', plain_title)
        
        if not plain_title or plain_title in seen:
            continue
            
        # 清理标题
        clean = plain_title.replace('《', '').replace('》', '').replace('百度云', '').replace('网盘', '').replace('夸克', '').strip()
        
        if len(clean) < 3:
            continue
            
        seen.add(plain_title)
        
        # 提取年份
        year_match = re.search(r'\((\d{4})\)', clean)
        year = year_match.group(1) if year_match else ''
        
        # 生成ID
        id_part = re.sub(r'[^\u4e00-\u9fa5a-z0-9]', '-', clean.lower())
        id_part = re.sub(r'-+', '-', id_part).strip('-')
        rid = f"rrdy-{id_part[:25]}"
        
        # 判断分类
        if '/movie/' in href or '电影' in plain_title:
            category = '华语电影'
        elif '/dianshiju/' in href:
            category = '国产剧'
        elif '/dongman/' in href:
            category = '动画电影'
        else:
            category = '其他'
        
        records.append({
            'id': rid,
            'title': clean.split('(')[0].strip(),
            'year': year,
            'category': category,
            'url': 'https://www.rrdynb.com' + href,
            'source': 'rrdynb'
        })
    
    return records


def main():
    print("=" * 60)
    print("人人电影网(rirdynb.com) 批量抓取工具")
    print("=" * 60)
    
    all_records = []
    seen_ids = set()
    
    # 解析各个HTML文件
    files_to_parse = [
        ('rrdynb_home.html', '首页'),
        ('rrdynb_movie.html', '电影页'),
        ('rrdynb_tv.html', '电视剧页'),
    ]
    
    for filename, desc in files_to_parse:
        filepath = os.path.join(SCRAPE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[WARN] {desc}: 文件不存在 {filepath}")
            continue
            
        print(f"\n[{desc}] 解析 {filename}...")
        records = extract_links_from_html(filepath)
        
        new_count = 0
        for r in records:
            if r['id'] not in seen_ids:
                seen_ids.add(r['id'])
                all_records.append(r)
                new_count += 1
        
        print(f"  找到 {len(records)} 条记录, 新增 {new_count} 条")
    
    print(f"\n总计: {len(all_records)} 条唯一记录")
    
    if not all_records:
        print("[ERROR] 未提取到任何记录!")
        return
    
    # 统计分类
    cats = {}
    for r in all_records:
        cat = r.get('category', '其他')
        cats[cat] = cats.get(cat, 0) + 1
    
    print("\n分类统计:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} 条")
    
    # 显示前20条示例
    print("\n前20条示例:")
    for i, r in enumerate(all_records[:20], 1):
        print(f"  {i}. [{r['category']}] {r['title'][:30]} ({r.get('year','')})")
    
    # 保存原始数据
    raw_path = os.path.join(SCRAPE_DIR, 'rrdynb_raw.json')
    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"\n原始数据已保存到: {raw_path}")
    
    # 转换为资源库格式
    convert_to_resources(all_records)


def convert_to_resources(records):
    """转换为 resources.json 格式"""
    # 读取现有资源
    with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    existing_ids = {r['id'] for r in existing}
    new_entries = []
    
    for r in records:
        # 避免与现有资源冲突
        cid = r['id']
        if cid in existing_ids:
            continue
            
        entry = {
            "id": cid,
            "title": r['title'],
            "category": r['category'],
            "tags": ['剧情'],
            "summary": f"{r['category']} | 来自人人电影网",
            "body": f"{r['title']} ({r.get('year', '未知年')})\n\n来源: {r['url']}",
            "cover": "",
            "hotness": 5000,
            "time": "今日更新",
            "price": "免费",
            "share": r['url']
        }
        
        new_entries.append(entry)
    
    # 合并
    all_resources = existing + new_entries
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_resources, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"导入完成!")
    print(f"  原有资源: {len(existing)} 条")
    print(f"  新增影视: {len(new_entries)} 条")
    print(f"  当前总数: {len(all_resources)} 条")
    
    # 最终统计
    final_cats = {}
    for r in all_resources:
        cat = r.get('category', '未分类')
        final_cats[cat] = final_cats.get(cat, 0) + 1
    
    print(f"\n📊 最终分类统计:")
    for cat, count in sorted(final_cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} 条")


if __name__ == '__main__':
    main()
