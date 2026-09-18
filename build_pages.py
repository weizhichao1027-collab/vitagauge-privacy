#!/usr/bin/env python3
"""Generate VitaGauge public pages from product-facts.json. Static HTML only."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FACTS = json.loads((ROOT / "product-facts.json").read_text(encoding="utf-8"))
BASE = FACTS["sites"]["base"]
TODAY = FACTS["updated"]
REVIEWED = FACTS.get("reviewed", TODAY)
EFFECTIVE = FACTS["legal"]["privacyEffectiveDate"]
PREVIOUS = FACTS["legal"]["privacyPreviousDate"]
STORE = FACTS["stores"]["trackViewUrl"]
STORE_ZH = FACTS["stores"]["trackViewUrlZh"]
STORE_EN = FACTS["stores"]["trackViewUrlEn"]
EMAIL = FACTS["legal"]["email"]
APP_ID = FACTS["stores"]["appleId"]
BUNDLE = FACTS["product"]["bundleId"]
VERSION = FACTS["product"]["version"]
FILE_SIZE = FACTS["product"].get("fileSizeBytes", 7877632)


def asset(depth: str, name: str) -> str:
    return f"{depth}assets/{name}"


def url(*parts: str) -> str:
    path = "/".join(p.strip("/") for p in parts if p and p != "/")
    return f"{BASE}/{path}/" if path else f"{BASE}/"


APPLE_SVG = """<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.36 12.86c0-2.16 1.77-3.2 1.85-3.25-1.02-1.49-2.6-1.69-3.16-1.71-1.33-.14-2.62.79-3.3.79-.69 0-1.73-.77-2.86-.75-1.46.02-2.82.86-3.57 2.17-1.54 2.66-.39 6.59 1.09 8.75.73 1.06 1.59 2.24 2.72 2.2 1.1-.04 1.51-.7 2.84-.7 1.32 0 1.69.7 2.86.67 1.19-.02 1.93-1.07 2.65-2.14.84-1.22 1.18-2.41 1.2-2.47-.03-.01-2.29-.88-2.32-3.56zM14.7 6.37c.6-.73 1.01-1.75.9-2.77-.87.04-1.93.58-2.55 1.31-.56.64-1.05 1.68-.92 2.67.98.08 1.98-.5 2.57-1.21z"/></svg>"""


def store_badge(lang: str) -> str:
    href = STORE_ZH if lang.startswith("zh") else STORE_EN
    if lang.startswith("zh"):
        label, small, strong = "在 App Store 下载元气指数", "下载自", "App Store"
    else:
        label, small, strong = "Download VitaGauge on the App Store", "Download on the", "App Store"
    return (
        f'<a class="store-badge" href="{href}" rel="noopener" aria-label="{label}">'
        f"{APPLE_SVG}<span><small>{small}</small><strong>{strong}</strong></span></a>"
    )


def json_ld(payloads: list[dict]) -> str:
    graph = {"@context": "https://schema.org", "@graph": payloads}
    return (
        '<script type="application/ld+json">'
        + json.dumps(graph, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )


def org() -> dict:
    return {
        "@type": "Organization",
        "@id": f"{BASE}/#org",
        "name": "智超 卫",
        "alternateName": ["zhichao wei", "元气指数", "VitaGauge"],
        "email": EMAIL,
        "url": url("app"),
        "logo": f"{BASE}/assets/icon.png",
        "sameAs": [
            FACTS["stores"]["developerUrlZh"],
            FACTS["stores"]["developerUrlEn"],
            STORE,
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "customer support",
            "email": EMAIL,
            "availableLanguage": ["zh-Hans", "en"],
            "url": url("support"),
        },
    }


def software(lang: str) -> dict:
    zh = lang.startswith("zh")
    prefix = "zh-Hans" if zh else "en"
    return {
        "@type": "SoftwareApplication",
        "@id": f"{BASE}/#app",
        "name": "元气指数" if zh else "VitaGauge",
        "alternateName": ["VitaGauge", "VitaGauge: Health Tracker", "元气指数"],
        "applicationCategory": "HealthApplication",
        "applicationSubCategory": "LifestyleApplication",
        "operatingSystem": "iOS 15.0 or later",
        "softwareVersion": VERSION,
        "datePublished": FACTS["product"]["firstReleased"],
        "dateModified": FACTS["product"]["released"],
        "inLanguage": FACTS["product"]["languages"],
        "isAccessibleForFree": True,
        "fileSize": str(FILE_SIZE),
        "contentRating": FACTS["product"]["contentRating"],
        "featureList": (
            [
                "今日健康摘要",
                "16 项 Apple 健康指标",
                "7 天与 30 天趋势",
                "本地记录问答",
                "健康目标",
                "主屏幕与锁屏小组件",
                "自备 Key 的在线 AI",
            ]
            if zh
            else [
                "Daily health summary",
                "16 Apple Health metrics",
                "7-day and 30-day trends",
                "On-device record questions",
                "Health goals",
                "Home and Lock Screen widgets",
                "BYOK online AI",
            ]
        ),
        "offers": {
            "@type": "AggregateOffer",
            "lowPrice": "0",
            "highPrice": str(FACTS["iap"]["chinaLaunchPriceCNY"]),
            "priceCurrency": "CNY",
            "offerCount": 2,
            "offers": [
                {
                    "@type": "Offer",
                    "name": "元气指数免费下载" if zh else "VitaGauge free download",
                    "price": "0",
                    "priceCurrency": "CNY",
                    "availability": "https://schema.org/InStock",
                    "url": STORE_ZH if zh else STORE_EN,
                },
                {
                    "@type": "Offer",
                    "name": "VitaGauge Pro",
                    "price": str(FACTS["iap"]["chinaLaunchPriceCNY"]),
                    "priceCurrency": "CNY",
                    "availability": "https://schema.org/InStock",
                    "category": "https://schema.org/NonConsumable",
                    "description": FACTS["iap"]["priceNoteZh"] if zh else FACTS["iap"]["priceNoteEn"],
                    "url": url("features") if zh else url("en", "features"),
                },
            ],
        },
        "downloadUrl": STORE_ZH if zh else STORE_EN,
        "installUrl": STORE,
        "identifier": APP_ID,
        "url": url("app") if zh else url("en", "app"),
        "image": f"{BASE}/assets/icon.png",
        "screenshot": [
            f"{BASE}/assets/{prefix}-summary.png",
            f"{BASE}/assets/{prefix}-assistant.png",
            f"{BASE}/assets/{prefix}-trend.png",
            f"{BASE}/assets/{prefix}-goal.png",
        ],
        "author": {"@id": f"{BASE}/#org"},
        "publisher": {"@id": f"{BASE}/#org"},
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "bundleId", "value": BUNDLE},
            {"@type": "PropertyValue", "name": "itunesAppId", "value": APP_ID},
            {"@type": "PropertyValue", "name": "proProductId", "value": FACTS["iap"]["productId"]},
            {"@type": "PropertyValue", "name": "healthKitWrite", "value": "false"},
            {"@type": "PropertyValue", "name": "developerAccount", "value": "false"},
        ],
        "description": FACTS["product"]["shortPitchZh"] if zh else FACTS["product"]["shortPitchEn"],
    }


def website() -> dict:
    return {
        "@type": "WebSite",
        "@id": f"{BASE}/#website",
        "name": "元气指数 / VitaGauge",
        "alternateName": ["元气指数官网", "VitaGauge official site"],
        "url": f"{BASE}/",
        "inLanguage": ["zh-Hans", "en"],
        "publisher": {"@id": f"{BASE}/#org"},
        "about": {"@id": f"{BASE}/#app"},
    }


def crumbs(items: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": link}
            for i, (name, link) in enumerate(items)
        ],
    }


def faq_schema(pairs: list[tuple[str, str]]) -> dict:
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in pairs
        ],
    }


def head(
    *,
    lang: str,
    title: str,
    description: str,
    canonical: str,
    alt: str,
    depth: str,
    og_type: str = "website",
    og_image: str = "og-default.png",
    extra: str = "",
) -> str:
    locale = "zh_CN" if lang.startswith("zh") else "en_US"
    alt_locale = "en_US" if lang.startswith("zh") else "zh_CN"
    icon = asset(depth, "icon.png")
    image = f"{BASE}/assets/{og_image}"
    robots = "index,follow,max-image-preview:large,max-snippet:-1"
    keywords = (
        ",".join(FACTS["seo"]["keywordsZh"])
        if lang.startswith("zh")
        else ",".join(FACTS["seo"]["keywordsEn"])
    )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#eef3ea" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#121c17" media="(prefers-color-scheme: dark)">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="{robots}">
<meta name="googlebot" content="{robots}">
<meta name="author" content="智超 卫">
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords}">
<title>{title}</title>
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="zh-Hans" href="{canonical if lang.startswith('zh') else alt}">
<link rel="alternate" hreflang="en" href="{alt if lang.startswith('zh') else canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical if lang.startswith('zh') else alt}">
<link rel="alternate" type="application/json" href="{depth}product-facts.json" title="product facts">
<link rel="alternate" type="text/plain" href="{depth}llms.txt" title="LLM facts">
<link rel="manifest" href="{depth}site.webmanifest">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{title}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="{locale}">
<meta property="og:locale:alternate" content="{alt_locale}">
<meta property="og:site_name" content="元气指数 / VitaGauge">
<meta property="article:modified_time" content="{REVIEWED}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{image}">
<meta name="twitter:image:alt" content="{title}">
<meta name="apple-itunes-app" content="app-id={APP_ID}">
<link rel="icon" href="{icon}">
<link rel="icon" type="image/png" sizes="32x32" href="{asset(depth, 'favicon-32.png')}">
<link rel="apple-touch-icon" href="{asset(depth, 'apple-touch-icon.png')}">
<link rel="stylesheet" href="{depth}site.css">
{extra}
</head>
"""


NAV = {
    "zh": [
        ("app", "官方网站", url("app")),
        ("features", "功能与价格", url("features")),
        ("support", "支持中心", url("support")),
        ("privacy", "隐私政策", url()),
    ],
    "en": [
        ("app", "Official site", url("en", "app")),
        ("features", "Features", url("en", "features")),
        ("support", "Support", url("en", "support")),
        ("privacy", "Privacy", url("en")),
    ],
}


def header(lang: str, current: str, depth: str) -> str:
    zh = lang.startswith("zh")
    home = f"{depth}app/" if zh else f"{depth}en/app/"
    brand = "元气指数" if zh else "VitaGauge"
    skip = "跳至正文" if zh else "Skip to content"
    nav_label = "主导航" if zh else "Main"
    other_href = {
        "app": f"{depth}en/app/" if zh else f"{depth}app/",
        "features": f"{depth}en/features/" if zh else f"{depth}features/",
        "support": f"{depth}en/support/" if zh else f"{depth}support/",
        "privacy": f"{depth}en/" if zh else f"{depth}",
        "terms": f"{depth}en/terms/" if zh else f"{depth}terms/",
        "sources": f"{depth}en/sources/" if zh else f"{depth}sources/",
        "404": f"{depth}en/app/" if zh else f"{depth}app/",
    }[current]
    other_label = "English" if zh else "简体中文"
    other_lang = "en" if zh else "zh-Hans"
    items = []
    for key, label, href in NAV["zh" if zh else "en"]:
        href_local = {
            "app": f"{depth}app/" if zh else f"{depth}en/app/",
            "features": f"{depth}features/" if zh else f"{depth}en/features/",
            "support": f"{depth}support/" if zh else f"{depth}en/support/",
            "privacy": ("./" if depth == "" else depth) if zh else f"{depth}en/",
        }[key]
        cur = ' aria-current="page"' if key == current else ""
        items.append(f'<a href="{href_local}"{cur}>{label}</a>')
    items.append(f'<a href="{other_href}" lang="{other_lang}">{other_label}</a>')
    return f"""<body>
<a class="skip" href="#main">{skip}</a>
<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="{home}"><img src="{asset(depth, 'icon.png')}" width="44" height="44" alt="{brand} 图标"> {brand}</a>
    <nav class="site-nav" aria-label="{nav_label}">{''.join(items)}</nav>
  </div>
</header>
<main id="main">
"""


def footer(lang: str, depth: str) -> str:
    zh = lang.startswith("zh")
    if zh:
        links = f"""<a href="{depth}app/">官方网站</a>
        <a href="{depth}features/">功能与价格</a>
        <a href="{depth}support/">支持中心</a>
        <a href="{depth or './'}">隐私政策</a>
        <a href="{depth}terms/">使用说明</a>
        <a href="{depth}sources/">资料来源</a>
        <a href="{STORE_ZH}" rel="noopener">App Store</a>"""
        note = FACTS["disclaimerZh"]
        copy = f'© 2026 智超 卫 · <a href="mailto:{EMAIL}">{EMAIL}</a>'
        brand = "元气指数 · VitaGauge"
    else:
        links = f"""<a href="{depth}en/app/">Official site</a>
        <a href="{depth}en/features/">Features</a>
        <a href="{depth}en/support/">Support</a>
        <a href="{depth}en/">Privacy</a>
        <a href="{depth}en/terms/">Use &amp; purchases</a>
        <a href="{depth}en/sources/">Sources</a>
        <a href="{STORE_EN}" rel="noopener">App Store</a>"""
        note = FACTS["disclaimerEn"]
        copy = f'© 2026 zhichao wei · <a href="mailto:{EMAIL}">{EMAIL}</a>'
        brand = "VitaGauge · 元气指数"
    return f"""</main>
<footer class="footer">
  <div class="wrap">
    <div class="footer-row">
      <strong translate="no">{brand}</strong>
      <div>{links}</div>
    </div>
    <p class="note">{note}</p>
    <p class="note">{copy}</p>
  </div>
</footer>
</body>
</html>
"""


def crumb_nav(items: list[tuple[str, str]]) -> str:
    parts = []
    for i, (name, href) in enumerate(items):
        if i == len(items) - 1:
            parts.append(f'<span aria-current="page">{name}</span>')
        else:
            parts.append(f'<a href="{href}">{name}</a>')
        if i < len(items) - 1:
            parts.append("<span aria-hidden=\"true\"> / </span>")
    return f'<nav class="crumbs" aria-label="breadcrumb">{"".join(parts)}</nav>'


METRICS_ZH = "步数、步行与跑步距离、活动能量、心率、静息心率、血氧、睡眠、体重、体能训练、心率变异性、呼吸频率、心肺适能、体脂率、收缩压、舒张压、体温"
METRICS_EN = "steps, walking and running distance, active energy, heart rate, resting heart rate, blood oxygen, sleep, weight, workouts, heart rate variability, respiratory rate, cardio fitness, body fat percentage, systolic and diastolic blood pressure, and body temperature"

RAIL_ZH = ["步数", "睡眠", "心率", "血氧", "活动能量", "体重", "血压", "体脂", "体温", "HRV", "呼吸", "心肺适能", "训练", "步行距离", "静息心率", "16 项"]
RAIL_EN = ["Steps", "Sleep", "Heart rate", "Blood oxygen", "Energy", "Weight", "Blood pressure", "Body fat", "Temperature", "HRV", "Breathing", "Cardio", "Workouts", "Distance", "Resting HR", "16 metrics"]


def rail(items: list[str]) -> str:
    return '<div class="rail" tabindex="0">' + "".join(f"<span>{x}</span>" for x in items) + "</div>"


def cite_box(lang: str) -> str:
    zh = lang.startswith("zh")
    title = "可引用的产品事实" if zh else "Citable product facts"
    body = FACTS["citeZh"] if zh else FACTS["citeEn"]
    more = (
        f'<p class="note">机器可读事实：<a href="{BASE}/llms.txt">llms.txt</a>、<a href="{BASE}/product-facts.json">product-facts.json</a>、<a href="{BASE}/llms-full.txt">llms-full.txt</a>。</p>'
        if zh
        else f'<p class="note">Machine facts: <a href="{BASE}/llms.txt">llms.txt</a>, <a href="{BASE}/product-facts.json">product-facts.json</a>, <a href="{BASE}/llms-full.txt">llms-full.txt</a>.</p>'
    )
    return f'<aside class="cite" aria-label="{title}"><h2>{title}</h2><p>{body}</p>{more}</aside>'


def privacy_dates(zh: bool) -> str:
    if zh:
        return f"生效：{EFFECTIVE}。上一版：{PREVIOUS}。本页复核：{REVIEWED}（未新增处理类型）。"
    return f"Effective {EFFECTIVE}. Previous version {PREVIOUS}. Page reviewed {REVIEWED}. No new processing was added."


def howto_first_launch(zh: bool) -> dict:
    if zh:
        name = "第一次打开元气指数"
        steps = [
            ("从 App Store 安装", f"打开 {STORE_ZH} 安装元气指数。仅提供 iOS 版本。"),
            ("阅读健康说明并继续", "首屏说明下一步是系统权限。主按钮是「继续」，没有「稍后」可跳过系统表。"),
            ("在系统表选择读取类型", "选择允许读取的 Apple 健康类型。应用只读，不写入样本。"),
            ("打开摘要并下拉刷新", "授权完成不等于每项都有数。空白不是 0。"),
        ]
    else:
        name = "Open VitaGauge for the first time"
        steps = [
            ("Install from the App Store", f"Install VitaGauge from {STORE_EN}. iOS only."),
            ("Read the Health explanation and continue", "The first screen explains that the next step is the system sheet. The main button is Continue. There is no Later skip."),
            ("Choose read types", "Allow the Apple Health types you want the app to read. The app does not write samples."),
            ("Open the summary and refresh", "Permission is not the same as having numbers. A blank is not zero."),
        ]
    return {
        "@type": "HowTo",
        "name": name,
        "step": [
            {"@type": "HowToStep", "position": i + 1, "name": title, "text": text}
            for i, (title, text) in enumerate(steps)
        ],
    }


def topic_nav(items: list[tuple[str, str, str]]) -> str:
    links = "".join(
        f'<a href="{href}"><strong>{title}</strong><span>{blurb}</span></a>'
        for href, title, blurb in items
    )
    return f'<nav class="topic-list" aria-label="topics">{links}</nav>'


def page_app_zh() -> str:
    extra = json_ld([
        org(), software("zh"), website(),
        crumbs([("元气指数", url("app"))]),
    ])
    return (
        head(lang="zh-Hans", title="元气指数 VitaGauge：Apple 健康摘要、16 项趋势与本地问答",
             description="元气指数已在 App Store 上架。查看授权后的 Apple 健康摘要与 16 项趋势，用本地助理查询步数和睡眠，也可建立健康目标。无需账户或 API 即可开始。不是医疗器械。",
             canonical=url("app"), alt=url("en", "app"), depth="../", og_image="og-default.png", extra=extra)
        + header("zh", "app", "../")
        + f"""
<section class="hero">
  <div>
    {crumb_nav([("首页", "../app/"), ("官方网站", "../app/")])}
    <p class="kicker">元气指数已在 App Store 提供 · 版本 {VERSION}</p>
    <h1>把每天的健康，看得更明白。</h1>
    <p class="lead">从你授权的 Apple 健康记录出发，查看摘要和趋势，建立一个小目标，也可以用平常的话问问自己的数据。本地功能不必注册，也不必配置 API。</p>
    <div class="actions">{store_badge("zh")}<a class="button secondary" href="../features/">功能与价格</a></div>
    <p class="live"><i aria-hidden="true"></i>1.1.0 现已上架，含小组件、三种对话模式与 Pro 一次买断</p>
  </div>
  <div class="hero-art">
    <figure>
      <img class="screen" src="../assets/zh-Hans-summary.png" width="1242" height="2688" alt="元气指数健康摘要，示例为 6280 步、睡眠 7.5 小时" fetchpriority="high">
      <figcaption>真实界面 · 合成示例数据，不是某位用户的记录</figcaption>
    </figure>
  </div>
</section>
{rail(RAIL_ZH)}
<div class="proof">
  <div><strong>先在本机处理</strong><p>摘要、本地问答和目标默认留在设备上</p></div>
  <div><strong>16 项指标</strong><p>只读取已有记录，不编造测量值</p></div>
  <div><strong>一次买断 Pro</strong><p>无自动续订；基础功能免费</p></div>
</div>
<section class="section">
  <div class="section-heading">
    <h2>怎么用</h2>
    <p class="lead">打开应用后先阅读健康权限说明，点继续，再在系统弹窗里选择允许读取的类型。应用只读，不向 Apple 健康写入样本。</p>
  </div>
  <div class="steps">
    <article class="step">
      <figure><img class="screen" src="../assets/zh-Hans-summary.png" width="1242" height="2688" alt="健康摘要示例" loading="lazy"></figure>
      <div>
        <h3>看当天的摘要</h3>
        <p>把步数、睡眠、心率等已有记录放在同一页。没有记录就留空，不用 0 填补。部分指标需要 Apple Watch 或其他来源。</p>
      </div>
    </article>
    <article class="step">
      <figure><img class="screen" src="../assets/zh-Hans-assistant.png" width="1290" height="2796" alt="本地助理按日期汇总步数、睡眠和活动能量" loading="lazy"></figure>
      <div>
        <h3>用本地助理提问</h3>
        <p>可以问「今天走了多少步」「最近七天每天步数」，再追问「那昨天呢」。本地助理用规则和计算，不是通用大模型，也不会下诊断。</p>
      </div>
    </article>
    <article class="step">
      <figure><img class="widget" src="../assets/zh-Hans-widget.png" width="338" height="158" alt="主屏幕中号小组件显示步数、睡眠和活动能量" loading="lazy"></figure>
      <div>
        <h3>需要时再加深</h3>
        <p>免费含 1 个目标。iOS 17 可加主屏幕和锁屏小组件，显示最近一次同步，不是实时监测。Pro 解锁 30 天统计、两日比较、关联分析和在线 AI。</p>
      </div>
    </article>
  </div>
</section>
<section class="section">
  <div class="section-heading"><h2>已经上架的能力</h2></div>
  <div class="bento">
    <article class="card wide">
      <p class="meta">健康记录</p>
      <h3>16 项指标的摘要与趋势</h3>
      <p>{METRICS_ZH}。7 天趋势免费；30 天窗口属于 Pro。</p>
    </article>
    <article class="card">
      <p class="meta">三种对话模式</p>
      <h3>本地、API、本地 + API</h3>
      <p>本地不发送模型请求。API 只展示服务商回答，失败就报错。混合模式把简单查询留在本机。</p>
    </article>
    <article class="card">
      <p class="meta">13 种语言</p>
      <h3>界面已本地化</h3>
      <p>简体、繁体、英、西、法、德、日、韩、巴葡、俄、阿、印地、印尼。语音仅在设备端识别可用时提供。</p>
    </article>
  </div>
</section>
<section class="section">
  <h2>适合谁用</h2>
  <p class="lead">已经在用 iPhone 或 Apple Watch 记录活动，想把零散数据看成摘要和趋势的人。不面向 13 岁以下儿童，也不替代医生。</p>
  <div class="split">
    <div>
      <h3>它做什么</h3>
      <p>整理你授权的已有记录，显示当天摘要、趋势和目标进度，并用规则回答明确的记录问题。</p>
    </div>
    <div>
      <h3>它不做什么</h3>
      <p>不测量新的生理信号，不写入 Apple 健康，不诊断疾病，不提供处方或急救监护，也没有 Android 版本。</p>
    </div>
  </div>
</section>
{cite_box("zh")}
<section class="section">
  <div class="banner">
    <h2>健康记录怎么用，由你决定。</h2>
    <p>无需应用内账户，无广告，无行为分析 SDK。只有你配置自己的 AI 服务并单独同意后，当前问题和选定上下文才会从设备发到该服务商。</p>
    <p><a href="../">阅读隐私政策</a></p>
  </div>
</section>
<section class="section">
  <h2>界面一览</h2>
  <p class="note">下列截图由生产界面渲染，使用合成示例数据。</p>
  <div class="gallery">
    <figure><img src="../assets/zh-Hans-summary.png" width="1242" height="2688" alt="健康摘要示例" loading="lazy"><figcaption>今日摘要</figcaption></figure>
    <figure><img src="../assets/zh-Hans-assistant.png" width="1290" height="2796" alt="本地记录问答示例" loading="lazy"><figcaption>记录问答</figcaption></figure>
    <figure><img src="../assets/zh-Hans-trend.png" width="1242" height="2688" alt="步数趋势示例" loading="lazy"><figcaption>步数趋势</figcaption></figure>
    <figure><img src="../assets/zh-Hans-goal.png" width="1242" height="2688" alt="健康目标示例" loading="lazy"><figcaption>健康目标</figcaption></figure>
  </div>
</section>
<section class="section article">
  <h2>关于元气指数</h2>
  <dl class="facts">
    <dt>正式名称</dt><dd translate="no">元气指数 / VitaGauge</dd>
    <dt>开发者</dt><dd>智超 卫（zhichao wei）</dd>
    <dt>版本</dt><dd>1.1.0，2026 年 9 月 15 日上架</dd>
    <dt>系统</dt><dd>iOS 15 及以上；小组件需 iOS 17</dd>
    <dt>Bundle ID</dt><dd translate="no">{BUNDLE}</dd>
    <dt>App Store ID</dt><dd translate="no">{APP_ID}</dd>
    <dt>联系</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
  </dl>
</section>
<section class="section">
  <div class="notice">
    <h2>重要说明</h2>
    <p>{FACTS["disclaimerZh"]}</p>
  </div>
</section>
"""
        + footer("zh", "../")
    )


def page_app_en() -> str:
    extra = json_ld([
        org(), software("en"), website(),
        crumbs([("VitaGauge", url("en", "app"))]),
    ])
    return (
        head(lang="en", title="VitaGauge: Apple Health summary, 16 metrics and offline questions",
             description="VitaGauge is live on the App Store. Read authorized Apple Health summaries and 16 metrics, ask about steps and sleep without an API, and keep one free goal. Not a medical device.",
             canonical=url("en", "app"), alt=url("app"), depth="../../", og_image="og-default.png", extra=extra)
        + header("en", "app", "../../")
        + f"""
<section class="hero">
  <div>
    {crumb_nav([("Home", "../../en/app/"), ("Official site", "../../en/app/")])}
    <p class="kicker">Live on the App Store · version {VERSION}</p>
    <h1>A clearer view of everyday health.</h1>
    <p class="lead">Start from the Apple Health records you allow. See a summary and trends, keep a small goal, and ask about your numbers in ordinary language. Local features need no account and no API key.</p>
    <div class="actions">{store_badge("en")}<a class="button secondary" href="../features/">Features and pricing</a></div>
    <p class="live"><i aria-hidden="true"></i>1.1.0 is available, with widgets, three chat modes and one-time Pro</p>
  </div>
  <div class="hero-art">
    <figure>
      <img class="screen" src="../../assets/en-summary.png" width="1242" height="2688" alt="VitaGauge health summary sample showing 6,280 steps and 7.5 hours of sleep" fetchpriority="high">
      <figcaption>Actual interface · synthetic sample data, not a personal record</figcaption>
    </figure>
  </div>
</section>
{rail(RAIL_EN)}
<div class="proof">
  <div><strong>On-device first</strong><p>Summaries, local questions and goals stay on the phone</p></div>
  <div><strong>16 metrics</strong><p>Existing records only; readings are never invented</p></div>
  <div><strong>One-time Pro</strong><p>No renewal; free basics remain free</p></div>
</div>
<section class="section">
  <div class="section-heading">
    <h2>How it works</h2>
    <p class="lead">The first screen explains Health access. Tap Continue, then choose types in the system sheet. VitaGauge reads records and does not write samples to Apple Health.</p>
  </div>
  <div class="steps">
    <article class="step">
      <figure><img class="screen" src="../../assets/en-summary.png" width="1242" height="2688" alt="Health summary sample" loading="lazy"></figure>
      <div>
        <h3>See today together</h3>
        <p>Steps, sleep, heart rate and other allowed records share one page. Missing data stays blank instead of becoming zero. Some metrics need Apple Watch or another source.</p>
      </div>
    </article>
    <article class="step">
      <figure><img class="screen" src="../../assets/en-assistant.png" width="1290" height="2796" alt="Local assistant listing steps, sleep and active energy for a date" loading="lazy"></figure>
      <div>
        <h3>Ask the local assistant</h3>
        <p>Try “steps today” or “steps daily for the last 7 days”, then “what about yesterday”. It uses rules and math, not a general-purpose model, and it does not diagnose.</p>
      </div>
    </article>
    <article class="step">
      <figure><img class="widget" src="../../assets/en-widget.png" width="338" height="158" alt="Medium Home Screen widget with steps, sleep and active energy" loading="lazy"></figure>
      <div>
        <h3>Go further when you want</h3>
        <p>One goal is free. On iOS 17, widgets show the last sync; they are not live monitors. Pro unlocks 30-day stats, date comparisons, correlations and online AI.</p>
      </div>
    </article>
  </div>
</section>
<section class="section">
  <div class="section-heading"><h2>What ships today</h2></div>
  <div class="bento">
    <article class="card wide">
      <p class="meta">Records</p>
      <h3>Summaries and trends for 16 metrics</h3>
      <p>{METRICS_EN}. 7-day trends are free; 30-day windows need Pro.</p>
    </article>
    <article class="card">
      <p class="meta">Three modes</p>
      <h3>Local, API, Local + API</h3>
      <p>Local sends no model request. API shows the provider text or an error. Local + API keeps simple queries on-device.</p>
    </article>
    <article class="card">
      <p class="meta">13 languages</p>
      <h3>Localized interface</h3>
      <p>Voice input works only where the device can recognize speech on-device.</p>
    </article>
  </div>
</section>
<section class="section">
  <h2>Who it is for</h2>
  <p class="lead">People who already record activity on iPhone or Apple Watch and want those records as summaries and trends. Not for children under 13. Not a clinician.</p>
  <div class="split">
    <div>
      <h3>What it does</h3>
      <p>It organizes records you already authorized, shows a daily summary, trends and goal progress, and answers explicit record questions with rules and math.</p>
    </div>
    <div>
      <h3>What it does not do</h3>
      <p>It does not take new measurements, write to Apple Health, diagnose illness, prescribe, watch emergencies, or ship on Android.</p>
    </div>
  </div>
</section>
{cite_box("en")}
<section class="section">
  <div class="banner">
    <h2>Your records, your sending choices.</h2>
    <p>No app account, ads or analytics SDK. Text and selected context leave the device only after you configure a provider and give separate consent.</p>
    <p><a href="../../en/">Read the privacy policy</a></p>
  </div>
</section>
<section class="section">
  <h2>Interface</h2>
  <p class="note">Screenshots are the production UI with synthetic sample data.</p>
  <div class="gallery">
    <figure><img src="../../assets/en-summary.png" width="1242" height="2688" alt="Health summary sample" loading="lazy"><figcaption>Daily summary</figcaption></figure>
    <figure><img src="../../assets/en-assistant.png" width="1290" height="2796" alt="Local record question sample" loading="lazy"><figcaption>Record questions</figcaption></figure>
    <figure><img src="../../assets/en-trend.png" width="1242" height="2688" alt="Step trend sample" loading="lazy"><figcaption>Step trends</figcaption></figure>
    <figure><img src="../../assets/en-goal.png" width="1242" height="2688" alt="Goals sample" loading="lazy"><figcaption>Goals</figcaption></figure>
  </div>
</section>
<section class="section article">
  <h2>About VitaGauge</h2>
  <dl class="facts">
    <dt>Official name</dt><dd translate="no">VitaGauge / 元气指数</dd>
    <dt>Developer</dt><dd>智超 卫 (zhichao wei)</dd>
    <dt>Version</dt><dd>1.1.0, live 15 September 2026</dd>
    <dt>System</dt><dd>iOS 15 or later; widgets need iOS 17</dd>
    <dt>Bundle ID</dt><dd translate="no">{BUNDLE}</dd>
    <dt>App Store ID</dt><dd translate="no">{APP_ID}</dd>
    <dt>Contact</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
  </dl>
</section>
<section class="section">
  <div class="notice">
    <h2>Please read</h2>
    <p>{FACTS["disclaimerEn"]}</p>
  </div>
</section>
"""
        + footer("en", "../../")
    )


# Remaining pages continue in build_pages_more via exec of this module helpers.
# Features, support, privacy, terms, sources and 404 are defined below.

FEATURE_ROWS = [
    ("健康摘要与 16 项指标", "Health summary and 16 metrics", True, True),
    ("7 天趋势、本地基础查询", "7-day trends and basic local queries", True, True),
    ("内置生活习惯资料、使用帮助", "Built-in lifestyle information and help", True, True),
    ("健康目标", "Health goals", "1 个", "Multiple"),
    ("30 天趋势与统计", "30-day trends and statistics", False, True),
    ("两日比较、指标关联", "Date comparisons and correlations", False, True),
    ("自带 API Key 的在线 AI", "Online AI with your own API key", False, ("包含；模型费用另计", "Included; provider fees separate")),
]


def feature_cell(value, zh: bool) -> str:
    if value is True:
        return "包含" if zh else "Included"
    if value is False:
        return "不含" if zh else "No"
    if isinstance(value, tuple):
        return value[0] if zh else value[1]
    if value == "1 个":
        return "1 个" if zh else "1"
    if value == "Multiple":
        return "多个" if zh else "Multiple"
    return str(value)


def feature_table(zh: bool) -> str:
    rows = []
    for zh_n, en_n, free, pro in FEATURE_ROWS:
        name = zh_n if zh else en_n
        rows.append(
            f"<tr><th scope='row'>{name}</th><td>{feature_cell(free, zh)}</td><td>{feature_cell(pro, zh)}</td></tr>"
        )
    h1, h2, h3 = (("功能", "免费", "Pro 买断") if zh else ("Feature", "Free", "One-time Pro"))
    return f"<div class='table-wrap'><table><thead><tr><th scope='col'>{h1}</th><th scope='col'>{h2}</th><th scope='col'>{h3}</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>"


def page_features_zh() -> str:
    extra = json_ld([org(), software("zh"), website(), crumbs([("元气指数", url("app")), ("功能与价格", url("features"))])])
    return (
        head(lang="zh-Hans", title="功能与价格：元气指数免费版与 VitaGauge Pro 一次买断",
             description="元气指数免费含今日摘要、7 天趋势、本地问答和 1 个目标。Pro 一次买断解锁 30 天统计、多目标和自备 Key 的在线 AI。中国区首发价 ¥38，以 Apple 购买页为准。",
             canonical=url("features"), alt=url("en", "features"), depth="../", og_image="og-features.png", extra=extra)
        + header("zh", "features", "../")
        + f"""
<header class="page-head">
  {crumb_nav([("官方网站", "../app/"), ("功能与价格", "../features/")])}
  <h1>功能清楚，费用也清楚。</h1>
  <p class="lead">免费下载即可开始。需要更长窗口和更多目标时，再在应用内购买 Pro。1.1.0 已在 App Store 提供。</p>
  <div class="actions">{store_badge("zh")}<a class="button secondary" href="../support/">支持中心</a></div>
</header>
<section class="two">
  <article class="card">
    <h2>免费开始</h2>
    <p>无需 API Key，也不用订阅。含摘要、7 天趋势、基础本地问答、内置资料和 1 个目标。</p>
  </article>
  <article class="card">
    <h2>VitaGauge Pro</h2>
    <p class="price">¥38 <small>中国大陆首发买断价</small></p>
    <p>一次性非消耗型内购，商品 ID <span translate="no">com.vitagauge.pro.lifetime</span>。实际金额以 Apple 购买页为准。买断不含模型额度。</p>
  </article>
</section>
<section class="section">{feature_table(True)}
  <p class="note">无自动续订，未开启家庭共享。用原 Apple 账户恢复购买。未购买不影响免费功能。</p>
</section>
<section class="section">
  <h2>看看实际界面</h2>
  <div class="gallery">
    <figure><img src="../assets/zh-Hans-trend.png" width="1242" height="2688" alt="步数趋势示例" loading="lazy"><figcaption>步数趋势 · 示例数据</figcaption></figure>
    <figure><img src="../assets/zh-Hans-sleep.png" width="1290" height="2796" alt="睡眠趋势示例" loading="lazy"><figcaption>睡眠趋势 · 示例数据</figcaption></figure>
    <figure><img src="../assets/zh-Hans-local.png" width="1290" height="2796" alt="本地助理查询示例" loading="lazy"><figcaption>本地查询 · 无需 API</figcaption></figure>
    <figure><img src="../assets/zh-Hans-goal.png" width="1242" height="2688" alt="目标示例" loading="lazy"><figcaption>健康目标 · 示例目标</figcaption></figure>
  </div>
</section>
<section class="article">
  <h2>三种对话模式</h2>
  <p><strong>本地：</strong>规则、内置资料和确定性计算。不调用 API，也不下载模型。</p>
  <p><strong>API：</strong>只显示服务商正文；失败显示错误，不降级成本地答案。</p>
  <p><strong>本地 + API：</strong>简单查询留在本机，开放解释走在线。在线部分同样需要 Pro、自备 Key 和对接收方的同意。</p>
</section>
<section class="article">
  <h2>购买之前先知道边界</h2>
  <p>本地助理支持最近 1 到 30 天及明确日期。更长窗口、两日比较和关联需要 Pro。关联至少需要 7 个已结束的有效配对日，且两组都有变化；这不是因果。缺失不当成零。体温是体温类型，不是睡眠腕温。血压两项不跨时间拼成一次测量。睡眠按自然日分割。AI 回复不能替代诊疗。</p>
  <p><a href="../support/">支持中心</a>，<a href="../terms/">使用与购买说明</a></p>
</section>
{cite_box("zh")}
<section class="section">
  <div class="notice"><p>{FACTS["disclaimerZh"]}</p></div>
</section>
"""
        + footer("zh", "../")
    )


def page_features_en() -> str:
    extra = json_ld([org(), software("en"), website(), crumbs([("VitaGauge", url("en", "app")), ("Features", url("en", "features"))])])
    return (
        head(lang="en", title="Features and pricing: VitaGauge free plan and one-time Pro",
             description="VitaGauge is free for the daily summary, 7-day trends, local questions and one goal. One-time Pro unlocks 30-day stats, multiple goals and BYOK online AI. China list price CNY 38; Apple shows your price.",
             canonical=url("en", "features"), alt=url("features"), depth="../../", og_image="og-features.png", extra=extra)
        + header("en", "features", "../../")
        + f"""
<header class="page-head">
  {crumb_nav([("Official site", "../../en/app/"), ("Features", "../../en/features/")])}
  <h1>Clear features. Clear cost.</h1>
  <p class="lead">Download free. Buy Pro in the app when you want a longer window and more goals. Version 1.1.0 is live.</p>
  <div class="actions">{store_badge("en")}<a class="button secondary" href="../support/">Support</a></div>
</header>
<section class="two">
  <article class="card">
    <h2>Start free</h2>
    <p>No API key and no subscription. Summary, 7-day trends, basic local questions, built-in information and one goal.</p>
  </article>
  <article class="card">
    <h2>VitaGauge Pro</h2>
    <p class="price">CNY 38 <small>China launch list price, one time</small></p>
    <p>Non-consumable IAP, product ID <span translate="no">com.vitagauge.pro.lifetime</span>. Apple shows the local price. The purchase does not include model credits.</p>
  </article>
</section>
<section class="section">{feature_table(False)}
  <p class="note">No automatic renewal. Family Sharing is off. Restore with the original Apple Account. Free features stay available without buying.</p>
</section>
<section class="section">
  <h2>The shipping interface</h2>
  <div class="gallery">
    <figure><img src="../../assets/en-trend.png" width="1242" height="2688" alt="Step trend sample" loading="lazy"><figcaption>Step trends · sample data</figcaption></figure>
    <figure><img src="../../assets/en-sleep.png" width="1290" height="2796" alt="Sleep trend sample" loading="lazy"><figcaption>Sleep trends · sample data</figcaption></figure>
    <figure><img src="../../assets/en-local.png" width="1290" height="2796" alt="Local assistant sample" loading="lazy"><figcaption>Local query · no API</figcaption></figure>
    <figure><img src="../../assets/en-goal.png" width="1242" height="2688" alt="Goals sample" loading="lazy"><figcaption>Goals · sample target</figcaption></figure>
  </div>
</section>
<section class="article">
  <h2>Three conversation modes</h2>
  <p><strong>Local:</strong> rules, built-in notes and deterministic math. No API call and no model download.</p>
  <p><strong>API:</strong> shows the provider text or an error. It does not fall back to a local answer.</p>
  <p><strong>Local + API:</strong> simple queries stay on-device; open-ended text uses the provider. Online parts still need Pro, your key and recipient consent.</p>
</section>
<section class="article">
  <h2>Know the limits before you buy</h2>
  <p>The offline assistant supports recent 1 to 30 day windows and explicit dates. Longer windows, date comparisons and correlations need Pro. Correlation needs at least 7 finished paired days with variation in both series; it is not causation. Missing data is not zero. Body temperature is the body-temperature type, not sleep wrist temperature. The two blood-pressure readings are not joined across time into one measurement. Sleep is split by calendar day. AI replies do not replace care.</p>
  <p><a href="../support/">Support</a>, <a href="../terms/">use and purchases</a></p>
</section>
{cite_box("en")}
<section class="section">
  <div class="notice"><p>{FACTS["disclaimerEn"]}</p></div>
</section>
"""
        + footer("en", "../../")
    )


FAQ_ZH = [
    ("元气指数现在上架了吗？", "是。1.1.0 已在 App Store 提供，仅 iOS。商店页：https://apps.apple.com/app/id6762522305"),
    ("有 Android 或 Google Play 版本吗？", "没有。目前只发布 iOS。"),
    ("第一次打开要做什么？", "阅读健康权限说明后点「继续」，在系统弹窗选择允许读取的类型。稍后可到「设置 → 健康数据与权限」。应用只读，不写入 Apple 健康。"),
    ("为什么有的指标是空的？", "先确认 Apple 健康里该日期已有记录，再检查读取权限并刷新。空白不是 0，也不能单凭空白判断你拒绝了权限。"),
    ("没有 API Key 能用什么？", "摘要、7 天趋势、基础本地查询、内置生活习惯资料和 1 个目标。Pro 的本机统计也不需要 API。"),
    ("Pro 是订阅吗？", "不是。Pro 是一次性买断，中国区首发价 ¥38，以 Apple 购买页为准。无自动扣费，未开启家庭共享。在线模型费用由你的服务商另计。"),
    ("换手机怎么恢复？", "用原购买 Apple 账户，到「设置 → 元气指数 Pro → 恢复购买」。恢复不会带回聊天、目标或 API Key，这些文件不随本应用备份。"),
    ("已付款但没解锁？", "确认 Apple 交易已完成而不是待批准，联网后点恢复购买。退款请到 reportaproblem.apple.com。"),
    ("怎样连接在线 AI？", "「设置 → 连接在线 AI」选择服务商，粘贴自己的 Key 并验证保存。验证只发送固定测试文字。在线对话需要 Pro，首次向该接收方发送还要单独同意。"),
    ("如何撤回对某个服务商的同意？", "到「设置 → 第三方 AI 数据授权」撤回。撤回会停止后续发送并取消进行中的请求，但不能召回服务商已收到的数据。更换完整接收方网址后须重新同意。"),
    ("小组件为什么不更新？", "打开主应用同步。小组件读取本机快照，不是实时监测。超过约两小时会提示需要更新。午夜后不再显示昨天的数据。"),
    ("怎样改界面语言？", "「设置 → 应用语言」。支持简体、繁体、英、西、法、德、日、韩、巴葡、俄、阿、印地、印尼。"),
    ("语音不能用？", "检查麦克风和语音识别权限，以及设备是否支持端侧识别。应用不回退到云端识别。转写先进入输入框，核对后再发送。"),
    ("如何删除数据和密钥？", "助理菜单清空对话；目标页删除目标；连接在线 AI 页清除配置。卸载前请先清除 AI 配置。这不会删除 Apple 健康原始记录或服务商已收到的数据。"),
    ("能判断我是否生病吗？", "不能。应用不诊断、不给用药剂量、不监护急症。有症状请联系医生，紧急情况联系当地急救。"),
]

FAQ_EN = [
    ("Is VitaGauge on the App Store?", "Yes. Version 1.1.0 is live, iOS only. https://apps.apple.com/app/id6762522305"),
    ("Is there an Android app?", "No. There is no Google Play listing."),
    ("What should I do on first launch?", "Read the Health explanation, tap Continue, and choose types in the system sheet. Later use Settings → Health data & permissions. The app reads records and does not write to HealthKit."),
    ("Why are some metrics blank?", "Confirm Apple Health has records for that date, review read permissions, then refresh. A blank is not zero and does not by itself prove denied access."),
    ("What works without an API key?", "Summary, 7-day trends, basic local queries, built-in lifestyle information and one goal. Pro local statistics also work offline."),
    ("Is Pro a subscription?", "No. It is a one-time purchase. The China list price is CNY 38; Apple shows your price. No recurring charge and no Family Sharing. Your model provider may bill separately."),
    ("How do I restore on a new iPhone?", "Use the original Apple Account and open Settings → VitaGauge Pro → Restore purchases. Restore does not bring back chats, goals or API keys."),
    ("I paid but Pro is locked.", "Check that Apple finished the transaction, then restore on a network. Request refunds at reportaproblem.apple.com."),
    ("How do I connect online AI?", "Settings → Connect online AI. Paste your own key, verify and save. Verification sends fixed test text. Online chat needs Pro and separate consent for that recipient."),
    ("How do I withdraw consent for a provider?", "Open Settings → Third-party AI data authorization. Withdrawal stops later sends and cancels in-flight requests. It cannot recall data already delivered. Changing the full destination URL requires new consent."),
    ("Why is the widget stale?", "Open the main app to sync. Widgets read a local snapshot and are not live monitors. After about two hours they ask you to update. After midnight they hide yesterday's values."),
    ("How do I change the language?", "Settings → App language. The 13 locales are Simplified Chinese, Traditional Chinese, English, Spanish, French, German, Japanese, Korean, Brazilian Portuguese, Russian, Arabic, Hindi and Indonesian."),
    ("Voice input fails.", "Check microphone and speech permissions and on-device recognition support. There is no cloud speech fallback. Review the transcript in the editor before sending."),
    ("How do I delete data and keys?", "Clear chat, delete goals, and clear AI configuration. Clear the key before uninstalling. This does not erase Apple Health originals or data a provider already received."),
    ("Can it tell if I am ill?", "No. It does not diagnose, dose medication or watch emergencies. See a clinician for symptoms; use local emergency services for emergencies."),
]


def faq_html(pairs: list[tuple[str, str]]) -> str:
    return "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in pairs)


def page_support_zh() -> str:
    extra = json_ld([
        org(), software("zh"), website(),
        crumbs([("元气指数", url("app")), ("支持中心", url("support"))]),
        faq_schema(FAQ_ZH),
        howto_first_launch(True),
    ])
    return (
        head(lang="zh-Hans", title="支持中心：元气指数入门、权限、恢复购买与数据删除",
             description="元气指数支持：首次授权、指标空白、Pro 恢复与退款、三种对话模式、语音、小组件、权限、导出与删除。联系 weizhichao1027@gmail.com。",
             canonical=url("support"), alt=url("en", "support"), depth="../", og_image="og-support.png", extra=extra)
        + header("zh", "support", "../")
        + f"""
<header class="page-head">
  {crumb_nav([("官方网站", "../app/"), ("支持中心", "../support/")])}
  <h1>需要帮助，从这里开始。</h1>
  <p class="lead">应用没有开发者账户。按主题查看步骤，或直接写信。请勿发送 API Key、Apple 密码或不必要的健康资料。</p>
</header>
<div class="contact">
  <h2>联系开发者</h2>
  <p>请写明 App 版本（当前商店版本 1.1.0）、iOS 版本、复现步骤和错误提示。截图请遮盖私人信息。</p>
  <p><a class="button" href="mailto:{EMAIL}?subject=%E5%85%83%E6%B0%94%E6%8C%87%E6%95%B0%20%E6%94%AF%E6%8C%81">发送支持邮件</a></p>
  <p class="note">{EMAIL}</p>
</div>
<section class="section">
  {topic_nav([
      ("#start", "开始使用", "授权健康数据并查看摘要"),
      ("#account", "账户与恢复", "没有注册；恢复的是 Pro 权益"),
      ("#howto", "功能说明", "助理、目标、小组件、语音"),
      ("#permissions", "权限", "健康、照片、麦克风"),
      ("#billing", "购买与退款", "一次买断，经 Apple 处理"),
      ("#trouble", "排查", "空白指标、购买未解锁、小组件"),
      ("#data", "导出与删除", "本机清除与服务商数据"),
      ("#faq", "常见问题", "可展开的问答"),
  ])}
</section>
<article class="article">
  <section id="start">
    <h2>开始使用</h2>
    <p>从 <a href="{STORE_ZH}" rel="noopener">App Store</a> 安装元气指数。首次启动会说明下一步是系统健康权限，主按钮是「继续」。点继续后出现 iOS 授权表，选择允许读取的类型。设备不支持 HealthKit 时不会请求权限。</p>
    <p>授权完成不等于每项都有数。打开摘要，下拉刷新。无数据时，应用会区分「没有记录」和「无法读取」。可到「设置 → 健康数据与权限」再打开系统设置。</p>
  </section>
  <section id="account">
    <h2>账户与恢复购买</h2>
    <p>元气指数不提供开发者账户，也没有登录。免费功能只存在这台设备的应用数据里。</p>
    <p>Pro 权益跟你的 Apple 账户走。换机后用同一账户打开「设置 → 元气指数 Pro → 恢复购买」。恢复成功不会恢复聊天、目标、头像或 API Key。这些敏感文件被排除在系统备份之外。</p>
  </section>
  <section id="howto">
    <h2>功能怎么用</h2>
    <h3>本地助理</h3>
    <p>问明确日期或「昨天」「最近 7 天」。避免「昨晚」「上周」这类对不齐自然日汇总的说法。可看有效日平均、极值和逐日明细。</p>
    <h3>三种对话模式</h3>
    <p>在助理右上角「⋯ → 对话模式」或「设置 → 连接在线 AI」切换。本地：不发在线请求。API：只显示服务商正文，失败显示错误。本地 + API：简单查询留在本机，开放解释走在线。在线模式需要 Pro、已保存的 Key，以及对该接收方的同意。</p>
    <h3>目标</h3>
    <p>选指标、设目标值、查看最近 30 天进度，可暂停或删除。免费 1 个，多个需要 Pro。</p>
    <h3>小组件</h3>
    <p>iOS 17 可添加桌面小号/中号、锁屏圆形/矩形。每个实例可选步数、睡眠、活动能量、步行距离、体能训练或自动关注进行中目标，并可隐藏数值。打开应用同步后更新，显示同步时间。超过约两小时会提示需要更新。午夜后不再显示昨天的数据。不是实时监测，也不调用 AI。</p>
    <h3>界面语言</h3>
    <p>「设置 → 应用语言」。支持 13 种界面语言。语音只在设备端识别可用时提供。</p>
    <h3>语音</h3>
    <p>点按开始/结束，或按住说话。上滑或取消放弃。文字进入输入框，由你核对后发送。最长 55 秒。仅端侧识别。</p>
  </section>
  <section id="permissions">
    <h2>权限</h2>
    <p><strong>Apple 健康：</strong>只读 16 项指标，用于摘要、趋势、目标和助理。可在健康或 iOS 隐私设置中关闭。</p>
    <p><strong>照片：</strong>可选头像通过系统选择器读取一张照片，只保存在本机，不随 AI 请求发送。没有相机权限。</p>
    <p><strong>麦克风和语音识别：</strong>仅在你开始语音输入时使用，并在设备端转写。</p>
    <p>应用不请求跟踪，也不嵌入广告或行为分析 SDK。</p>
  </section>
  <section id="billing">
    <h2>购买、恢复与退款</h2>
    <p>Pro 是非消耗型一次买断，中国区首发价 ¥38，以购买页为准。待批准不是已完成。开发者收不到银行卡号。</p>
    <p>退款由 Apple 处理：<a href="https://reportaproblem.apple.com/">reportaproblem.apple.com</a>。许可遵循 <a href="{FACTS['legal']['standardEula']}">Apple 标准 EULA</a>。详见<a href="../terms/">使用说明</a>。</p>
  </section>
  <section id="trouble">
    <h2>排查</h2>
    <p>指标空白：健康 App 里有没有当天记录，本应用读取权限是否开启，然后刷新。部分指标依赖手表或其他 App。</p>
    <p>购买未解锁：网络正常后恢复购买；确认用的是付款账户。</p>
    <p>在线 AI 失败：查看服务商额度、接口地址和同意是否仍指向当前域名。API 模式失败不会改成本地答案。</p>
    <p>语音失败：权限、语言和设备是否支持端侧识别；到时限会保留已识别文字。</p>
    <p>小组件过期：先打开主应用同步。确认系统已允许该小组件显示，并在 iOS 17 及以上使用。</p>
  </section>
  <section id="data">
    <h2>导出与删除</h2>
    <p>应用没有独立的健康数据导出。原始记录请用 Apple 健康导出。</p>
    <p>本机：清空对话、删除目标、编辑或移除头像、清除 AI 配置（含 Keychain 密钥）。卸载前请先清除 AI 配置。卸载会删除沙盒文件，但不能保证密钥一定被删掉；如需立即失效，请在服务商处撤销 Key。</p>
    <p>服务商已收到的内容，请向该服务商申请访问或删除。开发者邮箱里的支持信件，可写信要求查阅、更正或删除。</p>
    <p>完整条款见<a href="../">隐私政策</a>。</p>
  </section>
  <section id="faq">
    <h2>常见问题</h2>
    {faq_html(FAQ_ZH)}
  </section>
</article>
{cite_box("zh")}
"""
        + footer("zh", "../")
    )


def page_support_en() -> str:
    extra = json_ld([
        org(), software("en"), website(),
        crumbs([("VitaGauge", url("en", "app")), ("Support", url("en", "support"))]),
        faq_schema(FAQ_EN),
        howto_first_launch(False),
    ])
    return (
        head(lang="en", title="Support: VitaGauge setup, permissions, restore and deletion",
             description="VitaGauge help: first Health permission, blank metrics, Pro restore and refunds, chat modes, voice, widgets, export and deletion. Email weizhichao1027@gmail.com.",
             canonical=url("en", "support"), alt=url("support"), depth="../../", og_image="og-support.png", extra=extra)
        + header("en", "support", "../../")
        + f"""
<header class="page-head">
  {crumb_nav([("Official site", "../../en/app/"), ("Support", "../../en/support/")])}
  <h1>Help, by topic.</h1>
  <p class="lead">There is no developer account. Follow the steps below, or email. Do not send API keys, Apple passwords or extra health details.</p>
</header>
<div class="contact">
  <h2>Contact the developer</h2>
  <p>Include app version (store version 1.1.0), iOS version, steps and the error text. Redact private information in screenshots.</p>
  <p><a class="button" href="mailto:{EMAIL}?subject=VitaGauge%20Support">Email support</a></p>
  <p class="note">{EMAIL}</p>
</div>
<section class="section">
  {topic_nav([
      ("#start", "Getting started", "Allow Health and open the summary"),
      ("#account", "Account and restore", "No sign-in; restore Pro only"),
      ("#howto", "How-tos", "Assistant, goals, widgets, voice"),
      ("#permissions", "Permissions", "Health, photos, microphone"),
      ("#billing", "Billing", "One-time purchase via Apple"),
      ("#trouble", "Troubleshooting", "Blanks, locked Pro, stale widgets"),
      ("#data", "Export and delete", "On-device clear and providers"),
      ("#faq", "FAQ", "Expandable answers"),
  ])}
</section>
<article class="article">
  <section id="start">
    <h2>Getting started</h2>
    <p>Install from the <a href="{STORE_EN}" rel="noopener">App Store</a>. The first screen explains that the next step is the system Health sheet. The main button is Continue. Then choose read types. If HealthKit is unavailable, the app does not request permission.</p>
    <p>Permission is not the same as having numbers. Open the summary and pull to refresh. Empty states distinguish missing records from read failures. Use Settings → Health data & permissions to reopen system settings.</p>
  </section>
  <section id="account">
    <h2>Account and restore</h2>
    <p>VitaGauge has no developer account and no login. Free data lives in this install.</p>
    <p>Pro follows your Apple Account. On a new device, Settings → VitaGauge Pro → Restore purchases. Restore does not return chats, goals, avatars or API keys. Those files are excluded from backups.</p>
  </section>
  <section id="howto">
    <h2>Feature how-tos</h2>
    <h3>Local assistant</h3>
    <p>Use an explicit date, yesterday, or the last 7 days. Vague phrases such as “last night” may not match daily totals.</p>
    <h3>Three conversation modes</h3>
    <p>Switch from ⋯ → Conversation mode or Settings → Connect online AI. Local sends no online request. API shows provider text or an error. Local + API keeps simple queries on-device. Online modes need Pro, a saved key and consent for that recipient.</p>
    <h3>Goals</h3>
    <p>Pick a metric and target, review about 30 days of progress, pause or delete. One goal is free.</p>
    <h3>Widgets</h3>
    <p>On iOS 17, add small or medium Home Screen widgets and circular or rectangular Lock Screen widgets. Each instance can show steps, sleep, active energy, walking distance, workouts, or an in-progress goal, and can hide values. Open the app to sync. After about two hours they ask for an update. After midnight they hide yesterday. They are not live monitors and do not call AI.</p>
    <h3>Language</h3>
    <p>Settings → App language. The interface has 13 locales. Voice input needs on-device recognition for that language.</p>
    <h3>Voice</h3>
    <p>Tap to start and stop, or hold to talk. Cancel discards the take. Text enters the editor for review. Limit 55 seconds. On-device recognition only.</p>
  </section>
  <section id="permissions">
    <h2>Permissions</h2>
    <p><strong>Apple Health:</strong> read-only access to 16 types. Turn off in Health or iOS privacy settings.</p>
    <p><strong>Photos:</strong> optional avatar through the system picker, stored on-device, never attached to AI requests. No camera permission.</p>
    <p><strong>Microphone and speech:</strong> used when you start voice input; recognition stays on-device.</p>
    <p>The app does not request tracking and does not embed ads or analytics SDKs.</p>
  </section>
  <section id="billing">
    <h2>Billing and refunds</h2>
    <p>Pro is a non-consumable one-time purchase. China list price CNY 38; Apple shows the local price. Pending approval is not a completed buy. We do not receive card numbers.</p>
    <p>Refunds: <a href="https://reportaproblem.apple.com/">reportaproblem.apple.com</a>. License: <a href="{FACTS['legal']['standardEula']}">Apple standard EULA</a>. See <a href="../terms/">use and purchases</a>.</p>
  </section>
  <section id="trouble">
    <h2>Troubleshooting</h2>
    <p>Blank metrics: check Apple Health for that date, read permission, then refresh.</p>
    <p>Pro still locked: restore on a network with the paying Apple Account.</p>
    <p>Online AI errors: provider quota, endpoint, and whether consent still matches the current host. API mode does not fall back to a local answer.</p>
    <p>Voice: permissions and on-device language support. At the time limit, recognized text is kept.</p>
    <p>Stale widget: open the main app first. Confirm the widget is allowed to show and that the device is on iOS 17 or later.</p>
  </section>
  <section id="data">
    <h2>Export and deletion</h2>
    <p>There is no in-app export of original health samples. Use Apple Health.</p>
    <p>On-device: clear chat, delete goals, remove the avatar, clear AI configuration (including the Keychain key). Clear the key before uninstalling. Uninstall removes sandbox files but is not a guarantee of key deletion. Revoke the key with the provider if it must die immediately.</p>
    <p>For information a provider already received, contact that provider. For support mail we hold, email access, correction or deletion requests.</p>
    <p>Full terms: <a href="../../en/">privacy policy</a>.</p>
  </section>
  <section id="faq">
    <h2>FAQ</h2>
    {faq_html(FAQ_EN)}
  </section>
</article>
{cite_box("en")}
"""
        + footer("en", "../../")
    )


def recipients_p(zh: bool) -> str:
    items = FACTS["dataPractices"]["presetAiRecipients"]
    body = "、".join(f"{r['name']}（{r['host']}）" for r in items) if zh else ", ".join(f"{r['name']} ({r['host']})" for r in items)
    if zh:
        return f"<p><strong>接收方：</strong>预设包括 {body}。也可配置自定义 HTTPS 服务。首次发送前，同意页会同时显示可识别的名称和实际域名；域名变更会使原同意失效。</p>"
    return f"<p><strong>Recipients:</strong> Presets include {body}. You may also set a custom HTTPS service. Before the first send, the consent screen shows the recognizable name and the actual host. A host change voids prior consent.</p>"


def page_privacy_zh() -> str:
    extra = json_ld([
        org(), software("zh"), website(),
        crumbs([("元气指数", url("app")), ("隐私政策", url())]),
        {
            "@type": "WebPage",
            "name": "隐私政策",
            "url": url(),
            "dateModified": REVIEWED,
            "datePublished": EFFECTIVE,
            "inLanguage": "zh-Hans",
            "about": {"@id": f"{BASE}/#app"},
            "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".digest", "#s1", "#s4"]},
        },
    ])
    return (
        head(lang="zh-Hans", title="隐私政策：元气指数 VitaGauge 如何处理健康与 AI 数据",
             description="元气指数隐私政策：控制者智超 卫，HealthKit 只读、可选照片头像、端侧语音、自备 Key 的第三方 AI、无分析 SDK、内购由 Apple 处理。生效 2026-09-16，复核 2026-09-18。",
             canonical=url(), alt=url("en"), depth="", og_image="og-privacy.png", extra=extra)
        + header("zh", "privacy", "")
        + f"""
<header class="page-head">
  {crumb_nav([("官方网站", "app/"), ("隐私政策", "./")])}
  <p class="kicker">隐私与数据</p>
  <h1>隐私政策</h1>
  <p class="lead">说明本机如何使用健康与个人数据，以及你选择在线 AI 时什么会离开设备。</p>
  <p class="note">{privacy_dates(True)}</p>
</header>
<section class="digest" id="digest">
  <h2>先读这一段</h2>
  <p>元气指数先在本机整理你授权的 Apple 健康记录。开发者不运营账户，也不接收健康问答。只有你配置自己的 API 并单独同意后，当前问题和选定上下文才会从设备发到该服务商。本政策本身不是同意。</p>
  <ul>
    <li>HealthKit 只读 16 项；不写入样本。</li>
    <li>无应用账户、无广告、无分析或崩溃 SDK，不请求跟踪。</li>
    <li>头像用系统照片选择器，无相机权限。</li>
    <li>语音只在设备端识别，最长 55 秒，核对后再发送。</li>
    <li>内购由 Apple 处理；开发者收不到银行卡号。</li>
  </ul>
  <p class="note">{FACTS["legal"]["privacyReviewNoteZh"]} App Store 隐私链接保持本页根路径。</p>
</section>
<nav class="contents" aria-label="目录">
  <h2>本页内容</h2>
  <ol>
    <li><a href="#s1">控制者与范围</a></li>
    <li><a href="#s2">数据类别</a></li>
    <li><a href="#s3">HealthKit</a></li>
    <li><a href="#s4">第三方 AI</a></li>
    <li><a href="#s5">共享、转移与处理者</a></li>
    <li><a href="#s6">本地存储与保留</a></li>
    <li><a href="#s7">你的权利与删除</a></li>
    <li><a href="#s8">内购</a></li>
    <li><a href="#s9">儿童与健康提示</a></li>
    <li><a href="#s10">本网站与更新</a></li>
    <li><a href="#s11">联系</a></li>
  </ol>
</nav>
<article class="policy-card article" id="policy">
  <section id="s1">
    <h2>控制者与范围</h2>
    <p>本政策适用于 iOS 应用「元气指数」（英文 VitaGauge，Bundle ID <span translate="no">{BUNDLE}</span>，App Store ID {APP_ID}）以及本 GitHub Pages 网站。个人信息控制者为开发者<strong>智超 卫</strong>（对外也写作 zhichao wei）。联系邮箱 {EMAIL}。</p>
    <p>应用不要求注册开发者账户，也不运营接收健康问答的 AI 中转服务器。Apple 作为 App Store 与 StoreKit 的独立控制者处理下载和内购。</p>
  </section>
  <section id="s2">
    <h2>数据类别</h2>
    <p><strong>健康与健身：</strong>经系统授权后读取的 16 类 Apple 健康记录，用于本机摘要、趋势、目标与助理。详见下一节。Privacy Manifest 将健康与健身标为与用户关联、用于应用功能，且不用于跟踪。</p>
    <p><strong>你提供的内容：</strong>聊天问题与回复、目标及备注、可选昵称和性别、可选头像、你填写的 AI 地址、模型名和 API Key。</p>
    <p><strong>照片：</strong>可选头像通过系统照片选择器（PHPicker）选取。头像经缩小后只存本机，不附带到 AI 请求，也不上传给开发者。应用不使用相机，Info.plist 无相机用途说明。</p>
    <p><strong>麦克风与语音：</strong>仅用于你主动开始的语音转文字。识别在支持的设备和语言上于设备端执行，不回退云端识别。识别文字先进入输入框，由你核对并发送后再按聊天规则处理。单次最长 55 秒。</p>
    <p><strong>设备偏好：</strong>应用使用 UserDefaults 保存界面语言、对话模式等功能设置（CA92.1），不用于广告。</p>
    <p><strong>支持通信：</strong>若你发信，开发者会收到邮箱、正文和附件，仅用于回应请求。</p>
    <p><strong>本站访问：</strong>页面无登录、表单、Cookie、分析脚本或外部字体。托管方 GitHub 可能处理 IP、浏览器和访问日志，见 <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener">GitHub 隐私声明</a>。</p>
    <p>应用<strong>没有</strong>第三方行为分析 SDK、广告 SDK 或崩溃收集 SDK，也不请求 App Tracking Transparency。</p>
  </section>
  <section id="s3">
    <h2>HealthKit</h2>
    <p>只有你通过系统授权后，应用才读取：{METRICS_ZH}。应用只读，不向 HealthKit 写入或修改样本。原始记录仍由 Apple 健康管理。体温是体温类型，不是睡眠腕温。收缩压与舒张压不跨时间拼成一次测量。睡眠合并重叠区间后按自然日及夏令时分割。</p>
    <p>首次启动先说明用途，主按钮为「继续」，然后进入系统权限表；不能用「稍后」跳过该系统表。之后可在 Apple 健康或「设置 → 健康数据与权限」更改。系统授权完成不代表每一类都有可见数据。</p>
    <p>iOS 17 及以上的小组件通过 App Group 读取本机摘要与目标快照，不调用 AI，也不发给开发者。快照使用文件保护并排除备份。打开应用同步后更新；小组件显示同步时间，可隐藏数值，不是实时监测。</p>
  </section>
  <section id="s4">
    <h2>何时发到第三方 AI</h2>
    <p>在任何个人数据发往第三方 AI 之前，应用内会说明将发送哪些数据，标明接收方名称和实际域名，并先征求同意。关闭或拒绝即取消发送。仅写在本政策中不构成同意。</p>
    <p>你主动发送、已配置自己的接口，并选择「API 对话」或由「本地 + API」触发在线请求且已单独同意后，当前问题和有长度限制的近期对话才会经 HTTPS 从设备直连到你配置的接口。API Key 用于该接口认证。</p>
    <p>新附带的健康信息按问题选择，通常最近 7 天，月度趋势最多 30 天；点名的历史日期可能另附该日汇总。问候和应用使用问题默认不附新的健康汇总。逐分钟原始样本、头像和模型内部推理不会作为附件发送。<strong>近期消息里已经出现的健康信息仍可能随在线问题发出</strong>，可先清空对话。</p>
    <p>本地模式即使保存了 Key 也不发送在线对话。更换接收地址须重新同意。撤回同意会停止当前请求并阻止新的发送，但不能收回已到达接收方的数据。</p>
  </section>
  <section id="s5">
    <h2>共享、跨境与处理者</h2>
    <p>开发者不出售健康信息，不使用健康数据投放广告。</p>
    {recipients_p(True)}
    <p><strong>同等保护：</strong>获准接收个人数据的第三方须提供不低于本政策及 Apple 适用要求的保护，不得出售健康数据，也不得将 HealthKit 数据用于广告、营销或基于用途的数据挖掘。若服务商条款不满足，请不要连接。</p>
    <p>服务商独立处理其收到的信息，保存期、是否用于改进模型、处理地区和删除方式以其条款和你的账户设置为准，<strong>可能在你所在地区以外处理</strong>。发送前请阅读该服务商政策。</p>
    <p>Apple 处理购买与收据。GitHub 处理本站托管流量。开发者不另设分析或广告处理者。</p>
  </section>
  <section id="s6">
    <h2>本地存储、保留与保护</h2>
    <p>应用不把原始健康样本批量复制到独立健康库。目标、刷新日志、资料、头像、AI 元数据和聊天存在应用沙盒，使用 iOS 文件保护并排除系统备份。</p>
    <p>会话最多约 100 条、正文合计约 200,000 个 UTF-8 字节、单条约 24,000 字符。模型推理不持久化。API Key 存在解锁后可用、仅当前设备的 Keychain，与地址和协议绑定，不同步 iCloud Keychain，不写入安装包或日志。</p>
    <p>进入后台时会遮盖任务切换器中的敏感界面，并取消进行中的 AI、语音和健康查询。这些措施降低风险，但不能保证绝对安全。</p>
  </section>
  <section id="s7">
    <h2>选择、权利、导出与删除</h2>
    <p>你可以在系统设置管理健康、照片、麦克风和语音权限；在应用内撤回第三方 AI 同意、清除 AI 配置、清空聊天、删除目标或改资料。</p>
    <p>应用没有独立健康导出。原始健康数据请用 Apple 健康导出。针对开发者持有的支持邮件，你可以请求查阅、更正或删除。针对服务商已接收的数据，请向该服务商行使权利。</p>
    <p>卸载会删除沙盒文件。<strong>卸载前请先「清除 AI 配置」</strong>；不要把卸载当成密钥一定消失的保证。若密钥须立即失效，请在服务商处撤销或轮换。</p>
  </section>
  <section id="s8">
    <h2>App 内购买</h2>
    <p>VitaGauge Pro（<span translate="no">{FACTS['iap']['productId']}</span>）是一次性非消耗型商品，由 Apple StoreKit 验证。开发者根据交易状态解锁功能，不会收到银行卡资料。退款由 Apple 处理。买断不包含 API Key 或模型费用。</p>
  </section>
  <section id="s9">
    <h2>儿童与健康提示</h2>
    <p>应用不面向 13 岁以下儿童。App Store 年龄分级为 12+。若认为儿童向开发者提供了个人信息，请发信以便处理。</p>
    <p>{FACTS["disclaimerZh"]} 急症请联系当地急救。</p>
  </section>
  <section id="s10">
    <h2>本网站与政策更新</h2>
    <p>本站由 GitHub Pages 托管，无表单、Cookie、分析脚本或外部字体。公开的机器可读事实见 <a href="llms.txt">llms.txt</a> 与 <a href="product-facts.json">product-facts.json</a>。重大变更会在本页更新日期，并通过应用或 App Store 更新说明告知。需要同意的新处理会另行征求同意。应用内离线政策摘要会随下一版构建同步本页复核日期。</p>
  </section>
  <section id="s11">
    <h2>联系我们</h2>
    <p>隐私、支持或数据请求：<a href="mailto:{EMAIL}">{EMAIL}</a>。请写明「元气指数 / VitaGauge」，只提供处理所需信息。</p>
  </section>
</article>
{cite_box("zh")}
"""
        + footer("zh", "")
    )


def page_privacy_en() -> str:
    extra = json_ld([
        org(), software("en"), website(),
        crumbs([("VitaGauge", url("en", "app")), ("Privacy", url("en"))]),
        {"@type": "WebPage", "name": "Privacy Policy", "url": url("en"), "dateModified": REVIEWED, "datePublished": EFFECTIVE, "inLanguage": "en", "about": {"@id": f"{BASE}/#app"}},
    ])
    return (
        head(lang="en", title="Privacy Policy: how VitaGauge handles health and AI data",
             description="VitaGauge privacy policy: controller 智超 卫 (zhichao wei). HealthKit read-only, optional photo avatar, on-device speech, BYOK third-party AI, no analytics SDK, Apple IAP. Effective 16 September 2026, reviewed 18 September 2026.",
             canonical=url("en"), alt=url(), depth="../", og_image="og-privacy.png", extra=extra)
        + header("en", "privacy", "../")
        + f"""
<header class="page-head">
  {crumb_nav([("Official site", "../en/app/"), ("Privacy", "../en/")])}
  <p class="kicker">Privacy and data</p>
  <h1>Privacy Policy</h1>
  <p class="lead">What stays on the device, what you may send to an AI provider you choose, and how to ask us about support mail.</p>
  <p class="note">{privacy_dates(False)}</p>
</header>
<section class="digest" id="digest">
  <h2>Read this first</h2>
  <p>VitaGauge organizes authorized Apple Health records on the device. The developer does not run an account system and does not receive health chats. Text and selected context leave the device only after you configure your own API and give separate consent. This policy is not consent.</p>
  <ul>
    <li>HealthKit is read-only for 16 types. The app does not write samples.</li>
    <li>No app account, ads, analytics or crash SDK, and no tracking prompt.</li>
    <li>Avatars use the system photo picker. There is no camera permission.</li>
    <li>Speech recognition is on-device only, max 55 seconds, review before send.</li>
    <li>Apple processes in-app purchases. We do not receive card numbers.</li>
  </ul>
  <p class="note">{FACTS["legal"]["privacyReviewNoteEn"]} The App Store Privacy URL stays on this English page for English listings.</p>
</section>
<nav class="contents" aria-label="Contents">
  <h2>On this page</h2>
  <ol>
    <li><a href="#s1">Controller and scope</a></li>
    <li><a href="#s2">Categories of data</a></li>
    <li><a href="#s3">HealthKit</a></li>
    <li><a href="#s4">Third-party AI</a></li>
    <li><a href="#s5">Sharing, transfers and processors</a></li>
    <li><a href="#s6">Storage and retention</a></li>
    <li><a href="#s7">Rights and deletion</a></li>
    <li><a href="#s8">In-app purchases</a></li>
    <li><a href="#s9">Children and health notice</a></li>
    <li><a href="#s10">This website and changes</a></li>
    <li><a href="#s11">Contact</a></li>
  </ol>
</nav>
<article class="policy-card article" id="policy">
  <section id="s1">
    <h2>Controller and scope</h2>
    <p>This policy covers the iOS app VitaGauge (元气指数, bundle ID <span translate="no">{BUNDLE}</span>, App Store ID {APP_ID}) and this GitHub Pages site. The controller is <strong>智超 卫</strong> (zhichao wei), email {EMAIL}.</p>
    <p>The app has no developer account and no server that relays health chats. Apple is an independent controller for App Store distribution and StoreKit purchases.</p>
  </section>
  <section id="s2">
    <h2>Categories of data</h2>
    <p><strong>Health and fitness:</strong> 16 Apple Health types after system permission, for on-device summary, trends, goals and the assistant. The Privacy Manifest marks health and fitness as linked, used for app functionality, and not used for tracking.</p>
    <p><strong>Content you enter:</strong> chat, goals and notes, optional nickname and gender, optional avatar, and the AI endpoint, model name and API key you type.</p>
    <p><strong>Photos:</strong> an optional avatar through the system photo picker (PHPicker). It is resized and stored on-device only, never attached to AI requests or sent to the developer. There is no camera permission.</p>
    <p><strong>Microphone and speech:</strong> used when you start speech-to-text. Recognition is on-device for supported devices and languages, with no cloud fallback. Text lands in the editor for review. Maximum 55 seconds.</p>
    <p><strong>Preferences:</strong> UserDefaults for language and conversation mode (CA92.1), not advertising.</p>
    <p><strong>Support mail:</strong> if you email us, we receive your address, message and attachments to respond.</p>
    <p><strong>This website:</strong> no sign-in, forms, cookies, analytics scripts or external fonts. GitHub may process IPs and logs under the <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener">GitHub Privacy Statement</a>.</p>
    <p>The app has <strong>no</strong> third-party analytics, advertising or crash SDK, and does not request tracking permission.</p>
  </section>
  <section id="s3">
    <h2>HealthKit</h2>
    <p>After permission the app may read {METRICS_EN}. It does not write HealthKit samples. Originals stay in Apple Health. Body temperature is the body-temperature type, not sleep wrist temperature. Systolic and diastolic readings are not joined across time into one measurement. Sleep intervals are merged, then split by calendar day and daylight-saving boundaries.</p>
    <p>First launch explains the next step, the main button is Continue, then the system sheet appears. There is no Later control that skips that sheet. You can change access in Apple Health or Settings → Health data & permissions.</p>
    <p>Widgets on iOS 17+ read a local App Group snapshot. They do not call AI or send data to the developer. The snapshot uses file protection and is excluded from backups. Open the app to sync. Widgets are not real-time monitors.</p>
  </section>
  <section id="s4">
    <h2>When data goes to third-party AI</h2>
    <p>Before any personal data is sent, the app names the recipient and host, lists what will be sent, and asks permission. Closing or declining cancels the send. This policy alone is not consent.</p>
    <p>After you configure an endpoint, choose API or trigger an online request in Local + API, consent, and send, the current question and a bounded recent chat go from the device over HTTPS. Your key authenticates that request.</p>
    <p>New health context is usually 7 days, or up to 30 for monthly trends. Minute-level samples, avatars and hidden model reasoning are not attached. <strong>Health text already inside recent messages may still be sent</strong> until you clear the chat.</p>
    <p>Local mode sends no online conversation even if a key is saved. Changing the destination requires new consent. Withdrawal cannot recall data already delivered.</p>
  </section>
  <section id="s5">
    <h2>Sharing, transfers and processors</h2>
    <p>The developer does not sell health information or use it for advertising.</p>
    {recipients_p(False)}
    <p><strong>Equal protection:</strong> a recipient must not sell health data or use HealthKit data for advertising, marketing or use-based mining. Do not connect if its terms fall short.</p>
    <p>Providers process what they receive under their terms. Retention, optional training, location and deletion are theirs, and <strong>processing may occur outside your country</strong>.</p>
    <p>Apple processes purchases. GitHub hosts this site. We add no analytics or advertising processors.</p>
  </section>
  <section id="s6">
    <h2>Storage and retention</h2>
    <p>The app does not bulk-copy raw samples into a second health database. Goals, profile, avatar, AI metadata and chats use file protection and are excluded from backups.</p>
    <p>Chat is bounded (about 100 messages, 200,000 UTF-8 bytes, 24,000 characters each). Keys use device-only Keychain and are not synced with iCloud Keychain.</p>
    <p>Backgrounding covers the app switcher and cancels in-flight AI, voice and health queries. No storage or transfer is absolutely secure.</p>
  </section>
  <section id="s7">
    <h2>Rights and deletion</h2>
    <p>You can manage Health, Photos, microphone and speech in iOS settings; revoke AI consent, clear configuration, clear chat, delete goals or edit the profile in the app.</p>
    <p>There is no in-app export of original health samples. Use Apple Health. For support mail we hold, you may request access, correction or deletion. For data a provider already received, contact that provider.</p>
    <p>Uninstalling removes sandbox files. <strong>Clear AI configuration before uninstalling</strong>. Uninstall is not a guarantee that the Keychain item is gone. Revoke or rotate the key with the provider if it must become invalid immediately.</p>
  </section>
  <section id="s8">
    <h2>In-app purchases</h2>
    <p>VitaGauge Pro (<span translate="no">{FACTS['iap']['productId']}</span>) is a one-time non-consumable product verified with StoreKit. We unlock features from the transaction state and do not receive card numbers. Apple handles refunds. The purchase does not include an API key or model credits.</p>
  </section>
  <section id="s9">
    <h2>Children and health notice</h2>
    <p>The app is not intended for children under 13. The App Store rating is 12+. Contact us if you believe a child sent personal information to the developer.</p>
    <p>{FACTS["disclaimerEn"]} Use local emergency services for urgent situations.</p>
  </section>
  <section id="s10">
    <h2>This website and changes</h2>
    <p>The site is hosted on GitHub Pages, with no forms, cookies, analytics scripts or external fonts. Machine-readable facts: <a href="../llms.txt">llms.txt</a> and <a href="../product-facts.json">product-facts.json</a>. Material updates will change the date on this page and may appear in the app or App Store notes. New processing that needs consent will ask for it. The in-app offline summary date will follow this review date in the next app build.</p>
  </section>
  <section id="s11">
    <h2>Contact</h2>
    <p>Privacy, support or data requests: <a href="mailto:{EMAIL}">{EMAIL}</a>. Write “VitaGauge / 元气指数” and send only what is needed.</p>
  </section>
</article>
{cite_box("en")}
"""
        + footer("en", "../")
    )


def page_terms_zh() -> str:
    extra = json_ld([org(), website(), crumbs([("元气指数", url("app")), ("使用说明", url("terms"))])])
    return (
        head(lang="zh-Hans", title="使用与购买说明 · 元气指数",
             description="元气指数由智超 卫开发。Pro 为一次性非消耗型内购，无自动续订，未开家庭共享。退款由 Apple 处理。应用不是医疗器械。",
             canonical=url("terms"), alt=url("en", "terms"), depth="../", extra=extra)
        + header("zh", "terms", "../")
        + f"""
<header class="page-head">
  {crumb_nav([("官方网站", "../app/"), ("使用说明", "../terms/")])}
  <h1>使用与购买说明</h1>
  <p class="note">{REVIEWED}</p>
</header>
<article class="article">
  <section>
    <h2>产品与开发者</h2>
    <p>元气指数由智超 卫开发，面向 iPhone（iOS 15+），用于整理已授权的 Apple 健康记录、管理个人目标和查看一般资料。当前商店版本 1.1.0 已上架，含 Pro 与小组件。</p>
  </section>
  <section>
    <h2>购买与恢复</h2>
    <p>Pro 是一次性非消耗型内购，商品 <span translate="no">com.vitagauge.pro.lifetime</span>，无自动续订，未开启家庭共享。中国区首发价 ¥38，以 Apple 购买页为准。买断不含 API Key 或模型费用。用原 Apple 账户恢复。待批准不是已完成购买。退款：<a href="https://reportaproblem.apple.com/">reportaproblem.apple.com</a>。</p>
  </section>
  <section>
    <h2>你选择的在线服务</h2>
    <p>你自行选择服务商并承担其费用。不要通过支持邮件发送 API Key。更换接收方需重新同意。应用无法删除服务商已收到的信息。</p>
  </section>
  <section>
    <h2>健康与数据边界</h2>
    <p>{FACTS["disclaimerZh"]} 缺失数据不等于零。应用不面向 13 岁以下儿童。</p>
  </section>
  <section>
    <h2>许可</h2>
    <p>如无另外适用的协议，许可遵循 <a href="{FACTS['legal']['standardEula']}">Apple 标准最终用户许可协议</a>。本页不替代 Apple 购买条款或消费者依法享有的权利。</p>
  </section>
  <section>
    <h2>联系</h2>
    <p><a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="../support/">支持中心</a> · <a href="../">隐私政策</a></p>
  </section>
</article>
"""
        + footer("zh", "../")
    )


def page_terms_en() -> str:
    extra = json_ld([org(), website(), crumbs([("VitaGauge", url("en", "app")), ("Use and purchases", url("en", "terms"))])])
    return (
        head(lang="en", title="Use and purchases · VitaGauge",
             description="VitaGauge is developed by 智超 卫. Pro is a one-time non-consumable IAP with no renewal and no Family Sharing. Apple handles refunds. Not a medical device.",
             canonical=url("en", "terms"), alt=url("terms"), depth="../../", extra=extra)
        + header("en", "terms", "../../")
        + f"""
<header class="page-head">
  {crumb_nav([("Official site", "../../en/app/"), ("Use and purchases", "../../en/terms/")])}
  <h1>Use and purchases</h1>
  <p class="note">{REVIEWED}</p>
</header>
<article class="article">
  <section>
    <h2>About this app</h2>
    <p>VitaGauge is developed by 智超 卫 (zhichao wei) for iPhone (iOS 15+). It organizes authorized Apple Health records, personal goals and general information. Version 1.1.0 is live, including Pro and widgets.</p>
  </section>
  <section>
    <h2>Purchases and restoration</h2>
    <p>Pro is a one-time non-consumable product (<span translate="no">com.vitagauge.pro.lifetime</span>) with no renewal and no Family Sharing. China list price CNY 38; Apple shows the local price. The purchase does not include an API key or model credits. Restore with the original Apple Account. Pending approval is not a completed purchase. Refunds: <a href="https://reportaproblem.apple.com/">reportaproblem.apple.com</a>.</p>
  </section>
  <section>
    <h2>Your online provider</h2>
    <p>You choose and pay your provider. Never send API keys in support mail. Changing recipient requires new consent. The app cannot delete information a provider already received.</p>
  </section>
  <section>
    <h2>Health and data limits</h2>
    <p>{FACTS["disclaimerEn"]} Missing measurements are not zero. The app is not intended for children under 13.</p>
  </section>
  <section>
    <h2>License</h2>
    <p>Unless a separate agreement applies, the <a href="{FACTS['legal']['standardEula']}">Apple standard Licensed Application End User License Agreement</a> governs the license. This page does not replace Apple purchase terms or statutory consumer rights.</p>
  </section>
  <section>
    <h2>Contact</h2>
    <p><a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="../support/">Support</a> · <a href="../../en/">Privacy</a></p>
  </section>
</article>
"""
        + footer("en", "../../")
    )


def page_sources_zh() -> str:
    extra = json_ld([org(), website(), crumbs([("元气指数", url("app")), ("资料来源", url("sources"))])])
    return (
        head(lang="zh-Hans", title="资料来源 · 元气指数",
             description="元气指数内置生活习惯资料参考 CDC 与世界卫生组织公开页面；记录统计依据本机 Apple 健康数据。引用不代表机构背书或诊疗。",
             canonical=url("sources"), alt=url("en", "sources"), depth="../", extra=extra)
        + header("zh", "sources", "../")
        + f"""
<header class="page-head">
  {crumb_nav([("官方网站", "../app/"), ("资料来源", "../sources/")])}
  <h1>资料来源</h1>
  <p class="lead">内置生活习惯资料参考以下公开来源；记录统计依据本机 Apple 健康数据。引用不代表机构背书、医疗认证或个体化诊疗。</p>
  <p class="note">{REVIEWED}</p>
</header>
<article class="article">
  <section><h2><a href="https://www.cdc.gov/sleep/about/index.html" rel="noopener">CDC · About Sleep</a></h2></section>
  <section><h2><a href="https://www.who.int/news-room/fact-sheets/detail/physical-activity" rel="noopener">WHO · Physical activity</a></h2></section>
  <section><h2><a href="https://www.who.int/news-room/fact-sheets/detail/healthy-diet" rel="noopener">WHO · Healthy diet</a></h2></section>
  <section><h2><a href="https://developer.apple.com/documentation/healthkit" rel="noopener">Apple · HealthKit</a></h2></section>
</article>
"""
        + footer("zh", "../")
    )


def page_sources_en() -> str:
    extra = json_ld([org(), website(), crumbs([("VitaGauge", url("en", "app")), ("Sources", url("en", "sources"))])])
    return (
        head(lang="en", title="Sources · VitaGauge",
             description="VitaGauge built-in lifestyle notes cite CDC and WHO public pages. Record statistics use local Apple Health data. Sources do not imply endorsement or treatment.",
             canonical=url("en", "sources"), alt=url("sources"), depth="../../", extra=extra)
        + header("en", "sources", "../../")
        + f"""
<header class="page-head">
  {crumb_nav([("Official site", "../../en/app/"), ("Sources", "../../en/sources/")])}
  <h1>Sources</h1>
  <p class="lead">Built-in lifestyle information uses these public sources. Record statistics use local Apple Health data. Sources do not imply endorsement, medical validation or personalized treatment.</p>
  <p class="note">{REVIEWED}</p>
</header>
<article class="article">
  <section><h2><a href="https://www.cdc.gov/sleep/about/index.html" rel="noopener">CDC · About Sleep</a></h2></section>
  <section><h2><a href="https://www.who.int/news-room/fact-sheets/detail/physical-activity" rel="noopener">WHO · Physical activity</a></h2></section>
  <section><h2><a href="https://www.who.int/news-room/fact-sheets/detail/healthy-diet" rel="noopener">WHO · Healthy diet</a></h2></section>
  <section><h2><a href="https://developer.apple.com/documentation/healthkit" rel="noopener">Apple · HealthKit</a></h2></section>
</article>
"""
        + footer("en", "../../")
    )


def page_404() -> str:
    extra = '<meta name="robots" content="noindex">'
    return (
        head(lang="zh-Hans", title="页面未找到 · 元气指数",
             description="元气指数网站没有这个地址。可前往官方网站、支持中心或隐私政策。",
             canonical=f"{BASE}/404.html", alt=url("en", "app"), depth="", extra=extra)
        + header("zh", "404", "")
        + f"""
<header class="page-head">
  <h1>页面未找到</h1>
  <p class="lead">这个地址不存在。元气指数已在 App Store 上架，你也可以打开下面的页面。</p>
  <div class="actions">
    <a class="button" href="app/">官方网站</a>
    <a class="button secondary" href="support/">支持中心</a>
    <a class="button secondary" href="./">隐私政策</a>
    <a class="button secondary" href="en/app/" lang="en">English site</a>
  </div>
</header>
"""
        + footer("zh", "")
    )


PAGES = {
    "app/index.html": page_app_zh,
    "en/app/index.html": page_app_en,
    "features/index.html": page_features_zh,
    "en/features/index.html": page_features_en,
    "support/index.html": page_support_zh,
    "en/support/index.html": page_support_en,
    "index.html": page_privacy_zh,
    "en/index.html": page_privacy_en,
    "terms/index.html": page_terms_zh,
    "en/terms/index.html": page_terms_en,
    "sources/index.html": page_sources_zh,
    "en/sources/index.html": page_sources_en,
    "404.html": page_404,
}

SITEMAP_PATHS = [
    ("", "zh-Hans", "en/"),
    ("en/", "en", ""),
    ("app/", "zh-Hans", "en/app/"),
    ("en/app/", "en", "app/"),
    ("features/", "zh-Hans", "en/features/"),
    ("en/features/", "en", "features/"),
    ("support/", "zh-Hans", "en/support/"),
    ("en/support/", "en", "support/"),
    ("terms/", "zh-Hans", "en/terms/"),
    ("en/terms/", "en", "terms/"),
    ("sources/", "zh-Hans", "en/sources/"),
    ("en/sources/", "en", "sources/"),
]


def write_sitemap() -> None:
    ns = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"'
    chunks = ['<?xml version="1.0" encoding="UTF-8"?>', f"<urlset {ns}>"]
    images = {
        "app/": ["zh-Hans-summary.png", "zh-Hans-assistant.png", "zh-Hans-widget.png"],
        "en/app/": ["en-summary.png", "en-assistant.png", "en-widget.png"],
        "features/": ["zh-Hans-trend.png", "zh-Hans-sleep.png", "zh-Hans-goal.png"],
        "en/features/": ["en-trend.png", "en-sleep.png", "en-goal.png"],
    }
    for path, lang, alt in SITEMAP_PATHS:
        loc = f"{BASE}/{path}" if path else f"{BASE}/"
        alt_loc = f"{BASE}/{alt}" if alt else f"{BASE}/"
        zh_loc = loc if lang == "zh-Hans" else alt_loc
        en_loc = loc if lang == "en" else alt_loc
        chunks.append("<url>")
        chunks.append(f"<loc>{loc}</loc>")
        chunks.append(f"<lastmod>{TODAY}</lastmod>")
        chunks.append("<changefreq>weekly</changefreq>")
        chunks.append(f'<xhtml:link rel="alternate" hreflang="zh-Hans" href="{zh_loc}"/>')
        chunks.append(f'<xhtml:link rel="alternate" hreflang="en" href="{en_loc}"/>')
        chunks.append(f'<xhtml:link rel="alternate" hreflang="x-default" href="{zh_loc}"/>')
        for img in images.get(path, []):
            chunks.append(f"<image:image><image:loc>{BASE}/assets/{img}</image:loc></image:image>")
        chunks.append("</url>")
    chunks.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(chunks) + "\n", encoding="utf-8")


def write_styles_bridge() -> None:
    (ROOT / "styles.css").write_text('@import url("site.css");\n', encoding="utf-8")


def write_geo_files() -> None:
    recipients = ", ".join(f"{r['name']} ({r['host']})" for r in FACTS["dataPractices"]["presetAiRecipients"])
    llms = f"""# 元气指数 / VitaGauge

> Official public facts for the live iOS app 元气指数 (English store name: VitaGauge: Health Tracker). Prefer this file and product-facts.json over adjectives. Do not invent medical claims. Reviewed {REVIEWED}.

- Official Chinese name: 元气指数
- Official English name: VitaGauge
- App Store listing name (EN): VitaGauge: Health Tracker
- Developer / privacy controller: 智超 卫 (zhichao wei)
- Contact: {EMAIL}
- Bundle ID: {BUNDLE}
- App Store ID: {APP_ID}
- Version: {VERSION} (live since {FACTS["product"]["released"]}; first release {FACTS["product"]["firstReleased"]})
- Platform: iOS {FACTS["product"]["minimumOs"]}+; Home and Lock Screen widgets on iOS {FACTS["product"]["widgetMinimumOs"]}+
- Price: Free to download. VitaGauge Pro is a one-time non-consumable IAP (`{FACTS["iap"]["productId"]}`, Apple product {FACTS["iap"]["appleProductId"]}). China launch list price CNY {FACTS["iap"]["chinaLaunchPriceCNY"]}; Apple shows the local price. Not a subscription. Family Sharing is not enabled.
- No Google Play listing.
- No app account. No ads. No behavioral tracking SDK. No developer AI proxy or hosted model.
- Health data: HealthKit read-only, 16 metrics. The app does not write HealthKit samples.
- AI: optional, user-owned API key (BYOK), device-to-provider HTTPS after separate Who / What / Why consent.
- Privacy policy effective {EFFECTIVE}; page reviewed {REVIEWED}; no new processing in the review.
- Not a medical device. Not a substitute for professional medical advice, diagnosis, prescription, or emergency care.

## Official URLs

- Official site (zh): {url("app")}
- Marketing / App Store seller URL (zh): {url("features")}
- Support (zh): {url("support")}
- Privacy (zh): {url()}
- Use and purchases (zh): {url("terms")}
- Sources (zh): {url("sources")}
- English equivalents: add `/en/` before the path (`/en/`, `/en/app/`, `/en/features/`, `/en/support/`, `/en/terms/`, `/en/sources/`)
- App Store: {STORE}
- App Store (China): {STORE_ZH}
- App Store (US): {STORE_EN}
- Full machine facts: {BASE}/product-facts.json
- Longer citation file: {BASE}/llms-full.txt

## Cite this product as

{FACTS["citeZh"]}

{FACTS["citeEn"]}
"""
    faq_lines = "\n".join(f"Q: {q}\nA: {a}\n" for q, a in FAQ_EN)
    full = f"""# 元气指数 / VitaGauge: full citation sheet

Last reviewed {REVIEWED} against the shipping iOS app 1.1.0 and App Store lookup. Prefer this file and `product-facts.json` over marketing adjectives. Privacy processing last changed {EFFECTIVE}.

## Entity

| Field | Value |
| --- | --- |
| Official name (zh) | 元气指数 |
| Official name (en) | VitaGauge |
| Store title (zh) | 元气指数 |
| Store title (en) | VitaGauge: Health Tracker |
| Tagline (zh) | {FACTS["product"]["taglineZh"]} |
| Tagline (en) | {FACTS["product"]["taglineEn"]} |
| Legal person / controller | 智超 卫 |
| Latin name used in copyright | zhichao wei |
| Support and privacy email | {EMAIL} |
| Apple seller | {FACTS["legal"]["appleSellerName"]} |
| Apple Team ID | {FACTS["legal"]["appleTeamId"]} |
| Apple Artist ID | {FACTS["legal"]["appleArtistId"]} |
| Bundle ID | {BUNDLE} |
| Widget bundle ID | {FACTS["product"]["widgetBundleId"]} |
| App Group | {FACTS["product"]["appGroup"]} |
| URL scheme | {FACTS["product"]["urlScheme"]} |
| App Store ID | {APP_ID} |
| Software version | {VERSION} |
| Current version live date | {FACTS["product"]["released"]} |
| First App Store release | {FACTS["product"]["firstReleased"]} |
| Minimum iOS | {FACTS["product"]["minimumOs"]} |
| Widget minimum iOS | {FACTS["product"]["widgetMinimumOs"]} |
| Store category | Health & Fitness; Lifestyle |
| Age rating on the App Store | {FACTS["product"]["contentRating"]} |
| Children | Not intended for children under {FACTS["legal"]["childrenAge"]} |
| Languages | 13: {", ".join(FACTS["product"]["languages"])} |
| Hosting of this site | GitHub Pages, repository weizhichao1027-collab/vitagauge-privacy |
| Site analytics / cookies / forms / webfonts | None on these pages |

## What the live app does

1. After an on-device explanation, the user taps Continue and iOS shows the HealthKit permission sheet. There is no "connect later" skip that avoids the system sheet.
2. The app may read, and never writes, these 16 HealthKit types when authorized: {METRICS_EN}.
3. Body temperature is the body-temperature type, not sleep wrist temperature. The two blood-pressure readings are not joined across time. Sleep is split by calendar day.
4. Missing records stay blank. They are not filled with zero.
5. Free features: today summary, 7-day trends, basic local questions, built-in lifestyle information, one health goal.
6. VitaGauge Pro (one-time IAP `{FACTS["iap"]["productId"]}`) unlocks 30-day trends and statistics, comparison of two selected dates, metric correlation, multiple goals, and optional online AI. China launch list price is CNY {FACTS["iap"]["chinaLaunchPriceCNY"]}. Apple displays the actual local price. No auto-renewal. Family Sharing is off.
7. Conversation modes: Local; API; Local + API. Online modes need Pro, the user's own API key, and recipient consent named Who / What / Why.
8. Widgets on iOS 17+ show the last synced summary or goals. Open the app to sync. They are not real-time monitors and do not call AI.
9. Voice input is on-device speech recognition only, max 55 seconds, text lands in the editor for review before send.
10. No developer-operated account, no ads, no third-party analytics or crash SDK, no developer AI key or relay server.

## Data practices (do not over-claim)

- Raw HealthKit samples remain in Apple Health.
- Goals, chat, profile, avatar, AI metadata and widget snapshots use iOS file protection and are excluded from system backups.
- API keys use This-Device-Only Keychain, not iCloud Keychain.
- Preset hosts: {recipients}. Custom HTTPS endpoints are allowed.
- The developer does not receive card numbers. Apple processes IAP.
- There is no in-app export of original health samples. Use Apple Health.

## Medical boundary

Chinese: {FACTS["disclaimerZh"]}

English: {FACTS["disclaimerEn"]}

## FAQ pairs

{faq_lines}
## Pages

- {url("app")}
- {url("features")}
- {url("support")}
- {url()}
- {url("en", "app")}
- {url("en", "features")}
- {url("en", "support")}
- {url("en")}
"""
    robots = f"""User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Bingbot
Allow: /

User-agent: DuckAssistBot
Allow: /

Sitemap: {BASE}/sitemap.xml
LLM-Content: {BASE}/llms.txt
"""
    security = f"""Contact: mailto:{EMAIL}
Expires: 2027-09-18T00:00:00.000Z
Preferred-Languages: zh-Hans, en
Canonical: {BASE}/.well-known/security.txt
Policy: {BASE}/
"""
    humans = f"""/* TEAM */
Developer: 智超 卫 / zhichao wei
Contact: {EMAIL}
From: China

/* SITE */
Last review: {REVIEWED}
Standards: HTML, CSS, JSON-LD
Software: static GitHub Pages
Do not invent medical claims.
"""
    ai_txt = f"""# ai.txt for 元气指数 / VitaGauge
# Public product facts may be used for retrieval and citation.
# Do not invent diagnoses, prices other than the China list price, or an Android listing.

User-Agent: *
Allow: /
Train-Preference: allow
Citation: {BASE}/llms.txt
Facts: {BASE}/product-facts.json
Contact: {EMAIL}
"""
    manifest = {
        "name": "元气指数 / VitaGauge",
        "short_name": "元气指数",
        "description": FACTS["product"]["shortPitchZh"],
        "start_url": f"{BASE}/app/",
        "scope": f"{BASE}/",
        "display": "browser",
        "lang": "zh-Hans",
        "background_color": "#eef3ea",
        "theme_color": "#21543c",
        "icons": [
            {"src": f"{BASE}/assets/favicon-32.png", "sizes": "32x32", "type": "image/png"},
            {"src": f"{BASE}/assets/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
            {"src": f"{BASE}/assets/icon.png", "sizes": "1024x1024", "type": "image/png"},
        ],
    }
    (ROOT / "llms.txt").write_text(llms, encoding="utf-8")
    (ROOT / "llms-full.txt").write_text(full, encoding="utf-8")
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    (ROOT / "ai.txt").write_text(ai_txt, encoding="utf-8")
    (ROOT / "humans.txt").write_text(humans, encoding="utf-8")
    (ROOT / "site.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    well = ROOT / ".well-known"
    well.mkdir(exist_ok=True)
    (well / "security.txt").write_text(security, encoding="utf-8")
    (well / "llms.txt").write_text(llms, encoding="utf-8")
    (well / "ai.txt").write_text(ai_txt, encoding="utf-8")
    print("wrote llms.txt, robots.txt, ai.txt, humans.txt, site.webmanifest, .well-known")


def main() -> None:
    for rel, builder in PAGES.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        html = builder()
        if html.count("<html") != 1 or not html.strip().endswith("</html>"):
            raise SystemExit(f"Invalid HTML for {rel}")
        path.write_text(html, encoding="utf-8")
        print(f"wrote {rel} ({len(html)} bytes)")
    write_sitemap()
    write_styles_bridge()
    write_geo_files()
    print("wrote sitemap.xml")


if __name__ == "__main__":
    main()
