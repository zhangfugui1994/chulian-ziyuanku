#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正人人电影网条目的分类
"""
import json
import os

BASE_DIR = r'E:\主线\主线\正在做的\初恋资源库'
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'resources.json')

def classify_record(title, url=''):
    """根据标题和URL重新分类"""
    # 动漫相关
    anime_keywords = ['JOJO', '火影', '鬼灭', '进击', '咒术', '海贼', '柯南', 
                      '龙珠', 'EVA', '葬送的芙莉莲', '魔法少女', '奇犽', '数码',
                      '仙王', '灵笼', '雾山', '大理寺']
    if any(k.lower() in title.lower() for k in anime_keywords):
        return '动画电影'
    
    # 美剧/欧美剧关键词
    us_keywords = ['黑袍纠察', '亢奋', '权力游戏', '怪奇物语', '绝命毒师', 
                   '风骚律师', '行尸走肉', '西部世界', '曼达洛人', '王冠', '纸牌屋',
                   '最后生还者', '黄石', '继承之战', '泰德·拉索', '伦敦生活']
    if any(k in title for k in us_keywords):
        return '欧美剧'
    
    # 韩剧/日剧
    if any(c in title for c in ['韩国', '韩剧', '韩语']):
        return '日韩剧'
    if any(c in title for c in ['日剧', '日本']) and ('季' in title or '集' in title):
        return '日韩剧'
    
    # 国产剧（含港剧）
    if '/dianshiju/' in url or any(c in title for c in ['国产', '大陆', '内地', 'TVB', '港剧']):
        return '国产剧'
    if any(k in title for k in ['谷雨', '玫瑰战争', '烈焰', '长安', '庆余年']):
        return '国产剧'
    
    # 默认归类
    if '季' in title or '第X集' in title or '第X季' in title:
        return '欧美剧'  # 有季度的通常是美剧
    
    return '华语电影'  # 默认电影

def main():
    print("Reading resources.json...")
    with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
        resources = json.load(f)
    
    print(f"Total records: {len(resources)}")
    
    # 只修正 rrdy 开头的条目
    changed = 0
    for r in resources:
        rid = r.get('id', '')
        if not rid.startswith('rrdy-'):
            continue
        
        old_cat = r.get('category', '')
        new_cat = classify_record(r.get('title', ''), r.get('share', ''))
        
        if old_cat != new_cat:
            r['category'] = new_cat
            changed += 1
            title_short = r.get('title', '')[:30]
            print(f"  [{old_cat}] -> [{new_cat}] {title_short}")
    
    # 保存
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(resources, f, ensure_ascii=False, indent=2)
    
    # 统计
    cats = {}
    for r in resources:
        cat = r.get('category', '未分类')
        cats[cat] = cats.get(cat, 0) + 1
    
    print(f"\n{'='*60}")
    print(f"Fixed {changed} records")
    print(f"Final counts:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    # 影视类统计
    movie_cats = ['国产剧', '日韩剧', '欧美剧', '华语电影', '动画电影']
    movies = [r for r in resources if r.get('category') in movie_cats]
    print(f"\n影视资源共 {len(movies)} 条")

if __name__ == '__main__':
    main()
