#!/usr/bin/env python3
"""Compose 1200x630 Open Graph cards from the v39 向阳 icon. No external fonts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
FACTS = json.loads((ROOT / "product-facts.json").read_text())
W, H = 1200, 630
BG = (228, 238, 227)
INK = (23, 54, 44)
MUTED = (61, 92, 78)
SUN = (224, 122, 20)
FOREST = (33, 84, 60)
PAPER = (247, 250, 244)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    index = 1 if bold else 0
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size, index=index)
        except OSError:
            try:
                return ImageFont.truetype(path, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def rounded_icon(size: int = 168) -> Image.Image:
    src = Image.open(ASSETS / "icon.png").convert("RGBA")
    src = src.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=36, fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(src, (0, 0), mask)
    return out


def card(kicker: str, title: str, line: str, filename: str) -> None:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 18, H), fill=FOREST)
    draw.ellipse((980, -120, 1320, 220), fill=(214, 228, 208))
    draw.ellipse((1040, 430, 1280, 720), fill=(214, 226, 196))
    draw.rectangle((0, H - 14, W, H), fill=SUN)

    icon = rounded_icon()
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle((86, 178, 86 + 176, 178 + 176), radius=40, fill=(36, 75, 46, 40))
    img.paste(shadow.filter(ImageFilter.GaussianBlur(10)), (0, 0), shadow)

    canvas = img.convert("RGBA")
    canvas.alpha_composite(icon, (92, 184))
    img = canvas.convert("RGB")
    draw = ImageDraw.Draw(img)

    draw.text((92, 84), kicker, font=font(28), fill=MUTED)
    draw.multiline_text((300, 176), title, font=font(58, bold=True), fill=INK, spacing=10)
    draw.multiline_text((300, 360), line, font=font(30), fill=MUTED, spacing=8)
    draw.text((92, 548), f"App Store {FACTS['product']['version']}  weizhichao1027-collab.github.io", font=font(22), fill=FOREST)
    dest = ASSETS / filename
    img.save(dest, "PNG", optimize=True)
    print(f"wrote {dest} {dest.stat().st_size}")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    card(
        "元气指数  /  VitaGauge",
        "把每天的健康\n看得更明白",
        "Apple 健康摘要、16 项趋势与本地问答\n1.2.0 已上架，支持 iPad 与配对 Apple Watch",
        "og-default.png",
    )
    card(
        "功能与价格  /  Features",
        "免费开始\nPro 一次买断",
        "7 天趋势与 1 个目标免费\n价格与地区可用性，以 Apple 购买页为准",
        "og-features.png",
    )
    card(
        "支持中心  /  Support",
        "入门、权限\n恢复购买与删除",
        "weizhichao1027@gmail.com\n请勿发送 API Key 或不必要的健康资料",
        "og-support.png",
    )
    card(
        "隐私政策  /  Privacy",
        "先在本机处理\n发送由你决定",
        "HealthKit 只读，无账户，无分析 SDK\n生效 2026-09-16，本页复核 2026-10-31",
        "og-privacy.png",
    )

    # Lossless web assets keep production UI pixels intact while reducing transfer size.
    for language in ("zh-Hans", "en"):
        for name in ("summary", "assistant", "trend", "sleep", "goal", "local", "widget", "ipad", "watch"):
            path = ASSETS / f"{language}-{name}.png"
            with Image.open(path) as source:
                source.save(path.with_suffix(".webp"), "WEBP", lossless=True, method=6)
    records = []
    for path in sorted(p for p in ASSETS.iterdir() if p.suffix in {".png", ".webp"}):
        with Image.open(path) as source:
            size = list(source.size)
        records.append({"file": path.name, "size": size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (ASSETS / "manifest.json").write_text(json.dumps({
        "version": FACTS["product"]["version"], "reviewed": FACTS["reviewed"],
        "data": "synthetic production UI captures and brand artwork; no personal health records",
        "assets": records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
