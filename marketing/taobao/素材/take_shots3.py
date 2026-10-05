#!/usr/bin/env python3
"""第三轮截图：修正公告条隐藏、红框隐藏、统计数字、图表注入。"""

from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8643'
OUT = Path('/Users/liqian/Desktop/MyProject/xianyu-butler-desktop/marketing/taobao/素材')

COMMON_JS = r"""
() => {
  // 从含关键词的元素向上找"全宽横条"并隐藏
  window.__hideStrip = (kwList) => {
    document.querySelectorAll('span,div').forEach(el => {
      const t = (el.textContent || '');
      if (!kwList.some(k => t.includes(k))) return;
      let cur = el;
      for (let i = 0; i < 6 && cur; i++) {
        const r = cur.getBoundingClientRect();
        if (r.width > window.innerWidth * 0.6 && r.height > 20 && r.height < 100) {
          cur.style.display = 'none';
          return;
        }
        cur = cur.parentElement;
      }
    });
  };
  window.__hideStrip(['版本 已发布']);
  window.__hideStrip(['提示：挂']);
  window.__hideStrip(['人工验证']);
}
"""

STAGE_ACCOUNTS_JS = r"""
() => {
  // 红色错误提示框：从文字向上找"浅红背景、高度小"的盒子隐藏，无兜底
  document.querySelectorAll('div').forEach(el => {
    if ((el.innerText || '').indexOf('登录态已过期') === -1) return;
    if (el.children.length > 2) return;   // 从最内层开始
    let cur = el;
    for (let i = 0; i < 7 && cur && cur !== document.body; i++) {
      const r = cur.getBoundingClientRect();
      const bg = getComputedStyle(cur).backgroundColor || '';
      const m = bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      const reddish = m && +m[1] > 245 && +m[2] > 195 && +m[3] > 195;
      if (reddish && r.height < 110) { cur.style.display = 'none'; return; }
      cur = cur.parentElement;
    }
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

STAGE_DASH_JS = r"""
() => {
  const labelNum = (label, val) => {
    const labelEl = [...document.querySelectorAll('*')].find(e =>
      e.children.length === 0 && (e.textContent || '').trim() === label);
    if (!labelEl) return;
    let cur = labelEl.parentElement;
    while (cur && cur !== document.body) {
      const nums = [...cur.querySelectorAll('*')].filter(e =>
        e.children.length === 0 && /^\d+$/.test((e.textContent || '').trim()) && e !== labelEl);
      if (nums.length) { nums[0].textContent = val; return; }
      cur = cur.parentElement;
    }
  };
  let mi = 0;
  const money = ['¥12,860.50', '¥12,460.50', '¥400.00'];
  document.querySelectorAll('*').forEach(el => {
    if (el.children.length === 0 && (el.textContent || '').trim() === '¥0.00' && mi < money.length) {
      el.textContent = money[mi++];
    }
  });
  labelNum('订单总数', '86');
  labelNum('库存卡密余量', '528');
  // 涨幅徽标（只替换第一个文本节点，避免重复）
  document.querySelectorAll('span,div').forEach(el => {
    if ((el.innerText || '').trim() === '0%' && el.querySelectorAll('svg').length <= 1) {
      let done = false;
      el.childNodes.forEach(n => {
        if (n.nodeType === 3) {
          if (!done) { n.textContent = '+18%'; done = true; }
          else { n.textContent = ''; }
        }
      });
    }
  });

  // 最小面积的虚线空态框替换为示例图表
  const findSmallestDashed = (text) => {
    let best = null, bestArea = Infinity;
    document.querySelectorAll('div').forEach(el => {
      const bs = getComputedStyle(el).borderTopStyle + getComputedStyle(el).borderLeftStyle;
      if (!bs.includes('dashed')) return;
      if (!(el.innerText || '').includes(text)) return;
      const r = el.getBoundingClientRect();
      const area = r.width * r.height;
      if (area < bestArea) { bestArea = area; best = el; }
    });
    return best;
  };
  const lineSvg = `<svg viewBox="0 0 600 170" style="width:100%;height:170px;display:block">
    <defs><linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fbbf24" stop-opacity="0.45"/><stop offset="100%" stop-color="#fbbf24" stop-opacity="0"/></linearGradient></defs>
    <path d="M0,140 C60,130 90,88 150,93 C210,98 240,55 300,64 C360,73 390,36 450,40 C510,44 560,22 600,15 L600,170 L0,170 Z" fill="url(#g1)"/>
    <path d="M0,140 C60,130 90,88 150,93 C210,105 240,55 300,64 C360,73 390,36 450,40 C510,44 560,22 600,15" fill="none" stroke="#f59e0b" stroke-width="3"/>
    <circle cx="450" cy="40" r="5" fill="#f59e0b"/></svg>`;
  const barSvg = (hi) => `<svg viewBox="0 0 600 170" style="width:100%;height:170px;display:block">
    ${[100,150,80,170,130,190,160].map((h,idx)=>`<rect x="${20+idx*80}" y="${160-h}" width="44" height="${h}" rx="8" fill="${idx===hi?'#f59e0b':'#fde68a'}"/>`).join('')}
  </svg>`;
  let box = findSmallestDashed('暂无订单数据');
  if (box) {
    box.innerHTML = `<div style="font:600 13px -apple-system,sans-serif;color:#64748b;padding:8px 4px 2px">近 7 日成交额走势</div>${lineSvg}`;
    box.style.border = 'none'; box.style.borderRadius = '12px'; box.style.background = '#fffbeb';
  }
  box = findSmallestDashed('暂无商品销售数据');
  if (box) { box.innerHTML = barSvg(5); box.style.border = 'none'; }
  box = findSmallestDashed('暂无订单状态数据');
  if (box) { box.innerHTML = barSvg(3); box.style.border = 'none'; }
}
"""

STAGE_CARDS_JS = r"""
() => {
  const nums = [...document.querySelectorAll('*')].filter(el => el.children.length === 0 && (el.textContent || '').trim() === '0');
  const vals = ['12', '9', '3,486'];
  nums.slice(0, 3).forEach((el, i) => { el.textContent = vals[i] || el.textContent; });
  document.querySelectorAll('*').forEach(el => {
    if (el.children.length === 0 && (el.textContent || '').trim() === '0 组已停用') el.textContent = '3 组已停用';
  });
  document.querySelectorAll('div').forEach(el => {
    const t = el.innerText || '';
    if (t.includes('暂无卡密配置') && t.length < 80) el.style.display = 'none';
  });
}
"""


def shot(page, name, clip=None, full=False):
    page.wait_for_timeout(700)
    page.screenshot(path=str(OUT / f'{name}.png'), clip=clip, full_page=full)
    print(f'✓ {name}')


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=2, locale='zh-CN')
    page = ctx.new_page()
    page.goto(f'{BASE}/static/index.html', wait_until='networkidle')
    page.fill('input[type="text"], input:not([type="password"])', 'admin')
    page.fill('input[type="password"]', 'admin123')
    page.click('button:has-text("登 录"), button:has-text("登录")')
    page.wait_for_timeout(3500)

    page.evaluate(COMMON_JS)
    page.evaluate(STAGE_DASH_JS)
    shot(page, 'shot-dashboard')

    page.click('text="账号管理"')
    page.wait_for_timeout(2000)
    page.evaluate(COMMON_JS)
    page.evaluate(STAGE_ACCOUNTS_JS)
    shot(page, 'shot-accounts')

    page.click('text="卡密库存"')
    page.wait_for_timeout(2000)
    page.evaluate(COMMON_JS)
    page.evaluate(STAGE_CARDS_JS)
    shot(page, 'shot-cards-top', clip={'x': 280, 'y': 0, 'width': 1160, 'height': 420})

    page.click('text="AI 回复"')
    page.wait_for_timeout(2000)
    page.evaluate(COMMON_JS)
    shot(page, 'shot-ai')

    page.click('text="自动回复"')
    page.wait_for_timeout(2000)
    page.evaluate(COMMON_JS)
    shot(page, 'shot-reply')

    page.click('text="商品自动化"')
    page.wait_for_timeout(2000)
    page.evaluate(COMMON_JS)
    shot(page, 'shot-automation')

    browser.close()
    print('done')
