#!/usr/bin/env python3
"""启动真实应用界面，逐页截图用于电商素材。"""

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8643'
OUT = Path('/Users/liqian/Desktop/MyProject/xianyu-butler-desktop/marketing/taobao/素材')
OUT.mkdir(parents=True, exist_ok=True)

SHOTS = []  # (文件名, 描述)


def shot(page, name, desc, full=False):
    page.wait_for_timeout(1200)
    page.screenshot(path=str(OUT / f'{name}.png'), full_page=full)
    SHOTS.append((name, desc))
    print(f'✓ {name}: {desc}')


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=2, locale='zh-CN')
    page = ctx.new_page()

    # 1. 登录页
    page.goto(f'{BASE}/static/index.html', wait_until='networkidle')
    shot(page, 'ui-login', '登录页')

    # 2. 登录
    page.fill('input[type="text"], input:not([type="password"])', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("登 录"), button:has-text("登录")')
    page.wait_for_timeout(3000)
    shot(page, 'ui-home', '登录后首页', full=True)

    # 3. 遍历侧边栏导航，逐页截图
    links = page.eval_on_selector_all(
        'a, [class*="nav"] [class*="item"], aside *',
        """els => els
            .map(e => ({text: (e.innerText||'').trim(), tag: e.tagName}))
            .filter(x => x.text && x.text.length <= 8 && !x.text.includes('\\n'))"""
    )
    seen = set()
    for item in links:
        text = item['text']
        if text in seen or not text:
            continue
        seen.add(text)
        try:
            el = page.locator(f'text="{text}"').first
            if el.count() == 0:
                continue
            el.click(timeout=2000)
            page.wait_for_timeout(1500)
            name = 'ui-page-' + str(len(SHOTS))
            shot(page, name, f'页面[{text}]', full=True)
        except Exception as e:
            print(f'  跳过[{text}]: {type(e).__name__}')

    browser.close()

print('\n== 截图清单 ==')
for n, d in SHOTS:
    print(f'{n}.png  {d}')
