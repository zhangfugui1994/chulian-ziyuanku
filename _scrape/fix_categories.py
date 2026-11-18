#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复人人电影网抓取数据的分类
"""
import json
import re
import os

BASE_DIR = r'E:\主线\主线\正在做的\初恋资源库'
RAW_PATH = os.path.join(BASE_DIR, '_scrape', 'rrdynb_raw.json')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'resources.json')

def classify_record(record):
    """根据标题和URL重新分类"""
    title = record.get('title', '')
    url = record.get('url', '')
    
    # 动漫相关
    anime_keywords = ['JOJO', '火影', '鬼灭', '进击', '咒术', '海贼', '柯南', '名侦探', 
                      '灌篮', '网球', '数码', '皮卡丘', '精灵宝可梦', '龙珠', 'EVA', 
                      '新世纪', ' Evangelion', '葬送的芙莉莲', '魔法少女', '奇犽']
    if any(k in title for k in anime_keywords) or '/dongman/' in url:
        return '动画电影'
    
    # 韩剧/日剧
    if any(c in title for c in ['韩国', '韩剧', '韩语']) or '한' in title or '일' in title:
        return '日韩剧'
    if any(c in title for c in ['日剧', '日本']) and ('季' in title or '集' in title):
        return '日韩剧'
    
    # 美剧/欧美剧
    if any(k in title for k in ['美剧', '英国', '德国', '法国', '西班牙', '意大利']):
        return '欧美剧'
    if any(k in title for k in ['黑袍纠察', '亢奋', '权力游戏', '怪奇物语', '绝命毒', 
                                '风骚律师', '行尸走肉', '西部世界', '曼达洛人', '卢克凯奇',
                                '王冠', '纸牌屋', '绯闻女孩']):
        return '欧美剧'
    if '季' in title and any(k in title for k in ['第二', '第三', '第四', '第五', '第六']):
        # 可能是美剧或日韩剧，看关键词判断
        if not any(c in title for c in ['国产', '大陆', '中国']):
            return '欧美剧'
    
    # 国产剧（含港剧）
    if '/dianshiju/' in url or any(c in title for c in ['国产', '大陆', '内地', 'TVB', '港剧']):
        return '国产剧'
    if '续集' in title or '第X季' in title:
        return '国产剧'
    
    # 华语电影
    if '/movie/' in url:
        return '华语电影'
    if '电影' in title or any(k in title for k in ['2024', '2025', '2026', '2027']):
        # 有年份的可能是电影
        if '季' not in title and '集' not in title:
            return '华语电影'
    
    return '华语电影'  # 默认归为电影

def main():
    print("修复分类...")
    
    # 读取原始数据
    with open(RAW_PATH, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 重新分类
    fixed_data = []
    for r in raw_data:
        old_cat = r.get('category', '')
        new_cat = classify_record(r)
        r['category'] = new_cat
        fixed_data.append(r)
        if old_cat != new_cat:
            print(f"  {r['title'][:30]}: {old_cat} -> {new_cat}")
    
    # 统计
    cats = {}
    for r in fixed_data:
        cat = r.get('category', '未分类')
        cats[cat] = cats.get(cat, 0) + 1
    
    print(f"\n修复后分类:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} 条")
    
    # 保存固定数据
    fixed_path = os.path.join(BASE_DIR, '_scrape', 'rrdynb_fixed.json')
    with open(fixed_path, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    
    # 合并到 resources.json
    with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    existing_ids = {r['id'] for r in existing}
    new_entries = []
    
    for r in fixed_data:
        # 生成新ID（带来源标记）
        cid = r['id'].replace('rrdy-', 'rrdy-fix-')
        if cid in existing_ids:
            continue
        
        entry = {
            "id": cid,
            "title": r['title'],
            "category": r['category'],
            "tags": ['剧情'],
            "summary": f"{r['category']} | 来自人人电影网",
            "body": f"{r['title']}\n\n来源: {r['url']}",
            "cover": "",
            "hotness": 5000,
            "time": "今日更新",
            "price": "免费",
            "share": r['url']
        }
        new_entries.append(entry)
    
    all_resources = existing + new_entries
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_resources, f, ensure_ascii=False, indent=2)
    
    # 最终统计
    final_cats = {}
    for r in all_resources:
        cat = r.get('category', '未分类')
        final_cats[cat] = final_cats.get(cat, 0) + 1
    
    print(f"\n{'='*60}")
    print(f"导入完成!")
    print(f"  原有资源: {len(existing)} 条")
    print(f"  新增影视: {len(new_entries)} 条")
    print(f"  当前总数: {len(all_resources)} 条")
    
    print(f"\n最终分类统计:")
    for cat, count in sorted(final_cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} 条")
    
    # 显示影视类示例
    movies = [r for r in all_resources if r.get('category') in ['国产剧', '日韩剧', '欧美剧', '华语电影', '动画电影']]
    print(f"\n影视资源共 {len(movies)} 条 (已排序按热度)")
    for r in sorted(movies, key=lambda x: -x.get('hotness', 0))[:20]:
        print(f"  [{r['category']}] {r['title'][:35]}")

if __name__ == '__main__':
    main()
