#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlowUs 影视资源批量抓取脚本 - Playwright 版本
通过浏览器滚动翻页采集所有可见的影视条目
"""

import asyncio
import json
import re
import os
from playwright.async_api import async_playwright

FLOWUS_URL = "https://flowus.cn/share/40567600-fe76-4ce5-836e-af234c5eb5d3"
OUTPUT_PATH = "E:/主线/主线/正在做的/初恋资源库/data/resources.json"
LOG_PATH = "E:/主线/主线/正在做的/初恋资源库/_scrape/scraped_movies.json"

def parse_title(text):
    """从文本中提取标题"""
    # 匹配 "标题 (年份)" 或 "标题(年份)"
    m = re.search(r'([\u4e00-\u9fa5\w\s\.]+?)\s*\((\d{4})\)', text)
    if m:
        return m.group(1).strip(), m.group(2)
    return text.strip(), ''

def generate_id(title, year=''):
    """生成 kebab-case ID"""
    clean = re.sub(r'[^\u4e00-\u9fa5a-z0-9]', '-', title.lower())
    clean = re.sub(r'-+', '-', clean).strip('-')
    if len(clean) > 25:
        clean = clean[:25]
    suffix = '-' + year[-2:] if year else '-26'
    return clean + suffix

async def scrape_flowus():
    """使用 Playwright 抓取 FlowUs 页面"""
    all_records = []
    seen_titles = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={'width': 1280, 'height': 900})
        
        print(f"[INFO] Opening FlowUs page...")
        await page.goto(FLOWUS_URL, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)
        
        # 点击第一个分类按钮进入列表页
        first_btn = await page.query_selector('button:has-text("全部国产剧"), button:has-text("全部影视")')
        if first_btn:
            print("[INFO] Clicking category button...")
            await first_btn.click()
            await page.wait_for_timeout(2000)
        
        # 滚动收集数据
        max_scrolls = 30  # 最多滚动30次，约300条
        scroll_count = 0
        
        while scroll_count < max_scrolls:
            scroll_count += 1
            print(f"[INFO] Scroll {scroll_count}/{max_scrolls}...")
            
            # 等待内容加载
            await page.wait_for_timeout(1500)
            
            # 收集当前可见的影视卡片
            cards = await page.query_selector_all('article')
            new_count = 0
            
            for card in cards:
                try:
                    text = await card.inner_text()
                    if not text or len(text) < 30:
                        continue
                    
                    # 解析单条记录
                    record = parse_record(text)
                    if record and record['title'] not in seen_titles:
                        seen_titles.add(record['title'])
                        all_records.append(record)
                        new_count += 1
                except:
                    continue
            
            if new_count == 0:
                print(f"[INFO] No new records on this scroll.")
                break
            
            print(f"[INFO] Found {new_count} new records, total: {len(all_records)}")
            
            # 继续滚动
            await page.evaluate('window.scrollBy(0, 800)')
        
        await browser.close()
    
    return all_records

def parse_record(text):
    """解析单条影视记录的文本"""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    record = {}
    
    # 提取标题（包含年份）
    for line in lines:
        m = re.match(r'^([\u4e00-\u9fa5\w\s\.]+?)\s*\((\d{4})\)', line)
        if m:
            record['title'] = m.group(1).strip()
            record['year'] = m.group(2)
            break
    
    if not record.get('title'):
        return None
    
    # 提取各类字段
    field_patterns = {
        'category': r'(?:^|[ \t\n])分类[ \t]*([\u4e00-\u9fa5]+)',
        'type': r'(?:^|[ \t\n])类型[ \t]*([\u4e00-\u9fa5]+(?:、[\u4e00-\u9fa5]+)*)',
        'score': r'TMDB评分[ \t]*(\d+)',
        'quality': r'品质[ \t]*(4K[\w\- ]+)',
        'actors': r'演员[ \t]*([\u4e00-\u9fa5、,，]+)',
        'director': r'导演[ \t]*([\u4e00-\u9fa5、,，]+)',
        'update_info': r'更新信息[ \t]*(更新第?\d+集)',
        'update_date': r'更新日期[ \t]*(\d{4}/\d{2}/\d{2})',
    }
    
    full_text = '\n'.join(lines)
    for key, pattern in field_patterns.items():
        m = re.search(pattern, full_text)
        if m:
            record[key] = m.group(1).strip()
    
    # 提取网盘链接
    links = {}
    quark_m = re.search(r'https?://pan\.quark\.cn/s/[^\s]+', full_text)
    baidu_m = re.search(r'https?://pan\.baidu\.com/s/[^\s]+', full_text)
    xunlei_m = re.search(r'https?://pan\.xunlei\.com/s/[^\s]+', full_text)
    if quark_m:
        links['quark'] = quark_m.group(0)
    if baidu_m:
        links['baidu'] = baidu_m.group(0)
    if xunlei_m:
        links['xunlei'] = xunlei_m.group(0)
    record['links'] = links
    
    # 生成封面图 URL（尝试从 TMDB）
    tmdb_m = re.search(r'tmdb\.org/(?:tv|movie)/(\d+)', full_text)
    if tmdb_m:
        record['cover'] = f"https://image.tmdb.org/t/p/w780/{tmdb_m.group(1)}.jpg"
    elif 'poster' in full_text:
        pass  # 尝试提取 poster URL
    
    # 简化处理：根据标题构造合理内容
    record['summary'] = build_summary(record)
    record['body'] = build_body(record)
    record['tags'] = extract_tags(full_text)
    record['hotness'] = int(record.get('score', 8)) * 1000 + hash(record['title']) % 500
    
    return record

def build_summary(r):
    """构建摘要"""
    parts = []
    if r.get('score'):
        parts.append(f"TMDB {r['score']}分")
    if r.get('quality'):
        parts.append(r['quality'])
    if r.get('category'):
        parts.append(r['category'])
    return ' | '.join(parts) if parts else '持续更新中'

def build_body(r):
    """构建正文"""
    lines = [r['title']]
    if r.get('synopsis'):
        lines.append(r['synopsis'])
    if r.get('director'):
        lines.append(f"导演：{r['director']}")
    if r.get('actors'):
        lines.append(f"主演：{r['actors']}")
    if r.get('score'):
        lines.append(f"评分：TMDB {r['score']}分")
    if r.get('quality'):
        lines.append(f"品质：{r['quality']}")
    if r.get('update_info'):
        lines.append(f"状态：{r['update_info']}")
    return '\n'.join(lines)

def extract_tags(text):
    """从文本中提取标签"""
    m = re.search(r'类型[ \t]*([\u4e00-\u9fa5]+(?:、[\u4e00-\u9fa5]+)*)', text)
    if m:
        return [t.strip() for t in m.group(1).split('、') if t.strip()]
    return ['剧情']

def main():
    print("=" * 60)
    print("FlowUs 影视资源批量抓取工具 v4")
    print("=" * 60)
    
    # 运行异步抓取
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        records = loop.run_until_complete(scrape_flowus())
    finally:
        loop.close()
    
    if not records:
        print("[WARN] No records scraped! Using manual fallback data.")
        records = get_fallback_data()
    
    print(f"\n抓取到 {len(records)} 条影视记录")
    
    # 保存原始抓取结果
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"原始数据已保存到: {LOG_PATH}")
    
    # 转换为资源库格式并合并
    convert_and_merge(records)

def get_fallback_data():
    """手动录入的备份数据（当抓取失败时使用）"""
    return [
        {"title": "谷雨 (2026)", "category": "国产剧", "score": "9", "quality": "4K WEB-DL HDR10 H265 AAC 2.0"},
        {"title": "今天是太阳雨 (2026)", "category": "国产剧", "score": "0", "quality": "4K WEB-DL H264 AAC 2.0"},
        {"title": "玫瑰战争 (2026)", "category": "国产剧", "score": "8", "quality": "4K WEB-DL HDR10 H265 DDP 2.0"},
        {"title": "十万狂花入梦来 (2026)", "category": "国产剧", "score": "10", "quality": "4K WEB-DL H265 AAC 2.0"},
        {"title": "欲望的陷阱 (2026)", "category": "日韩剧", "score": "10", "quality": "4K WEB-DL HDR10"},
    ]

def convert_and_merge(raw_records):
    """将抓取的记录转换为 resources.json 格式并合并"""
    # 读取现有资源
    with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    existing_ids = {r['id'] for r in existing}
    new_entries = []
    
    for r in raw_records:
        cid = generate_id(r['title'], r.get('year', ''))
        if cid in existing_ids:
            continue
        
        # 构建条目
        entry = {
            "id": cid,
            "title": r['title'],
            "category": r.get('category', '国产剧'),
            "tags": r.get('tags', ['剧情']),
            "summary": r.get('summary', '持续更新中'),
            "body": r.get('body', r['title']),
            "cover": r.get('cover', ''),
            "hotness": r.get('hotness', 8000),
            "time": r.get('update_date', '今日更新').replace('/', '-') if r.get('update_date') else '今日更新',
            "price": "免费"
        }
        
        # 添加分享链接
        links = r.get('links', {})
        if links.get('quark'):
            entry['share'] = links['quark']
        alt_links = []
        if links.get('baidu'):
            alt_links.append({'netdisk': '百度', 'url': links['baidu']})
        if links.get('xunlei'):
            alt_links.append({'netdisk': '迅雷', 'url': links['xunlei']})
        if alt_links:
            entry['share_alt'] = alt_links
        
        new_entries.append(entry)
    
    # 合并
    all_resources = existing + new_entries
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_resources, f, ensure_ascii=False, indent=2)
    
    # 统计
    cats = {}
    for r in all_resources:
        cat = r.get('category', '未分类')
        cats[cat] = cats.get(cat, 0) + 1
    
    print(f"\n{'='*60}")
    print("导入完成!")
    print(f"  原有资源: {len(existing)} 条")
    print(f"  新增影视: {len(new_entries)} 条")
    print(f"  当前总数: {len(all_resources)} 条")
    print(f"\n分类统计:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} 条")

if __name__ == '__main__':
    main()
