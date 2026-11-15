# Cloudflare Pages 部署对照清单

> 仓库:`zhangfugui1994/chulian-ziyuanku`(HTTPS:`https://github.com/zhangfugui1994/chulian-ziyuanku.git`)
> 纯静态站,**无需构建**。

## 一、创建 Pages 项目(首次)

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)。
2. 左侧菜单 → **Workers & Pages** → 点 **Create** → **Pages** 标签 → **Connect to Git**。
3. 授权 GitHub(若首次)。
4. 仓库选 **`zhangfugui1994/-`**。
5. 构建配置(全部填默认值):

   | 字段 | 填法 |
   |------|------|
   | **Build command** | 留空(纯静态无需构建) |
   | **Build output directory** | `./`(整个仓库根目录) |
   | **Root directory** | `./` |
   | **Branch to build** | `main` |

6. 点 **Deploy site**,等约 30 秒构建完成。
7. 完成后拿到形如 `https://<随机名>.pages.dev` 的预览 URL,改 `data/resources.json` 后 `git push` 即自动重新部署。

> 提示:随机子域名是 `xxx.pages.dev`。若想自定义项目名,可在创建后于 **Settings → General** 修改,或用 **Custom domains** 绑定自己的域名。

## 二、自定义域名(可选)

1. Pages 项目 → **Custom domains** → **Set up a custom domain**。
2. 填你要的域名(需先把域名加到 Cloudflare 账户)。
3. Cloudflare 自动签发 HTTPS 证书,按提示在 DNS 里加 A / CNAME 记录即可。
4. 若域名在别的 DNS 服务商,按 Cloudflare 给出的记录手动加。

## 三、环境变量(本项目默认不需要)

纯静态站运行时只读 `data/resources.json`,**无需任何环境变量**。
将来若接 Cloudflare R2(对象存储)存媒体,可在此处配 `R2_*` 相关变量(配合 Workers)。

## 四、国内访问(可选,体验相关)

Cloudflare 默认无 ICP 备案,中国大陆访问可能不稳定。

- 短期:无备案,接受偶发缓慢。
- 长期:域名完成 ICP 备案后,Cloudflare 支持绑定国内加速节点(需企业版 / 单独申请),或改用阿里云 OSS + CDN。

## 五、上线后常规操作

| 操作 | 命令 |
|------|------|
| 加/改资料 | 编辑 `data/resources.json` → `git add . && git commit -m "..." && git push` |
| 看部署历史 | Cloudflare → Pages 项目 → **Deployments** |
| 手动重部署 | Deployments 里点 **Retry latest** |

## 六、排错

| 现象 | 排查 |
|------|------|
| 部署失败 | 看 **Deployments** 里该次构建的日志,多半是构建配置填错 |
| 页面 404 | 确认输出目录是 `./`,文件都在仓库根 |
| 列表为空 | 检查 `data/resources.json` 语法合法(可在线 JSON 校验) |
| 推送 403 / 认证失败 | 本机 GCM 缓存的可能是别的账号,清掉后重推(见仓库历史说明) |
