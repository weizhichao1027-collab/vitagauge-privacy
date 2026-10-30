# 元气指数 / VitaGauge 官方网站

**1.2.0（5）已上架**。Apple 公开版本发布时间为 `2026-10-30T16:45:57Z`，即北京时间 **2026-10-31 00:45:57**。本网站于 **2026-10-31** 按该版本复核。销售方以 Apple 公布的 **Shanghai Qishan Cultural Communication Co., Ltd.** 为准；持有人已于 2026-10-31 确认由同一公司承担隐私控制者责任，网站已同步披露；联系邮箱仍为 weizhichao1027@gmail.com。

## 公开入口

| 用途 | 中文 | English |
| --- | --- | --- |
| 营销 / App Store Marketing URL | [功能与价格](https://weizhichao1027-collab.github.io/vitagauge-privacy/features/) | [Features](https://weizhichao1027-collab.github.io/vitagauge-privacy/en/features/) |
| 技术支持 / Support URL | [支持中心](https://weizhichao1027-collab.github.io/vitagauge-privacy/support/) | [Support](https://weizhichao1027-collab.github.io/vitagauge-privacy/en/support/) |
| 隐私 / Privacy URL | [隐私政策](https://weizhichao1027-collab.github.io/vitagauge-privacy/) | [Privacy](https://weizhichao1027-collab.github.io/vitagauge-privacy/en/) |
| 官方介绍 | [官方网站](https://weizhichao1027-collab.github.io/vitagauge-privacy/app/) | [Official site](https://weizhichao1027-collab.github.io/vitagauge-privacy/en/app/) |

另含 `/terms/`、`/sources/` 与对应英文页面。隐私根路径保持不变，避免已上架 App 和商店资料中的链接失效。[App Store](https://apps.apple.com/app/id6762522305) 使用按账户地区打开的地址，中文下载区另提供美国区商店详情备用链接；不承诺所有国家或地区均可下载或购买。无 Android / Google Play 版本。

## 本轮更新

- 从待发布改为当前 `currentRelease`：版本、构建、发布时刻、商店名称、销售方、文件大小及引用摘要统一维护。
- 补齐原生 iPad、配对 Apple Watch、表盘 / 智能叠放，以及主屏幕小 / 中 / 大 / iPad 超大和锁屏圆 / 矩形 / 行内小组件。
- 明确 App 安装最低 iOS / iPadOS 15；iPad 健康读取需 iPadOS 17+；小组件需 iOS / iPadOS 17+；Watch 需 watchOS 10+ 和兼容的配对 iPhone。系统控制刷新，手表只显示最近同步快照。
- 支持页补设备条件、手表同步按钮、跨设备恢复边界；隐私补手机 / 手表缓存、本机删除及已发送第三方数据的区别。
- 中英 iPhone 界面图换成新版生产界面的合成示例，增加 iPad / Watch 图。社交图同步新版版本及政策日期。没有使用个人健康记录。
- Pro 仍为一次买断，模型费用另计；¥38 只作历史中国区参考，当前可用性和价格以 Apple 购买页为准。结构化报价只标记已核实的免费下载，不把历史 Pro 标价写成全球现价。
- 持有人确认后，个人信息控制者统一更新为 **Shanghai Qishan Cultural Communication Co., Ltd.**，正文、元数据、引用摘要与机器事实保持一致。仅记录 2026-10-31 为披露更新日，不推断法律转移的发生日期；未擅自翻译公司法定中文名称。
- 政策原生效日保留 **2026-09-16**，网站复核 **2026-10-31**；已上架 1.2.0 的应用内离线摘要仍为 **2026-10-30**，网站维护不会自动改变已安装 App。

## 事实源与重建

先修改 `product-facts.json` 与生成模板，再执行：

```sh
python3 build_pages.py
python3 generate_og.py
python3 validate_site.py --output /tmp/vitagauge-site-validation.json
```

页面生成和校验只需 Python 3 标准库；社交图生成需 Pillow 及系统字体。`generate_og.py` 同时将界面截图转为无损 WebP 供网页加载（保留原 PNG），并更新 `assets/manifest.json`，记录图片尺寸和 SHA-256。`site.css` 为既有品牌样式，不依赖外部字体、CDN 或客户端 JavaScript。

`validate_site.py` 检查 13 页、12 个 sitemap URL、双语 canonical / hreflang、标题 / 描述 / H1、内部链接和锚点、图片、JSON-LD、34 组 FAQ 与可见内容、版本 / 日期、404 noindex、机器资料镜像以及常见凭据形态。失败时非零退出。

## SEO / GEO

- HTML 直接输出可检索正文，每页独立 title / description，canonical、互反 `zh-Hans` / `en` / `x-default`，Open Graph / Twitter、1200×630 社交卡片、App Store Smart Banner。
- JSON-LD 使用稳定实体 ID 关联 Organization、SoftwareApplication、WebSite、WebPage、BreadcrumbList；支持页另有可见问答对应的 FAQPage 和首次使用 HowTo。没有编造评分或评论，不保证富结果资格或展示。
- `sitemap.xml` 列出 12 个双语页面、正确 lastmod、hreflang 及图片。404 只有一个 noindex 指令，不进入 sitemap。
- 可引用的产品事实、公开 Apple 来源、设备条件和更新时间与 `product-facts.json`、`llms.txt`、`llms-full.txt`、`ai.txt`、`humans.txt`、`.well-known/` 保持一致。
- **部署边界：**项目位于 `/vitagauge-privacy/`；此目录的 robots.txt 不是主机根 `/robots.txt`。爬虫只会把主机根文件作为标准 robots 规则。主机根当前返回 404，不设置抓取禁令；页面 meta 和内部 sitemap 链接仍正常。不要把项目内 robots / security 副本写成已配置主机级规则。
- 这些机器资料辅助理解和引用，并非特殊排名协议。Google 明确表示 AI 搜索沿用基础 SEO，无需专门的 AI 文本文件；收录、排名和 AI 引用不保证。参考 [Google AI features](https://developers.google.com/search/docs/appearance/ai-features)、[robots.txt 位置规则](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt)、[SoftwareApplication](https://developers.google.com/search/docs/appearance/structured-data/software-app)。

## 部署与维护

独立公开仓库：`weizhichao1027-collab/vitagauge-privacy`，GitHub Pages 发布 `main` 根目录。保留 `.nojekyll`，避免隐藏目录被过滤。推送后等待 Pages 成功，再比对公开 URL 的 HTTP 状态及 SHA-256。不得把 App 工程、审核说明、签名材料、个人数据或凭据复制到公开仓库。

本地同名目录由 App 仓库忽略，仅 Git clone App 无法取到它；网站仓库保留完整公开源码、生成器与素材。无自定义域名；无站内登录、表单、Cookie、分析脚本和外部字体。GitHub 托管仍会处理请求日志，见政策。

产品变化时同步中英正文、FAQ / JSON-LD、机器事实、截图和社交图，再更新交接记录。未来应用数据处理实质变化须同步 App 内 13 语言披露及商店资料。本轮不更改 App 二进制、销售地区或已有暂缓 ICP 的决定。
