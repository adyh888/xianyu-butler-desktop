#!/usr/bin/env python3
"""第二轮截图（v2）：精确 DOM 美化，只动最内层空态框，逐张校验。"""

from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8643'
OUT = Path('/Users/liqian/Desktop/MyProject/xianyu-butler-desktop/marketing/taobao/素材')

HIDE_JS = """
() => {
  // 只隐藏"公告条本体"：从含关键词的叶子往上找 class 含 banner/notice/announce 的元素，
  // 找不到就隐藏该叶子的直接父级（通常就是条状容器），绝不隐藏大容器。
  const kw = ['版本 已发布', '提示：挂'];
  document.querySelectorAll('div,span').forEach(leaf => {
    if (leaf.children.length > 0) return;
    const t = leaf.textContent || '';
    if (!kw.some(k => t.includes(k))) return;
    let bar = leaf.closest('[class*="banner"],[class*="notice"],[class*="announce"],[class*="marquee"]');
    if (!bar) { bar = leaf.parentElement; }
    if (bar && bar.getBoundingClientRect().height < 80) bar.style.display = 'none';
  });
}
"""

STAGE_ACCOUNTS_JS = """
() => {
  document.querySelectorAll('div').forEach(el => {
    const t = (el.innerText || '');
    if (t.includes('登录态已过期') && t.length < 120) { el.style.display = 'none'; }
  });
  document.querySelectorAll('span,div').forEach(el => {
    if ((el.innerText || '').trim() === '需重新扫码' && el.children.length === 0) {
      el.textContent = '● 运行中';
      el.style.background = '#dcfce7';
      el.style.color = '#16a34a';
    }
  });
}
"""

STAGE_DASH_JS = """
() => {
  const setCardNum = (labelText, val) => {
    document.querySelectorAll('*').forEach(el => {
      if (el.children.length === 0 && (el.textContent||'').trim() === labelText) {
        // 向上找统计卡容器，替换其中第一个纯数字节点
        let card = el.closest('[class]');
        for (let up = 0; up < 6 && card; up++) {
          if ((card.innerText||'').includes(labelText)) { el = card; card = card.parentElement; continue; }
          break;
        }
      }
    });
  };
  const swapLeaf = (from, to) => {
    document.querySelectorAll('*').forEach(el => {
      if (el.children.length === 0 && (el.textContent || '').trim() === from) el.textContent = to;
    });
  };
  const money = ['¥12,860.50', '¥12,460.50', '¥400.00'];
  let mi = 0;
  document.querySelectorAll('*').forEach(el => {
    if (el.children.length === 0 && (el.textContent || '').trim() === '¥0.00' && mi < money.length) {
      el.textContent = money[mi++];
    }
  });
  // 订单总数 / 库存卡密：只替换紧跟在对应文字之前的数字兄弟节点
  const labelSwap = (label, val) => {
    document.querySelectorAll('*').forEach(el => {
      if (el.children.length === 0 || (el.textContent||'').trim() !== label) return;
      const box = el.parentElement;
      if (!box) return;
      for (const sib of box.querySelectorAll('*')) {
        if (sib.children.length === 0 && /^(0|[0-9]+)$/.test((sib.textContent||'').trim())) { sib.textContent = val; break; }
      }
    });
  };
  labelSwap('订单总数', '86');
  labelSwap('库存卡密余量', '528');
  swapLeaf('0%', '+18%');

  // 替换空态：从文字向上找带虚线边框的最内层元素，只替换一次
  const lineSvg = `<svg viewBox="0 0 600 170" style="width:100%;height:170px">
    <defs><linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fbbf24" stop-opacity="0.45"/><stop offset="100%" stop-color="#fbbf24" stop-opacity="0"/></linearGradient></defs>
    <path d="M0,140 C60,130 90,88 150,93 C210,98 240,55 300,64 C360,73 390,36 450,40 C510,44 560,22 600,15 L600,170 L0,170 Z" fill="url(#g1)"/>
    <path d="M0,140 C60,130 90,88 150,93 C210,105 240,55 300,64 C360,73 390,36 450,40 C510,44 560,22 600,15" fill="none" stroke="#f59e0b" stroke-width="3"/>
    <circle cx="450" cy="40" r="5" fill="#f59e0b"/></svg>`;
  const barSvg = (hi) => `<svg viewBox="0 0 600 170" style="width:100%;height:170px">
    ${[100,150,80,170,130,190,160].map((h,idx)=>`<rect x="${20+idx*80}" y="${160-h}" width="44" height="${h}" rx="8" fill="${idx===hi?'#f59e0b':'#fde68a'}"/>`).join('')}
  </svg>`;

  const findDashed = (text) => {
    let target = null;
    document.querySelectorAll('*').forEach(el => {
      if (el.children.length === 0) return;
      const own = [...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('');
      if ((own + ' ' + (el.innerText||'')).includes(text)) {
        let cur = el;
        let dashed = null;
        while (cur && cur !== document.body) {
          const b = getComputedStyle(cur).borderStyle || '';
          if ((b.includes('dashed') || b.includes('solid')) && (cur.innerText||'').includes(text)) { dashed = cur; break; }
          cur = cur.parentElement;
        }
        if (dashed) target = dashed;
      }
    });
    return target;
  };

  let box = findDashed('暂无订单数据');
  if (box) {
    box.innerHTML = `<div style="font:600 13px -apple-system,sans-serif;color:#64748b;padding:8px 4px 2px">近 7 日成交额走势</div>${lineSvg}`;
    box.style.border = 'none'; box.style.borderRadius = '12px'; box.style.background = '#fffbeb';
  }
  box = findDashed('暂无商品销售数据');
  if (box) { box.innerHTML = barSvg(5); box.style.border='none'; }
  box = findDashed('暂无订单状态数据');
  if (box) { box.innerHTML = barSvg(3); box.style.border='none'; }
}
"""

STAGE_CARDS_JS = """
() => {
  const nums = [...document.querySelectorAll('*')].filter(el => el.children.length === 0 && (el.textContent||'').trim() === '0');
  const vals = ['12', '9', '3,486'];
  nums.slice(0, 3).forEach((el, i) => { el.textContent = vals[i] || el.textContent; });
  document.querySelectorAll('*').forEach(el => {
    if (el.children.length === 0 && (el.textContent||'').trim() === '0 组已停用') el.textContent = '3 组已停用';
    const t = el.innerText || '';
    if (t.includes('暂无卡密配置')) el.closest('[class]') ? el.closest('[style*="dashed"],[class*="empty"],[class*="placeholder"]')?.remove() : null;
  });
  document.querySelectorAll('div').forEach(el => {
    const t = el.innerText || '';
    if (t.includes('暂无卡密配置') && t.length < 80) { el.style.display = 'none'; }
  });
}
"""


def sidebar_ok(page):
    return page.evaluate("() => { const a=[...document.querySelectorAll('*')].find(e=>(e.innerText||'').trim()==='账号管理'); return !!a && a.getBoundingClientRect().width>0; }")


def shot(page, name, clip=None, full=False):
    page.wait_for_timeout(800)
    page.screenshot(path=str(OUT / f'{name}.png'), clip=clip, full_page=full)
    print(f'✓ {name}  sidebar={sidebar_ok(page)}')


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=2, locale='zh-CN')
    page = ctx.new_page()
    page.goto(f'{BASE}/static/index.html', wait_until='networkidle')
    page.fill('input[type="text"], input:not([type="password"])', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("登 录"), button:has-text("登录")')
    page.wait_for_timeout(3500)

    # 1. 总览
    page.evaluate(HIDE_JS)
    page.evaluate(STAGE_DASH_JS)
    shot(page, 'shot-dashboard')

    # 2. 账号管理
    page.click('text="账号管理"')
    page.wait_for_timeout(2000)
    page.evaluate(HIDE_JS)
    page.evaluate(STAGE_ACCOUNTS_JS)
    shot(page, 'shot-accounts', full=True)

    # 3. 卡密库存（只截头部+统计卡区域）
    page.click('text="卡密库存"')
    page.wait_for_timeout(2000)
    page.evaluate(HIDE_JS)
    page.evaluate(STAGE_CARDS_JS)
    shot(page, 'shot-cards-top', clip={'x': 280, 'y': 0, 'width': 1160, 'height': 420})

    # 4. AI 回复
    page.click('text="AI 回复"')
    page.wait_for_timeout(2000)
    page.evaluate(HIDE_JS)
    shot(page, 'shot-ai')

    # 5. 自动回复
    page.click('text="自动回复"')
    page.wait_for_timeout(2000)
    page.evaluate(HIDE_JS)
    shot(page, 'shot-reply')

    # 6. 商品自动化
    page.click('text="商品自动化"')
    page.wait_for_timeout(2000)
    page.evaluate(HIDE_JS)
    shot(page, 'shot-automation')

    browser.close()
    print('done')
