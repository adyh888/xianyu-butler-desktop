#!/bin/bash
# ==========================================
# 闲鱼管家桌面版 —— macOS 本地一键构建
# 产物: desktop/release/闲鱼管家-<版本>-arm64.dmg
# 前置: 已安装 Node.js 20+ 和 uv (https://docs.astral.sh/uv/)
# ==========================================
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON=".venv/bin/python"
PYINSTALLER=".venv/bin/pyinstaller"
BROWSERS_PATH="$ROOT/build-output/browsers"

echo "==> [1/6] 准备 Python 虚拟环境 (3.12)"
if [ ! -x "$PYTHON" ]; then
  (cd backend && uv venv --python 3.12 .venv)
fi
uv pip install --python "$PYTHON" -q -r backend/requirements.txt pyinstaller

echo "==> [2/6] 构建前端"
(cd backend/frontend && npm ci --no-audit --no-fund && npm run build)

echo "==> [3/6] 下载 Chromium 到 build-output/browsers"
# 国内网络直连 playwright 官方 CDN 极慢，默认走 npmmirror 镜像
export PLAYWRIGHT_DOWNLOAD_HOST="${PLAYWRIGHT_DOWNLOAD_HOST:-https://cdn.npmmirror.com/binaries/playwright}"
PLAYWRIGHT_BROWSERS_PATH="$BROWSERS_PATH" "$PYTHON" -m playwright install chromium

echo "==> [4/6] 生成应用图标"
(cd backend && ../$PYTHON ../scripts/gen_icon.py)

echo "==> [5/6] PyInstaller 打包后端"
(cd backend && "$PYINSTALLER" xianyu_backend.spec \
  --distpath ../build-output/backend \
  --workpath ../build/pyinstaller \
  --noconfirm)

echo "==> [6/6] Electron 出 dmg"
(cd desktop && npm ci --no-audit --no-fund && npx electron-builder --mac --publish never)

echo ""
echo "✅ 构建完成，安装包在 desktop/release/ 目录下"
