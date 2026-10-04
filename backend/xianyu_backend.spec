# -*- mode: python ; coding: utf-8 -*-
"""闲鱼管家桌面版后端 PyInstaller 打包配置（onedir）。

产物布局：
  dist/XianyuButlerBackend/
    XianyuButlerBackend(.exe)     冻结入口（desktop_launcher.py）
    _internal/                    Python 运行时与依赖
      payload/static/             前端构建产物（首启复制到用户数据目录）
      payload/global_config.yml   默认配置（仅首启复制）
      playwright/driver/node      playwright 自带 node，供 execjs 使用
      patchright/driver/node      patchright 自带 node，备用
"""

import os
from pathlib import Path

import patchright
import playwright

ROOT = Path(SPECPATH).resolve()

patchright_pkg = Path(patchright.__file__).resolve().parent
playwright_pkg = Path(playwright.__file__).resolve().parent

datas = [
    # 前端产物 + 默认配置，放到 payload/ 由启动器复制到可写的数据目录
    (str(ROOT / 'static'), 'payload/static'),
    (str(ROOT / 'global_config.yml'), 'payload'),
    # 两家 driver 里都有独立 node 可执行文件：playwright 运行浏览器子进程要用，
    # execjs 也拿它当 JS 运行时（桌面版不要求用户装 Node.js）
    (str(playwright_pkg / 'driver'), 'playwright/driver'),
    (str(patchright_pkg / 'driver'), 'patchright/driver'),
]

# uvicorn 通过字符串 "app.reply_server:app" 动态导入应用，
# 还会按字符串挑选 loops/protocols 实现，都需要显式声明
hiddenimports = [
    'app.reply_server',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.loops.asyncio',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
]

a = Analysis(
    [str(ROOT / 'desktop_launcher.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'IPython',
        'pytest',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='XianyuButlerBackend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='XianyuButlerBackend',
)
