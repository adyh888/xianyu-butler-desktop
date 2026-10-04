#!/usr/bin/env python3
"""生成桌面版应用图标：desktop/build/icon.{png,icns,ico}。

纯 PIL 绘制：蓝青渐变圆角底 + 白色小鱼 + 气泡。先按 4 倍尺寸绘制再缩小，
保证边缘平滑。macOS 下顺带用 iconutil 产出 icns。
"""

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / 'desktop' / 'build'
S = 2048  # 绘制尺寸（4x of 512）

BG_TOP = (34, 211, 238)     # #22d3ee cyan
BG_BOTTOM = (37, 99, 235)   # #2563eb blue
WHITE = (255, 255, 255, 255)
EYE = (30, 64, 175, 255)    # 深蓝眼睛
BUBBLE = (165, 243, 252, 230)


def rounded_gradient_base() -> Image.Image:
    # 垂直渐变（上浅下深）：linear_gradient 天然铺满整张图，不会有旋转产生的角落露底
    grad = Image.linear_gradient('L').transpose(Image.FLIP_TOP_BOTTOM).resize((S, S), Image.LANCZOS)
    base = ImageOps.colorize(grad, black=BG_BOTTOM[:3], white=BG_TOP[:3]).convert('RGBA')

    mask = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.225), fill=255)

    icon = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    icon.paste(base, (0, 0), mask)
    return icon


def draw_fish(icon: Image.Image) -> Image.Image:
    layer = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 身体：椭圆
    d.ellipse([300, 780, 1440, 1330], fill=WHITE)
    # 尾巴：燕尾三角
    d.polygon([(1360, 1055), (1740, 780), (1660, 1055), (1740, 1330)], fill=WHITE)
    # 背鳍
    d.polygon([(660, 800), (980, 620), (1160, 810)], fill=WHITE)
    # 眼睛
    d.ellipse([470, 940, 590, 1060], fill=EYE)
    # 气泡
    d.ellipse([1580, 520, 1690, 630], fill=BUBBLE)
    d.ellipse([1730, 380, 1800, 450], fill=BUBBLE)

    icon.alpha_composite(layer)
    return icon


def save_outputs(icon512: Image.Image) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    png_path = OUT_DIR / 'icon.png'
    icon512.save(png_path)

    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon512.resize((256, 256), Image.LANCZOS).save(OUT_DIR / 'icon.ico', sizes=ico_sizes)

    if sys.platform == 'darwin':
        iconset = OUT_DIR / 'icon.iconset'
        iconset.mkdir(exist_ok=True)
        for size in (16, 32, 64, 128, 256, 512, 1024):
            img = icon512.resize((size, size), Image.LANCZOS)
            img.save(iconset / f'icon_{size}x{size}.png')
            if size <= 512:
                img2 = icon512.resize((size * 2, size * 2), Image.LANCZOS)
                img2.save(iconset / f'icon_{size}x{size}@2x.png')
        subprocess.run(
            ['iconutil', '-c', 'icns', str(iconset), '-o', str(OUT_DIR / 'icon.icns')],
            check=True,
        )
        subprocess.run(['rm', '-rf', str(iconset)], check=True)

    print(f'图标已生成: {OUT_DIR}')


if __name__ == '__main__':
    icon = rounded_gradient_base()
    icon = draw_fish(icon)
    icon512 = icon.resize((512, 512), Image.LANCZOS)
    save_outputs(icon512)
