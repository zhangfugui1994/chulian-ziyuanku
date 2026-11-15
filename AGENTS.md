# 初恋资源库 — 项目记忆(AGENTS.md)

> **这是给 AI 助手看的项目记忆。** 新对话框开始时先读本文件(以及同目录的 `README.md`、`DEPLOY.md`),即可无缝接手本项目。人类阅读可跳到「快速上手」。

---

## 1. 项目是什么

- **纯静态资料库网站**:内容全部存在 `data/resources.json`,页面运行时 `fetch` 该文件并渲染(列表 + 详情 + 搜索 + 分类筛选)。
- **无后端、无构建、无 package.json**。唯一数据源:`data/resources.json`。
- 部署:**GitHub → Cloudflare Pages**。每次 `git push` 自动重新部署,几分钟后线上生效。

## 2. 仓库与部署(关键事实)

| 项 | 值 |
|----|----|
| GitHub 仓库 | `zhangfugui1994/chulian-ziyuanku` |
| 推送 URL | `https://github.com/zhangfugui1994/chulian-ziyuanku.git` |
| 本地分支 / 上游 | `main` ↔ `origin/main` |
| 部署平台 | Cloudflare Pages(构建命令**留空**,输出目录 `./`,根目录 `./`,分支 `main`) |
| 部署文档 | 本目录 `DEPLOY.md`(逐步操作 + 排错表) |
| 站点结构文档 | 本目录 `README.md` |

## 3. 文件结构

```
初恋资源库/
├── index.html            # 列表页:搜索框 + 分类筛选 + 资料卡片网格
├── resource.html         # 详情页:?id=xxx,和首页风格统一(顶部多分类导航 + 16:9 封面大图 + 相关推荐)
├── assets/
│   ├── app.js            # 渲染逻辑(列表 initListPage / 详情 initDetailPage)
│   └── styles.css        # 暗色主题、响应式
├── data/
│   └── resources.json    # ← 唯一数据源,加/改资料只动这里
├── .gitignore            # 排除 .reasonix/、*.log、node_modules/ 等本地工具目录
├── README.md             # 项目说明 + 加资料字段 + 本地运行 + 部署
├── DEPLOY.md             # Cloudflare Pages 逐步部署清单 + 排错
└── AGENTS.md             # 本文件(项目记忆,给 AI 接手用)
```

## 4. 数据格式(加/改资料)

`data/resources.json` 是**一个 JSON 数组**,每项字段:

```json
{
  "id": "唯一标识(英文,kebab-case)",
  "title": "资料标题",
  "category": "分类名(可选,列表页筛选下拉从这里生成)",
  "tags": ["标签1", "标签2"],
  "summary": "列表里的一句话摘要",
  "body": "正文,支持 \\n 分段",
  "cover": "封面图 URL(可选,没有就显示占位块)",
  "hotness": 12550,
  "time": "2 天前",
  "price": "免费"
}
```

**字段规则**:
- `id` 被详情页 `?id=` 引用,**必须唯一、不可改**(改了旧链接会 404)。
- `category` 不写就没有该分类的筛选项;导航也随 `category` 自动增减。
- `cover`/`hotness`/`time`/`price` 均可选:缺 `cover` 显示占位块,缺 `hotness` 不进侧栏榜。
- 保存后页面自动刷新可见,**无需改代码**。

**布局(参考 vip.gamers520.com 版式,深底克制配色)**:
- `index.html`:顶部多分类导航(`#nav-cats`,由 `category` 自动生成:首页 + 各分类,橙色 active 下划线)+ 顶栏「登录」按钮(装饰)→ 控制条(搜索 + 分类筛选)→ 章节标题(`#section-title`,随分类动态变,如「示例 · 最新资源」)→ **主列表(封面在上网格卡片**:`.card` 内 `cover-wrap` 封面图/占位块在上,`.card-body` 文字区在下,响应式 4→2→1 列)→ **分页**(`#pager`,`PAGE_SIZE=12`)。
- `resource.html`:**详情页,和首页风格统一**:顶部多分类导航(`#nav-cats`)+ 16:9 封面大图(左侧 `flex:0 0 360px`)+ 右侧标题/分类/标签 chips/时间/价格/热度 + 正文区(`.body`)→ 底部「**相关推荐**」区(`#related`,同分类优先,复用 `.card` 网格,最多 4 条)。`?id=xxx` 命中单条资料;`id` 不存在时显示「未找到该资料」。
- 搜索/分类筛选切换时**自动回到第 1 页**;`?cat=` 可直达某分类。
- 常量在 `assets/app.js` 顶部:`PAGE_SIZE`(每页条数)、`SIDEBAR_TOP`(侧栏榜长度,当前未启用)。
- **侧栏热门榜结构仍在(`#sidebar`,CSS `display:none`)**:将来要启用只需改回布局,`hotness` 字段保留。

**字段规则**:
- `id` 被详情页 `?id=` 引用,**必须唯一、不可改**(改了旧链接会 404)。
- `category` 不写就没有该分类的筛选项;导航也随 `category` 自动增减。
- `cover`/`hotness`/`time`/`price` 均可选:缺 `cover` 显示占位块,缺 `hotness` 不进侧栏榜。
- 保存后页面自动刷新可见,**无需改代码**。

## 5. 本地运行(纯静态必须走 HTTP,不能 file://)

`fetch(data/resources.json)` 在 `file://` 下会被浏览器 CORS 拦截,所以:

- VS Code:装 **Live Server** 扩展,右键 `index.html` → "Open with Live Server"
- 或命令行:`python -m http.server 8000` / `npx serve .` → 开 `http://localhost:8000`

## 6. 踩坑记录(重要,别再踩)

### 6.1 构建命令不能留空「构建输出目录」
- **现象**:Cloudflare 构建失败 `npm error ENOENT ... package.json`。
- **根因**:填了 `npm run build`,但仓库**没有 package.json**(纯静态)。
- **修法**:Cloudflare Pages 设置里,`Build command` **完全留空**;`Build output directory` 填 `./`。
- **判断**:日志里若出现 `Executing user command: npm run build` 就是构建命令没清空。

### 6.2 仓库名曾为 `-`,已改用 `chulian-ziyuanku`
- **现象**:最初仓库叫 `zhangfugui1994/-`(单字符名,URL 难看)。
- **根因**:早期创建失误。
- **现状**:已切到 `chulian-ziyuanku`,本地 `origin` 指向新仓库。
- **遗留**:旧的 `-` 仓库仍在 GitHub,建议后台删除避免混淆(不影响本项目)。

### 6.3 GitHub 凭据账号混淆:deploy key 只读 + GCM 缓存错账号
- **现象**:
  - `git push` 报 `Permission to zhangfugui1994/-.git denied to deploy key`(deploy key 只能拉)。
  - 切 HTTPS 后报 `Permission ... denied to lss5148`(GCM 缓存的是**另一个账号** `lss5148` 的凭据,推 `zhangfugui1994` 的仓库没写权限)。
- **根因**:本机 GCM 把某账号的 GitHub 凭据缓存在 `git:https://github.com` 这个 Windows Credential Manager target 下,且该账号无目标仓库写权限。
- **修法**(各账号各用各的凭据):
  ```powershell
  cmdkey /list | Select-String "git|github"     # 查缓存
  cmdkey /delete:git:https://github.com          # 删掉旧缓存
  git push -u origin main                        # 重新认证(浏览器/弹窗输入正确账号的 PAT)
  ```
- **要点**:每个 GitHub 账号推自己的仓库要各自的凭据;删掉错账号的缓存后,GCM 会重新触发认证。

### 6.4 GCM 关闭了 TLS 证书校验
- **现象**:每次 push 出现 `SECURITY WARNING: TLS certificate verification has been disabled!`(不影响推送成功)。
- **根因**:本机 GCM 配置禁用了 TLS 校验。
- **待办(非紧急)**:有空在 GCM 设置里重新开启 `TLSVerify`,消除中间人风险。

### 6.5 内容合规风险(长期)
- 若资料库含**非原创/无版权/敏感主题**内容:GitHub 可能 DMCA 封仓,Cloudflare 可能屏蔽或要求下架。
- 中国大陆访问:Cloudflare 无 ICP 备案,速度不稳;长期方案是备案 + CDN 或改阿里云 OSS。
- **上线前自检内容合规**(README 风险提醒段也有写)。

### 6.6 本地起 HTTP 服务端口占用(WinError 10013)
- **现象**:`python -m http.server 8899` 报 `PermissionError: [WinError 10013] 以一种未授权的方式访问了一个被绑定的尝试`。
- **根因**:该端口已被占用(常见于**上一次后台服务没真停干净**,或别的进程占了它)。
- **修法**:换端口(如 `python -m http.server 8900`),或先确认/杀掉占用该端口的进程。
- **要点**:每次本地预览换个端口最省事;`bash-3`/`bash-4` 这类后台服务用 `kill_shell` 停掉后要确认真退了,否则下次同端口还会撞。

## 7. 升级路径(按需)

| 需求 | 方案 |
|------|------|
| 大量图片/视频/PDF | 加 Cloudflare **R2** 存媒体,JSON 里引用 URL(运行时再考虑) |
| 用户登录/收藏/上传 | 改 **Workers + D1/KV**,或接 Supabase/Firebase |
| 国内加速 | ICP 备案 + Cloudflare 国内节点,或阿里云 OSS+CDN |

## 8. 快速上手(给新对话框的 AI)

1. **读**:本文件 + `README.md` + `DEPLOY.md`(都在仓库根)。
2. **改资料**:编辑 `data/resources.json`(数组加项,字段见 §4),`git add . && git commit -m "..." && git push`(推 `zhangfugui1994/chulian-ziyuanku` 的 `main`)。
3. **部署**:Cloudflare Pages 已对接该仓库,**构建命令必须留空**,`push` 后自动重新部署。
4. **本地预览**:`python -m http.server 8000` 后开 `http://localhost:8000`(不能 `file://`)。
5. **别踩坑**:先翻 §6,尤其 6.1(构建命令留空)、6.3(凭据账号混淆)。
