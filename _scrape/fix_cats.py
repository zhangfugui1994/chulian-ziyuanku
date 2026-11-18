#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os

BASE = r'E:\主线\主线\正在做的\初恋资源库'
OUTPUT = os.path.join(BASE, 'data', 'resources.json')

ANIME_KW = ['JOJO','火影','鬼灭','进击','咒术','海贼','柯南','龙珠','EVA',
            '葬送的芙莉莲','魔法少女','奇犽','数码','仙王','灵笼','雾山',
            '大理寺','一人之下']
US_KW = ['黑袍纠察','亢奋','权力游戏','怪奇物语','绝命毒师','风骚律师',
         '行尸走肉','西部世界','曼达洛人','王冠','纸牌屋','最后生还者',
         '黄石','继承之战','伦敦生活','傲骨贤妻']
KR_JP_KW = ['韩国','韩剧','韩语','日剧','日本','张瑞希','全惠媛']

def classify(title):
    t = title or ''
    if any(k in t for k in ANIME_KW):
        return '动画电影'
    if any(k in t for k in US_KW):
        return '欧美剧'
    if any(k in t for k in KR_JP_KW):
        return '日韩剧'
    # 有"季"字且不是动漫/韩剧 → 欧美剧
    if '季' in t and '动画' not in t:
        return '欧美剧'
    return '华语电影'

with open(OUTPUT, 'r', encoding='utf-8') as f:
    resources = json.load(f)

changed = 0
for r in resources:
    rid = r.get('id', '')
    if not rid.startswith('rrdy-'):
        continue
    old = r.get('category', '')
    new = classify(r.get('title', ''))
    if old != new:
        r['category'] = new
        changed += 1

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(resources, f, ensure_ascii=False, indent=2)

cats = {}
for r in resources:
    c = r.get('category', '-')
    cats[c] = cats.get(c, 0) + 1

print(f'Total: {len(resources)} records')
print(f'Changed: {changed} rrdy entries')
for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f'  {cat}: {n}')
