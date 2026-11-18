import json
import re

# 从 FlowUs 页面抓取的影视资源数据
movies_data = [
    {
        "id": "gu-yu-2026",
        "title": "谷雨 (2026)",
        "category": "国产剧",
        "tags": ["剧情"],
        "summary": "谷雨时节，一场关乎真相与正义的较量悄然展开。井柏然、张颂文领衔主演。",
        "body": "谷雨时节，一场关乎真相与正义的较量悄然展开。\n\n主演：井柏然、张颂文、孙艺洲、隋俊波、李小冉\n评分：TMDB 9分\n品质：4K WEB-DL HDR10 H265 AAC 2.0\n状态：持续更新中，目前已更新至第26集",
        "cover": "https://image.tmdb.org/t/p/w780/m5tiVhzIFIqDyIPwOsHDsMDGMsK.jpg",
        "hotness": 9850,
        "time": "今日更新",
        "price": "免费"
    },
    {
        "id": "jin-tian-shi-tai-yang-yu-2026",
        "title": "今天是太阳雨 (2026)",
        "category": "国产剧",
        "tags": ["剧情"],
        "summary": "杨超越、董思成主演，讲述一段温暖治愈的故事。",
        "body": "今天是太阳雨 (2026)\n\n主演：杨超越、董思成、李雨真、刘佳玺、肖添仁\n品质：4K WEB-DL H264 AAC 2.0\n状态：持续更新中，目前已更新至第23-24集",
        "cover": "https://image.tmdb.org/t/p/w780/9LtN1ac91JAqXMke8CAJ6BiBSLS.jpg",
        "hotness": 8520,
        "time": "今日更新",
        "price": "免费"
    },
    {
        "id": "mei-gui-zheng-zheng-2026",
        "title": "玫瑰战争 (2026)",
        "category": "国产剧",
        "tags": ["剧情"],
        "summary": "杨茜尧、陈豪领衔主演，TVB经典制作，讲述家族恩怨与爱情故事。",
        "body": "玫瑰战争 (2026)\n\n主演：杨茜尧、陈豪、林夏薇、马国明、陈展鹏\n评分：TMDB 8分\n品质：4K WEB-DL HDR10 H265 DDP 2.0\n状态：持续更新中，目前已更新至第25集",
        "cover": "https://image.tmdb.org/t/p/w780/idx5Alvalsje6j85BueoQc3OwHj.jpg",
        "hotness": 7650,
        "time": "今日更新",
        "price": "免费"
    },
    {
        "id": "shi-wan-kuang-hua-ru-meng-lai-2026",
        "title": "十万狂花入梦来 (2026)",
        "category": "国产剧",
        "tags": ["剧情", "奇幻"],
        "summary": "李宏毅、孙珍妮主演，一部充满魔幻色彩的剧集。TMDB评分满分10分！",
        "body": "十万狂花入梦来 (2026)\n\n导演：钟青\n主演：李宏毅、孙珍妮、赵昭仪、张康乐、马闻远\n评分：TMDB 10分\n品质：4K WEB-DL H265 AAC 2.0\n状态：持续更新中，目前已更新至第8集\n简介：万恶之源的魔头岐凤殷邂逅唐僧肉体质的少女鸭毛，被迫绑定的二人相互厌弃又相互救赎，历经长发枯骨、昼人夜妖、化蛟为龙、血池还魂、红妆剜心、金鱼花火六件诡案，破解幕后阴谋，终洗清彼此污名。",
        "cover": "https://image.tmdb.org/t/p/w780/msJpPeZiqSxXXKJ0IiuOOOv7s9p.jpg",
        "hotness": 12500,
        "time": "今日更新",
        "price": "免费",
        "share": "https://pan.quark.cn/s/2bb3875393fc?pwd=z9fe",
        "share_alt": [
            {"netdisk": "百度", "url": "https://pan.baidu.com/s/1Gh3nfPO3DP-p4NeOfpEMRg?pwd=8us3"},
            {"netdisk": "迅雷", "url": "https://pan.xunlei.com/s/VP6UGdJC_VxhKT5bB5IU5lwpA1?pwd=44ga"}
        ]
    },
    {
        "id": "yu-wang-de-xian-jing-2026",
        "title": "欲望的陷阱 (2026)",
        "category": "日韩剧",
        "tags": ["悬疑", "犯罪", "剧情"],
        "summary": "张瑞希、全惠媛、尹海英主演，一部充满悬疑色彩的韩剧。TMDB评分满分10分！",
        "body": "欲望的陷阱 (2026)\n\n主演：张瑞希、全惠媛、尹海英\n评分：TMDB 10分\n类型：悬疑、犯罪、剧情\n状态：持续更新中，目前已更新至第58集",
        "cover": "https://image.tmdb.org/t/p/w780/qJeyb3SHzH9B8K6ozayzE6VbmA3.jpg",
        "hotness": 11200,
        "time": "今日更新",
        "price": "免费"
    }
]

print(f"已准备 {len(movies_data)} 条影视数据")

# 读取现有资源文件
with open(r'E:\主线\主线\正在做的\初恋资源库\data\resources.json', 'r', encoding='utf-8') as f:
    resources = json.load(f)

initial_count = len(resources)

# 添加新数据（避免重复）
existing_ids = {r['id'] for r in resources}
new_count = 0
for movie in movies_data:
    if movie['id'] not in existing_ids:
        resources.append(movie)
        new_count += 1
        print(f"  + 新增: {movie['title']}")
    else:
        print(f"  - 跳过(已存在): {movie['title']}")

# 保存
with open(r'E:\主线\主线\正在做的\初恋资源库\data\resources.json', 'w', encoding='utf-8') as f:
    json.dump(resources, f, ensure_ascii=False, indent=2)

final_count = len(resources)
print(f"\n当前资源总数: {final_count}")
print(f"本次新增: {new_count} 条影视资源")

# 统计分类
cats = {}
for r in resources:
    cat = r.get('category', '未分类')
    cats[cat] = cats.get(cat, 0) + 1
print("\n分类统计:")
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count} 条")
