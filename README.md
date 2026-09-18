# 元气指数 / VitaGauge 官方网站

静态官方、营销、支持与政策站点。只放公开产品事实和合成示例截图。

应用 **1.1.0 已于 2026-09-15 在 App Store 上架**。本目录按 2026-09-18 再复核：文案为「现已提供」，政策生效日仍为 **2026-09-16**，本页复核日为 **2026-09-18**（未新增处理类型）。

本目录已被 **app 仓库 `.gitignore` 忽略**。`git status` 看不到这里的改动。线上以发布仓库为准；产品交接以 app 仓库的[项目交接文档](../项目交接文档.md)为准。

## 线上地址

商店三个入口（路径未改）：

- 功能与价格（**Marketing URL**）：https://weizhichao1027-collab.github.io/vitagauge-privacy/features/
- 支持中心（**Support URL**）：https://weizhichao1027-collab.github.io/vitagauge-privacy/support/
- 隐私政策（**Privacy URL**，必须保持根路径）：https://weizhichao1027-collab.github.io/vitagauge-privacy/

附加页面：

- 官方网站：https://weizhichao1027-collab.github.io/vitagauge-privacy/app/
- 使用与购买：https://weizhichao1027-collab.github.io/vitagauge-privacy/terms/
- 资料来源：https://weizhichao1027-collab.github.io/vitagauge-privacy/sources/
- 英文：在路径前加 `/en/`
- App Store：https://apps.apple.com/app/id6762522305 （仅 iOS，无 Google Play）

## 单一事实源

改产品事实时先改 `product-facts.json`，再运行：

```sh
python3 build_pages.py
python3 generate_og.py   # 仅当社交卡片文案变化
```

`build_pages.py` 会重写中英页面、`sitemap.xml`、`styles.css` 桥接，以及 `llms.txt`、`llms-full.txt`、`robots.txt`、`ai.txt`、`humans.txt`、`site.webmanifest` 与 `.well-known/`。

## 部署

1. 只把本目录的公开网站文件同步到独立仓库 `weizhichao1027-collab/vitagauge-privacy` 的 `main` 根目录。
2. 不要把 App 工程、审核备注或密钥推进该公开仓库。
3. 推送 `main` 后等待 GitHub Pages `pages build and deployment` 成功，再用无登录浏览器回读。
4. 仓库需保留 `.nojekyll`，否则 `.well-known` 可能被 Jekyll 丢掉。

GitHub Pages 发布 `main` 根目录。无构建依赖、无表单、无 Cookie、无分析、无外部字体。未购买自定义域名。

应用内法律链接未改：隐私 `/`，支持 `/support/`，官网 `/app/`，使用说明 `/terms/`（非中文加 `en/`）。

## SEO / GEO 文件清单

SEO：每页独立 title / description / canonical / robots / Open Graph / Twitter Card；1200×630 `og-*.png`；hreflang `zh-Hans` / `en` / `x-default`；`robots.txt`；`sitemap.xml`（含 hreflang 与截图）；`404.html`；`site.webmanifest`；JSON-LD `Organization`（含 ContactPoint）、`SoftwareApplication`（含 featureList、AggregateOffer、fileSize、contentRating）、`WebSite`、`HowTo`（支持页首次启动）、`FAQPage`、`BreadcrumbList`。

GEO：页面上的「可引用的产品事实」与政策「先读这一段」；`llms.txt`、`llms-full.txt`、`product-facts.json`、`ai.txt`、`humans.txt`、`.well-known/llms.txt`、`.well-known/ai.txt`、`.well-known/security.txt`；支持页 15 组 FAQ。Google Search 不把 llms.txt 当排名信号，这些文件用于助手引用与站点卫生。

## 2026-09-18 相对 2026-09-16 的变化

- 按已上架 1.1.0 再写营销、支持和隐私：补充「做什么 / 不做什么」、三种对话模式、体温/血压/睡眠口径、小组件与语言、撤回同意。
- 政策生效日仍为 2026-09-16；本页复核 2026-09-18，未新增处理类型。
- 补 1200×630 社交图、更完整的 JSON-LD、HowTo、FAQ、robots 检索机器人名单、`.well-known` 与 manifest。
- 应用内离线政策日期已在源码改为 2026-09-18（`SettingsFlow.swift`），需随下一版构建才会出现在商店包里。

更早的预览提交（如 `bc84e77`、`62d7ac2`、`3446594`）不能证明今日文案。

## 维护约定

- 健康应用：不编造疗效、评分或诊断能力。
- 截图必须是生产界面加合成数据，不得使用个人健康记录。
- 数据处理变化时，同步中英政策、`product-facts.json`、`llms.txt` 和应用内 13 语言摘要。
- 权限事实：HealthKit 只读；麦克风 + 设备端语音；头像 PHPicker，无相机；无账户；无分析 / 崩溃 / 广告 SDK。
- 中国大陆 Pro 首发标价写 ¥38 时，必须同时写「以 Apple 购买页为准」。
- 可见文案不用破折号（—）。
