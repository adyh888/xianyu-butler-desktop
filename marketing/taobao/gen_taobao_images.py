#!/usr/bin/env python3
"""闲鱼管家淘宝商品图生成器：主图 5 张（800×800）+ 详情图 9 张（790 宽）。

HTML/CSS 排版 → headless Chromium 截图导出 PNG（2 倍清晰度）。
"""

import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path('/Users/liqian/Desktop/MyProject/xianyu-butler-desktop')
MAT = ROOT / 'marketing' / 'taobao' / '素材'
OUT_MAIN = ROOT / 'marketing' / 'taobao' / '主图'
OUT_DETAIL = ROOT / 'marketing' / 'taobao' / '详情图'
ICON = ROOT / 'desktop' / 'build' / 'icon.png'

IMG = {
    'icon': ICON.as_uri(),
    'login': (MAT / 'ui-login.png').as_uri(),
    'dash': (MAT / 'shot-dashboard.png').as_uri(),
    'accounts': (MAT / 'shot-accounts.png').as_uri(),
    'ai': (MAT / 'shot-ai.png').as_uri(),
    'ai_full': (MAT / 'ui-page-16.png').as_uri(),
    'automation': (MAT / 'shot-automation.png').as_uri(),
}

BASE_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:"PingFang SC","Microsoft YaHei","Hiragino Sans GB",sans-serif;
       color:#171a1f; -webkit-font-smoothing:antialiased; }
.cv { position:relative; overflow:hidden; background:#faf8f2; }
.pill { display:inline-flex; align-items:center; gap:6px; padding:7px 16px; border-radius:999px;
        font-size:15px; font-weight:600; }
.browser { background:#fff; border-radius:14px; box-shadow:0 24px 60px rgba(23,26,31,.18);
           overflow:hidden; }
.browser .bar { height:34px; background:#f1f0ec; display:flex; align-items:center; gap:6px; padding:0 14px; }
.browser .bar i { width:10px; height:10px; border-radius:50%; display:inline-block; }
.browser .bar .u { margin-left:10px; flex:1; height:18px; border-radius:9px; background:#fff;
                   font-size:10px; color:#9aa1ac; display:flex; align-items:center; padding:0 10px; }
.browser .img { line-height:0; }
.browser .img img { width:100%; display:block; }
.shot { width:100%; display:block; }
.demo-note { position:absolute; font-size:10px; color:#b4a98f; letter-spacing:1px; }
"""


def chip(text, bg='#171a1f', fg='#fff'):
    return f'<span class="pill" style="background:{bg};color:{fg}">{text}</span>'


# ============================================================ 主图 1：全家福
MAIN1 = f"""
<div class="cv" style="width:800px;height:800px;
     background:radial-gradient(700px 420px at 50% -8%, #fff7c2 0%, rgba(255,247,194,0) 62%), #faf8f2;">
  <div style="position:absolute;top:34px;left:40px;display:flex;align-items:center;gap:12px;">
    <img src="{IMG['icon']}" style="width:44px;height:44px;border-radius:10px;">
    <div style="font-size:22px;font-weight:800;">闲鱼管家</div>
  </div>
  <div style="position:absolute;top:42px;right:40px;">
    {chip('官方开源 · 本地部署', '#fff', '#171a1f')}
  </div>

  <div style="position:absolute;top:118px;left:0;right:0;text-align:center;">
    <div style="display:inline-block;background:#171a1f;color:#ffe600;font-size:16px;font-weight:700;
                padding:7px 20px;border-radius:999px;letter-spacing:2px;">多账号 · 全自动 · 不漏单</div>
    <div style="font-size:84px;font-weight:900;letter-spacing:4px;margin-top:18px;line-height:1.12;">
      闲鱼运营<br>自动管家
    </div>
    <div style="font-size:20px;color:#5b6472;margin-top:14px;letter-spacing:1px;">
      自动回复 · 自动发货 · 智能议价 · 数据看板
    </div>
  </div>

  <div style="position:absolute;top:404px;left:50%;transform:translateX(-50%) rotate(-2.5deg);width:640px;">
    <div class="browser">
      <div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i>
        <div class="u">闲鱼管家 · 运营工作台（界面演示数据）</div></div>
      <div class="img"><img src="{IMG['dash']}" style="margin-top:-8px;"></div>
    </div>
  </div>
  <div style="position:absolute;bottom:44px;left:0;right:0;display:flex;justify-content:center;gap:16px;">
    {chip('🖥️ 桌面版 · 双击即用', '#2f7bff')}
    {chip('☁️ 服务器版 · 24小时挂机', '#12b76a')}
  </div>
</div>
"""

# ============================================================ 主图 2：桌面版
MAIN2 = f"""
<div class="cv" style="width:800px;height:800px;
     background:linear-gradient(160deg,#eaf2ff 0%, #faf8f2 55%);">
  <div style="position:absolute;top:56px;left:52px;">
    {chip('版本一 · 桌面版', '#2f7bff')}
    <div style="font-size:66px;font-weight:900;margin-top:20px;letter-spacing:2px;line-height:1.15;">
      双击安装<br>开箱即用
    </div>
    <div style="font-size:19px;color:#5b6472;margin-top:16px;line-height:1.75;">
      不用装 Python / Node / Docker，<br>浏览器内核已内置，装完就能扫码上号。
    </div>
    <div style="display:flex;gap:10px;margin-top:22px;">
      <span class="pill" style="background:#171a1f;color:#fff;">⭐ Windows 10/11</span>
      <span class="pill" style="background:#171a1f;color:#fff;">⭐ macOS 11+</span>
    </div>
  </div>

  <div style="position:absolute;top:64px;right:44px;width:330px;">
    <div class="browser" style="transform:rotate(2.5deg);">
      <div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i>
        <div class="u">闲鱼管家</div></div>
      <div class="img"><img src="{IMG['login']}"></div>
    </div>
  </div>

  <div style="position:absolute;top:436px;left:52px;right:52px;display:flex;gap:14px;">
    __STEPS__
  </div>

  <style>
  .step {{ flex:1; background:#fff; border-radius:14px; padding:16px 12px; text-align:center;
          box-shadow:0 10px 26px rgba(23,26,31,.08); }}
  .step b {{ font-size:26px; }}
  .step div {{ font-size:16px; font-weight:700; margin-top:6px; }}
  </style>

  <div style="position:absolute;top:560px;left:52px;right:52px;
              background:linear-gradient(135deg,#171a1f,#2c3540);border-radius:18px;padding:26px 30px;color:#fff;">
    <div style="font-size:20px;font-weight:800;color:#ffe600;">为什么选桌面版？</div>
    <div style="display:flex;gap:18px;margin-top:14px;font-size:15.5px;line-height:1.7;color:#e7ebf0;">
      <div>✅ 内置 Chromium 内核<br>滑块验证离线可用</div>
      <div>✅ 数据全部存本机<br>账号更安心</div>
      <div>✅ 装完即用<br>不挑电脑配置</div>
    </div>
  </div>
  <div class="demo-note" style="right:20px;bottom:12px;">界面为演示数据</div>
</div>
"""

# ============================================================ 主图 3：核心功能
MAIN3 = f"""
<div class="cv" style="width:800px;height:800px;
     background:radial-gradient(640px 400px at 50% -10%, #fff3b0 0%, rgba(255,243,176,0) 60%), #faf8f2;">
  <div style="position:absolute;top:64px;left:0;right:0;text-align:center;">
    <div style="font-size:54px;font-weight:900;letter-spacing:3px;">四大核心功能</div>
    <div style="font-size:19px;color:#5b6472;margin-top:12px;">从买家进店到成交发货，全流程自动接管</div>
  </div>

  <div style="position:absolute;top:212px;left:56px;right:56px;display:grid;grid-template-columns:1fr 1fr;gap:20px;">
    <div class="feat" style="background:#fff;border-radius:20px;padding:28px 26px;box-shadow:0 12px 30px rgba(23,26,31,.08);">
      <div style="font-size:44px;">💬</div>
      <div style="font-size:24px;font-weight:800;margin-top:10px;">关键词自动回复</div>
      <div style="font-size:15px;color:#5b6472;margin-top:8px;line-height:1.7;">咨询秒回不漏单，话术按账号/商品自由配置</div>
    </div>
    <div class="feat" style="background:#fff;border-radius:20px;padding:28px 26px;box-shadow:0 12px 30px rgba(23,26,31,.08);">
      <div style="font-size:44px;">🤖</div>
      <div style="font-size:24px;font-weight:800;margin-top:10px;">AI 智能议价</div>
      <div style="font-size:15px;color:#5b6472;margin-top:8px;line-height:1.7;">接入大模型自动谈价，最低价、议价轮数自己定</div>
    </div>
    <div class="feat" style="background:#fff;border-radius:20px;padding:28px 26px;box-shadow:0 12px 30px rgba(23,26,31,.08);">
      <div style="font-size:44px;">📦</div>
      <div style="font-size:24px;font-weight:800;margin-top:10px;">卡密自动发货</div>
      <div style="font-size:15px;color:#5b6472;margin-top:8px;line-height:1.7;">付款秒发货：文字、卡密、图片、API 数据源都行</div>
    </div>
    <div class="feat" style="background:#fff;border-radius:20px;padding:28px 26px;box-shadow:0 12px 30px rgba(23,26,31,.08);">
      <div style="font-size:44px;">📊</div>
      <div style="font-size:24px;font-weight:800;margin-top:10px;">经营数据看板</div>
      <div style="font-size:15px;color:#5b6472;margin-top:8px;line-height:1.7;">成交、退款、库存、商品排行一屏掌握</div>
    </div>
  </div>

  <div style="position:absolute;bottom:56px;left:0;right:0;text-align:center;">
    {chip('还有：自动评价 · 求小红花 · 定时擦亮 · 订单同步 · 风险拦截', '#ffe600', '#171a1f')}
  </div>
</div>
"""

# ============================================================ 主图 4：服务器版
MAIN4 = f"""
<div class="cv" style="width:800px;height:800px;background:#101418;">
  <div style="position:absolute;top:56px;left:56px;">
    {chip('版本二 · 服务器版', 'rgba(18,183,106,.16)', '#4ade80')}
    <div style="font-size:60px;font-weight:900;color:#fff;margin-top:20px;letter-spacing:2px;line-height:1.2;">
      Docker 部署<br>24 小时挂机
    </div>
    <div style="font-size:19px;color:#8b94a3;margin-top:16px;line-height:1.75;">
      部署在自己的云服务器 / NAS 上，<br>电脑关机也不掉线，异地随时打开网页管理。
    </div>
  </div>

  <div style="position:absolute;top:388px;left:56px;right:56px;background:#1b2129;border-radius:16px;
              box-shadow:0 20px 50px rgba(0,0,0,.5);overflow:hidden;">
    <div style="height:36px;background:#232b35;display:flex;align-items:center;gap:7px;padding:0 14px;">
      <i style="width:10px;height:10px;border-radius:50%;background:#ff5f57;display:inline-block;"></i>
      <i style="width:10px;height:10px;border-radius:50%;background:#febc2e;display:inline-block;"></i>
      <i style="width:10px;height:10px;border-radius:50%;background:#28c840;display:inline-block;"></i>
      <span style="color:#6b7686;font-size:12px;margin-left:8px;">terminal — ssh root@your-server</span>
    </div>
    <div style="padding:22px 26px;font-family:Menlo,monospace;font-size:15.5px;line-height:2;color:#c9d4e0;">
      <div><span style="color:#4ade80">$</span> docker run -d -p 8080:8080 \</div>
      <div>&nbsp;&nbsp;&nbsp;-v ./data:/app/data xianyu-butler:latest</div>
      <div style="color:#8b94a3;">[+] Running 3/3 ✔ 容器已启动</div>
      <div><span style="color:#4ade80">$</span> <span style="color:#ffe600;">✔ 闲鱼管家已上线: http://服务器IP:8080</span></div>
    </div>
  </div>

  <style>
  .sc {{ flex:1; background:#1b2129; border:1px solid #2a3340; border-radius:14px; padding:16px 14px;
        color:#e7ebf0; font-size:15px; font-weight:700; display:flex; flex-direction:column; gap:6px; align-items:center; }}
  .sc span {{ color:#8b94a3; font-size:12.5px; font-weight:500; }}
  </style>
  <div style="position:absolute;top:660px;left:56px;right:56px;display:flex;gap:14px;">
    <div class="sc">🖥️<span>群晖 / 极空间 NAS</span></div>
    <div class="sc">☁️<span>云服务器 VPS</span></div>
    <div class="sc">🏠<span>闲置电脑 / 软路由</span></div>
    <div class="sc">👥<span>多用户权限管理</span></div>
  </div>
  <div style="position:absolute;bottom:30px;left:0;right:0;text-align:center;color:#6b7686;font-size:14px;">
    断电关机不影响运行 · 网页远程访问 · 数据仍 100% 归你自己
  </div>
</div>
"""

# ============================================================ 主图 5：怎么选
MAIN5 = f"""
<div class="cv" style="width:800px;height:800px;
     background:radial-gradient(620px 380px at 50% -10%, #eaf2ff 0%, rgba(234,242,255,0) 60%), #faf8f2;">
  <div style="position:absolute;top:58px;left:0;right:0;text-align:center;">
    <div style="font-size:52px;font-weight:900;letter-spacing:3px;">两种版本，按需选择</div>
    <div style="font-size:19px;color:#5b6472;margin-top:12px;">功能完全一致，数据都保存在你自己手里，随时可以迁移</div>
  </div>

  <div style="position:absolute;top:200px;left:52px;right:52px;display:flex;gap:20px;">
    <div style="flex:1;background:#fff;border:3px solid #2f7bff;border-radius:22px;padding:30px 28px;
                box-shadow:0 16px 40px rgba(47,123,255,.14);">
      <div style="font-size:34px;">🖥️</div>
      <div style="font-size:30px;font-weight:900;margin-top:8px;">桌面版</div>
      <div style="color:#2f7bff;font-weight:800;font-size:16px;margin-top:2px;">装在自己电脑上</div>
      <div style="margin-top:18px;font-size:15.5px;line-height:2.1;color:#3c4654;">
        ✅ 小白友好，双击安装<br>
        ✅ Windows / macOS 都支持<br>
        ✅ 适合个人卖家 · 1~5 个号<br>
        ✅ 电脑开机时自动运营
      </div>
    </div>
    <div style="flex:1;background:#fff;border:3px solid #12b76a;border-radius:22px;padding:30px 28px;
                box-shadow:0 16px 40px rgba(18,183,106,.14);">
      <div style="font-size:34px;">☁️</div>
      <div style="font-size:30px;font-weight:900;margin-top:8px;">服务器版</div>
      <div style="color:#12b76a;font-weight:800;font-size:16px;margin-top:2px;">部署在服务器 / NAS</div>
      <div style="margin-top:18px;font-size:15.5px;line-height:2.1;color:#3c4654;">
        ✅ 24 小时在线不掉线<br>
        ✅ 手机浏览器也能远程管理<br>
        ✅ 适合工作室 · 多号集中管<br>
        ✅ 需要一台服务器或 NAS
      </div>
    </div>
  </div>

  <div style="position:absolute;top:648px;left:52px;right:52px;background:#171a1f;border-radius:18px;
              padding:22px 28px;color:#fff;display:flex;align-items:center;justify-content:space-between;">
    <div style="font-size:18px;font-weight:800;">不知道怎么选？</div>
    <div style="font-size:15.5px;color:#c9d4e0;">个人自用选桌面版 · 多店多号选服务器版 · 功能随时可升级迁移</div>
  </div>
  <div style="position:absolute;bottom:28px;left:0;right:0;text-align:center;font-size:14px;color:#9aa1ac;">
    均基于开源项目 xianyu-super-butler · AGPL-3.0 · 仅供学习研究
  </div>
</div>
"""

MAIN2 = MAIN2.replace('__STEPS__', """
<div class="step"><b>1️⃣</b><div>下载安装包</div></div>
<div class="step"><b>2️⃣</b><div>双击安装</div></div>
<div class="step"><b>3️⃣</b><div>打开扫码上号</div></div>
""")

# ============================================================ 详情公共
def detail(title_html, body_html, bg='#faf8f2', height=None):
    # 普通字符串里的 {{ }} 是给 f-string 准备的转义，这里统一还原成单个花括号
    def unescape(s):
        return s.replace('{{', '{').replace('}}', '}')
    h = f'height:{height}px;' if height else 'min-height:600px;'
    return (f'<div class="cv" style="width:790px;{h}background:{bg};">'
            f'{unescape(title_html)}{unescape(body_html)}</div>')


D1 = f"""
<div class="cv" style="width:790px;height:470px;
     background:radial-gradient(680px 400px at 50% -12%, #fff3b0 0%, rgba(255,243,176,0) 62%), #faf8f2;">
  <div style="position:absolute;top:66px;left:0;right:0;text-align:center;">
    <img src="{IMG['icon']}" style="width:92px;height:92px;border-radius:22px;box-shadow:0 14px 34px rgba(23,26,31,.16);">
    <div style="font-size:52px;font-weight:900;letter-spacing:4px;margin-top:20px;">闲鱼超级管家</div>
    <div style="font-size:21px;color:#5b6472;margin-top:12px;">多账号自动回复 · 自动发货 · AI 智能议价 · 经营看板</div>
    <div style="margin-top:24px;display:flex;justify-content:center;gap:14px;">
      {chip('🖥️ 桌面版', '#2f7bff')} {chip('☁️ 服务器版', '#12b76a')}
      <span class="pill" style="background:#171a1f;color:#fff;">两种版本任选</span>
    </div>
  </div>
  <div style="position:absolute;bottom:0;left:0;right:0;height:8px;
              background:linear-gradient(90deg,#ffe600,#2f7bff,#12b76a);"></div>
</div>
"""

D2 = detail("""
  <div style="padding:64px 44px 0;">
    <div style="font-size:42px;font-weight:900;letter-spacing:2px;">开闲鱼，这些事最耗人</div>
    <div style="font-size:17px;color:#5b6472;margin-top:10px;">每一个深夜咨询、每一次忘记发货，都是流失的订单</div>
  </div>
""", """
  <div style="padding:34px 44px 60px;display:grid;grid-template-columns:1fr 1fr;gap:18px;">
    <div class="pain"><div class="pi">💬</div><b>消息回不过来</b><p>同时接待几十个买家，回复慢了客户就去找别家</p></div>
    <div class="pain"><div class="pi">🌙</div><b>半夜订单发不了</b><p>虚拟商品明明可以秒发，却要守着手机手动回</p></div>
    <div class="pain"><div class="pi">📱</div><b>多号来回切换</b><p>几个店铺几个手机，消息轰炸根本看不过来</p></div>
    <div class="pain"><div class="pi">🤝</div><b>议价拉扯心累</b><p>买家反复砍价，接了吧亏钱，不接吧单飞了</p></div>
  </div>
  <div style="margin:0 44px;background:#171a1f;border-radius:18px;padding:26px 30px;text-align:center;">
    <div style="color:#ffe600;font-size:21px;font-weight:900;">这些活，管家都能替你干</div>
    <div style="color:#c9d4e0;font-size:15px;margin-top:8px;">7×24 小时守店，你只管发货和收钱</div>
  </div>
  <style>
  .pain {{ background:#fff; border-radius:18px; padding:26px 24px; box-shadow:0 10px 26px rgba(23,26,31,.07); }}
  .pain .pi {{ font-size:38px; }}
  .pain b {{ display:block; font-size:20px; margin-top:10px; }}
  .pain p {{ font-size:14.5px; color:#5b6472; margin-top:8px; line-height:1.7; }}
  </style>
""", height=800)

D3 = detail("""
  <div style="padding:64px 44px 0;">
    <div style="font-size:42px;font-weight:900;letter-spacing:2px;">一个管家，全部搞定</div>
    <div style="font-size:17px;color:#5b6472;margin-top:10px;">基于开源项目「闲鱼超级管家」深度打磨，功能持续更新</div>
  </div>
""", """
  <div style="padding:36px 44px 60px;display:grid;grid-template-columns:1fr 1fr;gap:16px;">
    <div class="fi"><b>💬 关键词自动回复</b><p>精确命中 + 兜底话术，按账号独立配置</p></div>
    <div class="fi"><b>🤖 AI 智能议价</b><p>兼容 OpenAI 接口，最低价与议价轮数可控</p></div>
    <div class="fi"><b>📦 卡密自动发货</b><p>四种数据源任选：文字、卡密、图片、API</p></div>
    <div class="fi"><b>🛡️ 发货风险拦截</b><p>异常订单先拦截再发，降低误发损失</p></div>
    <div class="fi"><b>⭐ 自动评价互动</b><p>确认收货自动好评、求小红花、致谢话术</p></div>
    <div class="fi"><b>🧹 商品定时擦亮</b><p>定时擦亮 / 自动上下架，曝光不掉队</p></div>
    <div class="fi"><b>🧾 订单同步管理</b><p>批量拉回历史订单，经营数据一目了然</p></div>
    <div class="fi"><b>👥 多账号集中管理</b><p>跨账号消息中心，回复决策有日志可查</p></div>
  </div>
  <style>
  .fi {{ background:#fff; border-radius:16px; padding:22px 22px; box-shadow:0 8px 22px rgba(23,26,31,.06); }}
  .fi b {{ font-size:18.5px; }}
  .fi p {{ font-size:14px; color:#5b6472; margin-top:7px; line-height:1.65; }}
  </style>
""", height=830)

D4 = detail("""
  <div style="padding:60px 44px 0;">
    """ + chip('版本一 · 桌面版', '#2f7bff') + """
    <div style="font-size:42px;font-weight:900;margin-top:16px;letter-spacing:2px;">双击安装，开箱即用</div>
    <div style="font-size:17px;color:#5b6472;margin-top:10px;">像装普通软件一样简单，全程不需要命令行</div>
  </div>
""", f"""
  <div style="padding:30px 44px 0;display:flex;gap:14px;">
    <div class="stp"><b>1</b><span>下载安装包<br><i>Windows 或 macOS</i></span></div>
    <div class="stp"><b>2</b><span>双击安装<br><i>拖进应用文件夹</i></span></div>
    <div class="stp"><b>3</b><span>打开即用<br><i>扫码添加闲鱼账号</i></span></div>
  </div>
  <style>
  .stp {{ flex:1; background:#fff; border-radius:16px; padding:18px 16px; text-align:center;
         box-shadow:0 8px 22px rgba(23,26,31,.07); }}
  .stp b {{ display:inline-block; width:34px; height:34px; line-height:34px; border-radius:50%;
           background:#2f7bff; color:#fff; font-size:17px; }}
  .stp span {{ display:block; font-size:16px; font-weight:800; margin-top:8px; line-height:1.5; }}
  .stp i {{ font-style:normal; font-size:12.5px; color:#8b94a3; font-weight:500; }}
  </style>

  <div style="padding:28px 44px 0;">
    <div class="browser">
      <div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i>
        <div class="u">闲鱼管家 · 登录界面</div></div>
      <div class="img"><img src="{IMG['login']}"></div>
    </div>
  </div>

  <div style="margin:26px 44px 0;background:#eaf2ff;border-radius:16px;padding:20px 24px;font-size:15px;line-height:1.8;color:#1d4ed8;">
    💡 内置 Chromium 浏览器内核与运行环境：不用装 Python、Node.js，扫码登录与滑块验证开箱即用
  </div>
  <div style="margin:14px 44px 0;display:flex;gap:12px;">
    <span class="pill" style="background:#fff;color:#171a1f;box-shadow:0 6px 16px rgba(23,26,31,.06);">🪟 Windows 10/11</span>
    <span class="pill" style="background:#fff;color:#171a1f;box-shadow:0 6px 16px rgba(23,26,31,.06);">🍎 macOS 11+（含 M 系列芯片）</span>
  </div>
  <div style="margin:16px 44px 44px;font-size:12px;color:#b4a98f;">* 界面为演示数据，实际界面以最新版本为准</div>
""", height=1045)

D5 = detail("""
  <div style="padding:60px 44px 0;">
    <div style="font-size:42px;font-weight:900;letter-spacing:2px;">真实界面抢先看</div>
    <div style="font-size:17px;color:#5b6472;margin-top:10px;">中文工作台，每一项功能都看得见、摸得着</div>
  </div>
""", f"""
  <div style="padding:30px 44px 0;">
    <div style="font-size:20px;font-weight:800;margin-bottom:12px;">📊 经营概览 · 营收 / 订单 / 库存一屏掌握</div>
    <div class="browser">
      <div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i>
        <div class="u">运营概览（演示数据）</div></div>
      <div class="img"><img src="{IMG['dash']}" style="margin-top:-40px;"></div>
    </div>
  </div>
  <div style="padding:26px 44px 44px;">
    <div style="font-size:20px;font-weight:800;margin-bottom:12px;">🧹 商品自动化 · 素材库 / 筛选规则 / 定时任务</div>
    <div class="browser">
      <div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i>
        <div class="u">商品自动化（演示数据）</div></div>
      <div style="max-height:200px;overflow:hidden;"><img class="shot" src="{IMG['automation']}" style="margin-top:-70px;"></div>
    </div>
    <div style="font-size:12px;color:#b4a98f;margin-top:10px;">* 界面为演示数据</div>
  </div>
""", height=1000)

D6 = detail("""
  <div style="padding:60px 44px 0;">
    <div style="font-size:42px;font-weight:900;letter-spacing:2px;">AI 议价与话术，可控可调</div>
    <div style="font-size:17px;color:#5b6472;margin-top:10px;">不是玄学全自动——边界、轮数、风格都由你说了算</div>
  </div>
""", f"""
  <div style="padding:30px 44px 0;display:flex;gap:16px;">
    <div class="ai"><b>⚖️ 议价边界</b><p>最大折扣比例、折扣金额、议价轮数三重限制</p></div>
    <div class="ai"><b>🗣️ 话术风格</b><p>语气、承诺、售后规则按账号自定义</p></div>
    <div class="ai"><b>🧠 上下文记忆</b><p>记住近期对话，跨商品不串台，回复更连贯</p></div>
  </div>
  <style>
  .ai {{ flex:1; background:#fff; border-radius:16px; padding:18px 16px; box-shadow:0 8px 22px rgba(23,26,31,.07); }}
  .ai b {{ font-size:16.5px; }}
  .ai p {{ font-size:13.5px; color:#5b6472; margin-top:7px; line-height:1.65; }}
  </style>

  <div style="padding:26px 44px 0;">
    <div class="browser">
      <div class="bar"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i>
        <div class="u">AI 回复配置（演示数据）</div></div>
      <div style="max-height:300px;overflow:hidden;"><img class="shot" src="{IMG['ai_full']}"
           style="width:158%;max-width:none;margin-left:-33%;margin-top:-639px;"></div>
    </div>
  </div>

  <div style="margin:26px 44px 44px;background:#fffbeb;border:1px solid #fde68a;border-radius:16px;
              padding:20px 24px;font-size:15px;line-height:1.8;color:#92600a;">
    🛟 AI 失败自动兜底：接口超时或异常时，自动降级为关键词回复，绝不中断消息处理
  </div>
""", height=880)

D7 = detail("""
  <div style="padding:60px 44px 0;">
    """ + chip('版本二 · 服务器版', '#12b76a') + """
    <div style="font-size:42px;font-weight:900;margin-top:16px;letter-spacing:2px;">部署一次，全年在线</div>
    <div style="font-size:17px;color:#5b6472;margin-top:10px;">适合有服务器 / NAS 的卖家与工作室，电脑关机也不影响接单</div>
  </div>
""", """
  <div style="padding:30px 44px 0;display:flex;gap:14px;">
    <div class="sce"><b>☁️</b><span>云服务器</span></div>
    <div class="sce"><b>🗄️</b><span>群晖 / 极空间 NAS</span></div>
    <div class="sce"><b>💻</b><span>闲置电脑 / 软路由</span></div>
  </div>
  <style>
  .sce {{ flex:1; background:#f0fbf5; border:1px solid #bbe9d0; border-radius:16px; padding:18px 12px;
         text-align:center; }}
  .sce b {{ font-size:30px; }}
  .sce span {{ display:block; font-size:15px; font-weight:800; margin-top:6px; }}
  </style>

  <div style="padding:26px 44px 0;">
    <div style="background:#101418;border-radius:16px;overflow:hidden;box-shadow:0 16px 40px rgba(16,20,24,.28);">
      <div style="height:36px;background:#232b35;display:flex;align-items:center;gap:7px;padding:0 14px;">
        <i style="width:10px;height:10px;border-radius:50%;background:#ff5f57;display:inline-block;"></i>
        <i style="width:10px;height:10px;border-radius:50%;background:#febc2e;display:inline-block;"></i>
        <i style="width:10px;height:10px;border-radius:50%;background:#28c840;display:inline-block;"></i>
        <span style="color:#6b7686;font-size:12px;margin-left:8px;">terminal</span>
      </div>
      <div style="padding:22px 26px;font-family:Menlo,monospace;font-size:14.5px;line-height:2;color:#c9d4e0;">
        <div style="color:#6b7686;"># 一条命令启动（也提供 docker-compose 编排）</div>
        <div><span style="color:#4ade80;">$</span> docker run -d -p 8080:8080 -v ./data:/app/data \</div>
        <div>&nbsp;&nbsp;&nbsp;xianyu-butler:latest</div>
        <div style="color:#8b94a3;">[+] Running ✔ 闲鱼管家已上线</div>
      </div>
    </div>
  </div>

  <div style="padding:26px 44px 0;display:grid;grid-template-columns:1fr 1fr;gap:14px;">
    <div class="ft"><b>⏰ 24 小时在线</b><p>定时任务、自动回复不因电脑关机而中断</p></div>
    <div class="ft"><b>🌐 异地访问</b><p>手机 / 任意电脑打开浏览器即可管理</p></div>
    <div class="ft"><b>👥 多用户权限</b><p>给员工开子账号，权限分级各管各的店</p></div>
    <div class="ft"><b>💾 自动备份</b><p>数据库定时备份，数据迁移升级无忧</p></div>
  </div>
  <style>
  .ft {{ background:#fff; border-radius:16px; padding:20px 20px; box-shadow:0 8px 22px rgba(23,26,31,.06); }}
  .ft b {{ font-size:17.5px; }}
  .ft p {{ font-size:13.5px; color:#5b6472; margin-top:7px; line-height:1.65; }}
  </style>
  <div style="margin:26px 44px 44px;background:#f0fbf5;border-radius:16px;padding:18px 24px;
              font-size:14.5px;line-height:1.8;color:#0f7a45;">
    ✅ 提供安装部署指导 · 支持国内镜像加速 · 数据库文件始终保存在你自己的服务器上
  </div>
""", height=950)

D8 = detail("""
  <div style="padding:60px 44px 0;">
    <div style="font-size:42px;font-weight:900;letter-spacing:2px;">桌面版 vs 服务器版</div>
    <div style="font-size:17px;color:#5b6472;margin-top:10px;">核心功能完全一致，只是运行的位置不一样</div>
  </div>
""", """
  <div style="padding:30px 44px 0;">
    <table class="cmp">
      <tr><th style="width:26%;"></th>
          <th style="color:#2f7bff;">🖥️ 桌面版</th>
          <th style="color:#12b76a;">☁️ 服务器版</th></tr>
      <tr><td>安装方式</td><td>双击安装，像装微信一样简单</td><td>Docker 部署，提供指导</td></tr>
      <tr><td>上手难度</td><td>⭐ 零基础即可</td><td>⭐⭐ 需一台服务器/NAS</td></tr>
      <tr><td>在线时长</td><td>电脑开机期间在线</td><td>7×24 小时全天在线</td></tr>
      <tr><td>远程管理</td><td>本机操作</td><td>手机浏览器随时随地</td></tr>
      <tr><td>适合人群</td><td>个人卖家 · 新手起步</td><td>工作室 · 多号多店</td></tr>
      <tr><td>数据位置</td><td colspan="2" style="text-align:center;">都保存在你自己的设备上，不经过第三方</td></tr>
    </table>
  </div>
  <style>
  .cmp {{ width:100%; border-collapse:separate; border-spacing:0; background:#fff; border-radius:18px;
          overflow:hidden; box-shadow:0 12px 30px rgba(23,26,31,.08); font-size:15px; }}
  .cmp th {{ background:#171a1f; color:#fff; padding:16px 14px; font-size:17px; }}
  .cmp td {{ padding:15px 14px; border-top:1px solid #f0efe9; line-height:1.6; color:#3c4654; }}
  .cmp td:first-child {{ font-weight:800; color:#171a1f; background:#fbfaf6; }}
  </style>
  <div style="margin:26px 44px 0;background:#eaf2ff;border-radius:16px;padding:20px 24px;font-size:15px;
              line-height:1.8;color:#1d4ed8;">
    🔄 两个版本数据库结构一致，从小做起用桌面版，做大了迁到服务器版，配置数据可以带走
  </div>
  <div style="margin:14px 44px 44px;text-align:center;font-size:14px;color:#8b94a3;">
    另有官方云端托管版（开箱注册即用），详情可咨询客服
  </div>
""", height=815)

D9 = detail("""
  <div style="padding:60px 44px 0;">
    <div style="font-size:42px;font-weight:900;letter-spacing:2px;">购买前请务必阅读 👇</div>
    <div style="font-size:17px;color:#5b6472;margin-top:10px;">虚拟商品，请仔细阅读以下说明</div>
  </div>
""", """
  <div style="padding:30px 44px 60px;display:flex;flex-direction:column;gap:16px;">
    <div class="qa"><b>📦 发货方式</b><p>付款后发送安装包网盘链接 + 图文安装教程；服务器版含部署指导。请留可用的联系方式以便售后。</p></div>
    <div class="qa"><b>🔄 更新政策</b><p>跟随上游开源项目持续更新，同版本号内免费更新，更新包通过网盘发放。</p></div>
    <div class="qa"><b>⚠️ 重要提示</b><p>需自备正常闲鱼账号；自动化操作存在平台风控风险，请自行评估并遵守平台规则；本工具基于开源项目（AGPL-3.0）仅供学习研究使用。</p></div>
    <div class="qa"><b>🍎 macOS 首次打开</b><p>应用未做苹果签名公证：首次打开请「右键 → 打开」，或在 系统设置 → 隐私与安全性 中允许运行。</p></div>
    <div class="qa"><b>🪟 Windows 首次打开</b><p>若 SmartScreen 提示，点击「更多信息 → 仍要运行」即可；杀毒软件误报请添加信任。</p></div>
    <div class="qa"><b>💬 售后支持</b><p>安装问题、使用疑问可随时联系客服；界面截图含演示数据，实际以最新版本为准。</p></div>
  </div>
  <style>
  .qa {{ background:#fff; border-radius:16px; padding:20px 24px; box-shadow:0 8px 22px rgba(23,26,31,.06); }}
  .qa b {{ font-size:17.5px; }}
  .qa p {{ font-size:14px; color:#5b6472; margin-top:8px; line-height:1.75; }}
  </style>
""", height=950)

D10 = detail("""
  <div style="padding:60px 44px 0;">
    """ + chip('增值服务', '#ffe600', '#171a1f') + """
    <div style="font-size:42px;font-weight:900;margin-top:16px;letter-spacing:2px;">标准功能不够用？可以定制</div>
    <div style="font-size:17px;color:#5b6472;margin-top:10px;">在开源基础上为你的生意量身加功能，交付后随版本一起更新维护</div>
  </div>
""", """
  <div style="padding:30px 44px 0;display:grid;grid-template-columns:1fr 1fr;gap:14px;">
    <style>
    .fi {{ background:#fff; border-radius:16px; padding:20px 20px; box-shadow:0 8px 22px rgba(23,26,31,.06); }}
    .fi b {{ font-size:17.5px; }}
    .fi p {{ font-size:13.5px; color:#5b6472; margin-top:7px; line-height:1.65; }}
    </style>
    <div class="fi"><b>🗣️ 回复话术定制</b><p>按类目与人设定制话术库和关键词策略</p></div>
    <div class="fi"><b>🔗 发货渠道对接</b><p>对接你自有的发货 API、网盘或仓库系统</p></div>
    <div class="fi"><b>🏷️ 品牌白标</b><p>替换应用名称、Logo 与界面主题色</p></div>
    <div class="fi"><b>📈 报表增强</b><p>按经营指标定制统计与导出格式</p></div>
    <div class="fi"><b>⚡ 批量操作工具</b><p>批量改价、批量上架、多店协同</p></div>
    <div class="fi"><b>🧩 其他自动化需求</b><p>有想法就能提，评估后纳入排期</p></div>
  </div>

  <div style="padding:26px 44px 0;display:flex;gap:14px;">
    <div class="stp"><b>1</b><span>沟通需求<br><i>说清场景与期望效果</i></span></div>
    <div class="stp"><b>2</b><span>评估报价<br><i>确认范围周期费用</i></span></div>
    <div class="stp"><b>3</b><span>开发联调<br><i>阶段可见进度</i></span></div>
    <div class="stp"><b>4</b><span>交付验收<br><i>随版本更新维护</i></span></div>
  </div>
  <style>
  .stp {{ flex:1; background:#fff; border-radius:16px; padding:18px 12px; text-align:center;
         box-shadow:0 8px 22px rgba(23,26,31,.07); }}
  .stp b {{ display:inline-block; width:34px; height:34px; line-height:34px; border-radius:50%;
           background:#ffe600; color:#171a1f; font-size:17px; font-weight:900; }}
  .stp span {{ display:block; font-size:15.5px; font-weight:800; margin-top:8px; line-height:1.5; }}
  .stp i {{ font-style:normal; font-size:12px; color:#8b94a3; font-weight:500; }}
  </style>

  <div style="margin:26px 44px 0;background:#fffbeb;border:1px solid #fde68a;border-radius:16px;
              padding:18px 24px;font-size:14px;line-height:1.8;color:#92600a;text-align:center;">
    📋 定制说明：基于 AGPL-3.0 开源项目定制，定制部分代码同样开放；风控与合规风险由使用方自行评估
  </div>
  <div style="margin:16px 44px 44px;text-align:center;font-size:15px;font-weight:800;color:#171a1f;">
    💬 定制需求请直接联系客服沟通，评估后给出方案与报价
  </div>
""", height=950)

TEMPLATES = {
    # 主图
    '主图1-主推-全家福': (800, MAIN1),
    '主图2-桌面版': (800, MAIN2),
    '主图3-核心功能': (800, MAIN3),
    '主图4-服务器版': (800, MAIN4),
    '主图5-版本选择': (800, MAIN5),
    # 详情图
    '详情1-品牌头图': (790, D1),
    '详情2-痛点': (790, D2),
    '详情3-功能总览': (790, D3),
    '详情4-桌面版详解': (790, D4),
    '详情5-界面巡礼': (790, D5),
    '详情6-AI能力': (790, D6),
    '详情7-服务器版': (790, D7),
    '详情8-版本对比': (790, D8),
    '详情9-购买须知': (790, D9),
    '详情10-定制服务': (790, D10),
}


def main():
    OUT_MAIN.mkdir(parents=True, exist_ok=True)
    OUT_DETAIL.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={'width': 900, 'height': 1200}, device_scale_factor=2)
        page = ctx.new_page()

        for name, (width, html) in TEMPLATES.items():
            file = tmp / f'{name}.html'
            file.write_text(f'<!DOCTYPE html><html><head><meta charset="utf-8">'
                            f'<style>{BASE_CSS}</style></head><body>{html}</body></html>',
                            encoding='utf-8')
            page.goto(file.as_uri())
            page.wait_for_timeout(500)
            el = page.locator('.cv')
            out_dir = OUT_MAIN if width == 800 else OUT_DETAIL
            el.screenshot(path=str(out_dir / f'{name}.png'))
            print(f'✓ {name}.png')

        browser.close()
    print('全部完成')


if __name__ == '__main__':
    main()
