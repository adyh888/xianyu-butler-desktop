# 闲鱼管家桌面版（xianyu-butler-desktop）

把开源项目 [闲鱼超级管家 xianyu-super-butler](https://github.com/23Star/xianyu-super-butler) 打包成**开箱即用的 Windows / macOS 桌面应用**：双击安装、打开即用，不需要装 Python、Node.js、Docker，浏览器内核也随包内置，全程无需联网配置环境。

```
双击安装包 → 打开「闲鱼管家」→ 浏览器内核已内置 → 登录界面直接扫码用
（默认管理员账号 admin / admin123，登录后请立即修改密码）
```

---

## 一、下载安装（普通用户看这里）

到本仓库的 [Releases](../../releases) 页面，按系统下载：

| 系统 | 文件 | 安装方式 |
|------|------|----------|
| Windows 10/11 (64位) | `闲鱼管家-x.x.x-x64.exe` | 双击安装，装完自动启动 |
| macOS Apple Silicon (M1/M2/M3/M4) | `闲鱼管家-x.x.x-arm64.dmg` | 打开 dmg，把图标拖进「应用程序」 |
| macOS Intel 芯片 | `闲鱼管家-x.x.x-x64.dmg` | 同上 |

### 首次打开的提示（应用未做签名公证，属正常现象）

- **macOS**：第一次打开如果提示「无法打开，因为无法验证开发者」——在「应用程序」里**右键点「闲鱼管家」→ 打开 → 再点「打开」**，之后就不会再提示。若系统是较新 macOS 且仍拦截，到「系统设置 → 隐私与安全性」底部点「仍要打开」。
- **Windows**：首次运行如果出现 SmartScreen 蓝色提示，点「更多信息 → 仍要运行」。

### 数据放在哪里

所有账号数据、配置、上传的图片都在用户数据目录，卸载重装不会丢失（除非手动删除）：

- Windows：`C:\Users\你\AppData\Roaming\xianyu-butler-desktop\`
- macOS：`~/Library/Application Support/xianyu-butler-desktop/`

---

## 二、项目结构

```
xianyu-butler-desktop/
├── backend/                     # 上游源码（AGPL-3.0），仅 2 处小改动，见下文「与上游的差异」
│   ├── desktop_launcher.py      # 新增：冻结模式启动入口
│   └── xianyu_backend.spec      # 新增：PyInstaller 打包配置
├── desktop/                     # Electron 壳
│   ├── main.js                  # 拉起后端、等端口、开窗口、退出回收进程
│   ├── splash.html              # 启动画面
│   └── build/                   # 应用图标（icns/ico/png）
├── scripts/
│   ├── build-mac.sh             # macOS 本地一键构建
│   └── gen_icon.py              # 图标生成
└── .github/workflows/build.yml  # CI：三平台自动出安装包并发布 Release
```

### 工作原理

```
┌─ 闲鱼管家.app / 闲鱼管家.exe (Electron) ─────────────────────┐
│  1. 挑一个空闲端口，环境变量告知后端：                         │
│     API_HOST=127.0.0.1  API_PORT=<空闲端口>                  │
│     XIANYU_HOME=<用户数据目录>  PLAYWRIGHT_BROWSERS_PATH=<内置浏览器> │
│  2. 启动 PyInstaller 打包的后端 sidecar（日志写进用户目录）     │
│  3. 轮询后端就绪 → 显示主窗口（启动期间是 splash 画面）         │
│  4. 外部链接交给系统浏览器；退出时完整回收后端进程              │
└──────────────────────────────────────────────────────────────┘
```

- **后端**：上游 FastAPI 服务原样运行，窗口里看到的就是它的 Web 界面，功能与 Docker 部署版一致（自动回复/自动发货/订单同步/看板等）。
- **浏览器内核**：构建时用 `playwright install chromium` 下载并打进安装包（所以安装包约 300MB），扫码登录、滑块验证离线可用，不依赖用户电脑上有没有 Chrome。
- **JS 运行时**：签名脚本所需的 Node.js 直接复用 playwright 自带的 node，用户机器无需安装 Node。
- **数据目录**：后端通过 `XIANYU_HOME` 把数据库/配置/日志写到用户数据目录，应用本体保持只读，升级覆盖安装不会丢数据。

## 三、与上游的差异（AGPL-3.0 声明）

本项目遵循上游的 **AGPL-3.0** 许可证，源码全部开放。对 `backend/`（上游源码副本）的改动如下，其余与上游一致：

改动的 3 个文件（不设置 `XIANYU_HOME` 环境变量时行为与上游完全相同，不影响 Docker/源码部署）：

1. `app/config.py`：`PROJECT_ROOT` 支持 `XIANYU_HOME` 环境变量重定向（桌面版把可写目录指到用户数据目录）。
2. `app/reply_server.py`：同上。
3. `utils/xianyu_utils.py`：签名 JS 文件路径同样支持 `XIANYU_HOME` 优先。

新增的 2 个文件：

- `desktop_launcher.py`：冻结模式启动入口（数据目录初始化、PATH 注入、拉起上游 Start.py）。
- `xianyu_backend.spec`：PyInstaller 打包配置。

同步上游更新的方式：用上游新版本覆盖 `backend/`，然后重新应用上面 3 处改动。

## 四、开发者：本地构建（macOS）

前置要求：Node.js 20+、[uv](https://docs.astral.sh/uv/)。其余（Python 3.12、依赖、Chromium）脚本自动处理：

```bash
bash scripts/build-mac.sh
# 产物: desktop/release/闲鱼管家-<版本>-arm64.dmg
```

开发调试（不走打包，直接起 Electron 壳 + 源码后端）：

```bash
# 终端 1：源码跑后端（在 backend/ 目录，与上游一致）
cd backend && ../.venv/bin/python Start.py
# 终端 2：开发模式跑壳（读取 build-output/browsers 里的浏览器）
cd desktop && npx electron .
```

### 国内网络构建注意事项

- **Chromium 下载慢/失败**：设置镜像 `export PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright`（`build-mac.sh` 已内置）。
- **electron-builder 卡在 `downloading dmgbuild-bundle`**：它要从 GitHub 拉 dmg 制作工具（约 22MB），直连常被重置。手动下载后放进缓存即可跳过：
  ```bash
  curl -L -o /tmp/dmgbuild.tar.gz "https://ghfast.top/https://github.com/electron-userland/electron-builder-binaries/releases/download/dmg-builder%401.2.5/dmgbuild-bundle-arm64-75c8a6c.tar.gz"
  # x86_64 机器把 arm64 换成 x86_64
  shasum -a 256 /tmp/dmgbuild.tar.gz   # 应为 793404d0c96687e27d5ee40a668d498c92e36a64d6c2906df511031adb33cbeb
  mkdir -p ~/Library/Caches/electron-builder/dmg-builder@1.2.5
  cp /tmp/dmgbuild.tar.gz ~/Library/Caches/electron-builder/dmg-builder@1.2.5/dmgbuild-bundle-arm64-75c8a6c.tar.gz
  ```
  或者设置镜像环境变量 `export ELECTRON_BUILDER_BINARIES_MIRROR=https://npmmirror.com/mirrors/electron-builder-binaries/`（镜像同步可能滞后）。GitHub Actions 构建不受影响。

## 五、开发者：发布三平台安装包

仓库已配好 GitHub Actions（`.github/workflows/build.yml`），推一个 tag 即可自动构建并发布：

```bash
git tag v1.0.0 && git push origin v1.0.0
# Actions 会产出：arm64.dmg（macOS 14 跑）、x64.dmg（macOS 13 跑）、x64.exe（Windows 跑）
# 完成后在 Releases 页面生成草稿，检查后点发布
```

也可以在 Actions 页面手动触发（workflow_dispatch），产物在 Artifacts 里下载。

## 六、常见问题

- **端口占用？** 桌面版每次启动自动挑空闲端口，不会和 8080 之类冲突；后端只监听 127.0.0.1，不对外网开放。
- **能多开吗？** 不能，重复启动会自动聚焦已有窗口（数据目录是同一份，多开也没有意义）。
- **忘了后台密码？** 关闭应用后删除用户数据目录里的 `app_root/data/xianyu_data.db`（会清空所有账号数据，慎用），重新打开即为默认 admin/admin123。
- **滑块验证需要 Chrome 吗？** 优先用内置 Chromium（patchright），不需要；仅当走 DrissionPage 兜底逻辑时才需要系统安装 Chrome。
- **杀毒软件报毒？** PyInstaller 打包的程序偶尔被误报，加入信任即可；介意的可以自己用本仓库源码构建。
- **风险提示（同上游）**：本项目仅供学习研究，自动化操作闲鱼存在账号风控风险，请自行评估并遵守平台规则。
