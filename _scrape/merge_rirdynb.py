#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人人电影网数据清洗和合并脚本
"""
import json
import os

BASE_DIR = r'E:\主线\主线\正在做的\初恋资源库'
RAW_PATH = os.path.join(BASE_DIR, '_scrape', 'rrdynb_raw.json')
FIXED_PATH = os.path.join(BASE_DIR, '_scrape', 'rrdynb_fixed.json')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'resources.json')

def classify_record(record):
    """根据标题和URL重新分类"""
    title = record.get('title', '')
    url = record.get('url', '')
    
    # 动漫相关
    anime_keywords = ['JOJO', '火影', '鬼灭', '进击', '咒术', '海贼', '柯南', 
                      '龙珠', 'EVA', '葬送的芙莉莲', '魔法少女', '奇犽', '数码']
    if any(k in title for k in anime_keywords) or '/dongman/' in url:
        return '动画电影'
    
    # 美剧/欧美剧关键词
    us_keywords = ['黑袍纠察', '亢奋', '权力游戏', '怪奇物语', '绝命毒师', 
                   '风骚律师', '行尸走肉', '西部世界', '曼达洛人', '王冠', '纸牌屋']
    if any(k in title for k in us_keywords):
        return '欧美剧'
    
    # 韩剧/日剧
    if any(c in title for c in ['韩国', '韩剧', '韩语']) or '한' in title or '일' in title:
        return '日韩剧'
    if any(c in title for c in ['日剧', '日本']) and ('季' in title or '集' in title):
        return '日韩剧'
    
    # 国产剧
    if '/dianshiju/' in url:
        return '国产剧'
    
    # 华语电影（默认）
    if '/movie/' in url:
        return '华语电影'
    
    return '华语电影'

def main():
    print("Step 1: Loading raw data...")
    with open(RAW_PATH, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    print(f"  Loaded {len(raw_data)} records")
    
    # 统计原始分类
    cats_before = {}
    for r in raw_data:
        cat = r.get('category', '未分类')
        cats_before[cat] = cats_before.get(cat, 0) + 1
    print(f"  Original categories: {dict(sorted(cats_before.items(), key=lambda x: -x[1]))}")
    
    # 重新分类
    print("\nStep 2: Reclassifying...")
    fixed_data = []
    changed = 0
    for r in raw_data:
        old_cat = r.get('category', '')
        new_cat = classify_record(r)
        r['category'] = new_cat
        fixed_data.append(r)
        if old_cat != new_cat:
            changed += 1
    
    print(f"  Changed {changed} records")
    
    # 统计新分类
    cats_after = {}
    for r in fixed_data:
        cat = r.get('category', '未分类')
        cats_after[cat] = cats_after.get(cat, 0) + 1
    print(f"  New categories: {dict(sorted(cats_after.items(), key=lambda x: -x[1]))}")
    
    # 保存修复后的数据
    with open(FIXED_PATH, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved to: {FIXED_PATH}")
    
    # 合并到 resources.json
    print("\nStep 3: Merging to resources.json...")
    with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)
    
    existing_ids = {r['id'] for r in existing}
    new_entries = []
    
    for r in fixed_data:
        cid = "rrdy-" + r['id'].replace('rrdy-', '').replace('fix-', '')
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
    print(f"DONE!")
    print(f"  Previous resources: {len(existing)}")
    print(f"  New movies added: {len(new_entries)}")
    print(f"  Total now: {len(all_resources)}")
    print(f"\nFinal categories:")
    for cat, count in sorted(final_cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    # 显示新增的影视示例
    movies = [r for r in all_resources if r.get('category') in 
              ['国产剧', '日韩剧', '欧美剧', '华语电影', '动画电影']]
    print(f"\nMovie resources (top 15 by hotness):")
    for r in sorted(movies, key=lambda x: -x.get('hotness', 0))[:15]:
        print(f"  [{r['category']}] {r['title'][:30]}")

if __name__ == '__main__':
    main()
