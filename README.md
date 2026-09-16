# 元气指数 / VitaGauge 官方网站

静态官方、营销、支持与政策站点。只放公开产品事实和合成示例截图。

应用 **1.1.0 已于 2026-09-15 在 App Store 上架**。本目录源码按 2026-09-16 的上架事实改写，语言为「现已提供」，不再写即将上线。

## 线上地址

- 官方网站：https://weizhichao1027-collab.github.io/vitagauge-privacy/app/
- 功能与价格（商店 Marketing URL）：https://weizhichao1027-collab.github.io/vitagauge-privacy/features/
- 支持中心：https://weizhichao1027-collab.github.io/vitagauge-privacy/support/
- 隐私政策（商店 Privacy URL，路径保持不变）：https://weizhichao1027-collab.github.io/vitagauge-privacy/
- 使用与购买：https://weizhichao1027-collab.github.io/vitagauge-privacy/terms/
- 资料来源：https://weizhichao1027-collab.github.io/vitagauge-privacy/sources/
- 英文：在路径前加 `/en/`
- App Store：https://apps.apple.com/app/id6762522305

## 单一事实源

改产品事实时先改 `product-facts.json`，再运行：

```sh
python3 build_pages.py
```

会重写中英页面、`sitemap.xml` 和 `styles.css` 桥接。`llms.txt` / `llms-full.txt` / `robots.txt` 与 JSON 对齐，需同步修订。

## 部署

发布仓库 `weizhichao1027-collab/vitagauge-privacy`，GitHub Pages 发布 `main` 根目录。无构建依赖、无表单、无 Cookie、无分析、无外部字体。GitHub 按自身隐私声明处理托管请求。

应用内法律链接未改：

- 隐私：`https://weizhichao1027-collab.github.io/vitagauge-privacy/`
- 支持：`…/support/`
- 官网：`…/app/`
- 使用说明：`…/terms/`（非中文加 `en/`）

## 维护约定

- 健康应用：不编造疗效或诊断能力。
- 截图必须是生产界面加合成数据，不得使用个人健康记录。
- 数据处理变化时，同步中英政策、`product-facts.json`、`llms.txt` 和应用内 13 语言摘要（应用内离线政策日期目前仍为 2026-09-14）。
