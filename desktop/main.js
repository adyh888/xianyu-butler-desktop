/**
 * 闲鱼管家桌面版 —— Electron 主进程
 *
 * 职责：
 *   1. 拉起打包好的 Python 后端（sidecar），把日志落到用户数据目录
 *   2. 轮询后端 HTTP 端口就绪后打开主窗口（启动期间显示 splash）
 *   3. 退出时确保后端进程被完整回收；后端异常退出时给出提示/自动重启
 *
 * 与后端的约定（backend/desktop_launcher.py）：
 *   API_HOST / API_PORT            后端监听地址与端口
 *   XIANYU_HOME                    可写数据目录（数据库、配置、上传文件）
 *   PLAYWRIGHT_BROWSERS_PATH       随包分发的 Chromium 位置
 */

const { app, BrowserWindow, dialog, shell } = require('electron');
const { spawn } = require('child_process');
const net = require('net');
const path = require('path');
const fs = require('fs');

const isDev = !app.isPackaged;
// 打包后资源根目录（backend/、browsers/ 由 electron-builder extraResources 放进来）
const RESOURCES_ROOT = isDev ? path.join(__dirname, '..') : process.resourcesPath;

const BACKEND_READY_TIMEOUT_MS = 3 * 60 * 1000; // 首次启动要复制数据目录并拉起浏览器验证
const MAX_RESTARTS = 3;

let backendProc = null;
let mainWindow = null;
let splashWindow = null;
let backendPort = 0;
let backendReady = false;
let restartCount = 0;
let quitting = false;

// ---------- 基础工具 ----------

function userDataDir() {
  return path.join(app.getPath('userData'), 'app_root');
}

function logDir() {
  return path.join(app.getPath('userData'), 'logs');
}

function backendLogPath() {
  return path.join(logDir(), 'backend.log');
}

function appendLog(line) {
  try {
    fs.mkdirSync(logDir(), { recursive: true });
    const file = backendLogPath();
    try {
      const stat = fs.statSync(file);
      if (stat.size > 5 * 1024 * 1024) fs.renameSync(file, `${file}.old`);
    } catch (_) { /* 首次没有日志文件 */ }
    fs.appendFileSync(file, line);
  } catch (_) { /* 日志失败不影响主流程 */ }
}

function backendExecutable() {
  const name = process.platform === 'win32' ? 'XianyuButlerBackend.exe' : 'XianyuButlerBackend';
  return path.join(RESOURCES_ROOT, 'backend', name);
}

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      server.close(() => resolve(port));
    });
    server.on('error', reject);
  });
}

function waitForBackend(port, timeoutMs) {
  const startedAt = Date.now();
  return new Promise((resolve, reject) => {
    const tick = async () => {
      if (quitting) return reject(new Error('应用正在退出'));
      try {
        const res = await fetch(`http://127.0.0.1:${port}/static/index.html`, { method: 'GET' });
        if (res.ok) return resolve();
      } catch (_) { /* 后端还没起来，继续等 */ }
      if (Date.now() - startedAt > timeoutMs) {
        return reject(new Error(`等待后端启动超时（${Math.round(timeoutMs / 1000)} 秒）`));
      }
      setTimeout(tick, 500);
    };
    tick();
  });
}

// ---------- 后端进程管理 ----------

function startBackend() {
  const exe = backendExecutable();
  if (!fs.existsSync(exe)) {
    throw new Error(`找不到后端程序: ${exe}`);
  }

  const env = {
    ...process.env,
    API_HOST: '127.0.0.1',
    API_PORT: String(backendPort),
    XIANYU_HOME: userDataDir(),
    PLAYWRIGHT_BROWSERS_PATH: path.join(RESOURCES_ROOT, 'browsers'),
    PYTHONUNBUFFERED: '1',
  };
  delete env.API_KEY;

  // windowsHide 会让 Windows 用 CREATE_NO_WINDOW 拉起控制台程序，不弹黑窗
  const child = spawn(exe, [], {
    env,
    cwd: userDataDir(),
    windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  appendLog(`\n===== ${new Date().toISOString()} 后端启动 (pid=${child.pid}) =====\n`);
  const pipe = (stream) => {
    stream.setEncoding('utf8');
    stream.on('data', (chunk) => appendLog(chunk));
  };
  pipe(child.stdout);
  pipe(child.stderr);

  child.on('exit', (code, signal) => {
    appendLog(`===== 后端退出 code=${code} signal=${signal} =====\n`);
    backendProc = null;
    backendReady = false;
    if (quitting) return;
    handleBackendExit(code);
  });

  backendProc = child;
  return child;
}

function stopBackend() {
  const proc = backendProc;
  backendProc = null;
  if (!proc || proc.exitCode !== null) return;
  try {
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', String(proc.pid), '/T', '/F'], { windowsHide: true });
    } else {
      proc.kill('SIGTERM');
      setTimeout(() => {
        try { proc.kill('SIGKILL'); } catch (_) { /* 已退出 */ }
      }, 3000);
    }
  } catch (_) { /* 进程可能已退出 */ }
}

function handleBackendExit(code) {
  restartCount += 1;
  if (restartCount > MAX_RESTARTS) {
    showErrorAndQuit(
      '后端服务多次异常退出，应用即将关闭。\n\n' +
      `日志文件：${backendLogPath()}\n\n` +
      '可以尝试删除用户数据目录后重新启动（会保留备份建议）。'
    );
    return;
  }
  relaunchBackendAndWindow();
}

async function relaunchBackendAndWindow() {
  try {
    backendPort = await getFreePort();
    startBackend();
    await waitForBackend(backendPort, BACKEND_READY_TIMEOUT_MS);
    backendReady = true;
    if (!mainWindow || mainWindow.isDestroyed()) {
      createMainWindow();
    }
    await mainWindow.loadURL(`http://127.0.0.1:${backendPort}/static/index.html`);
  } catch (err) {
    showErrorAndQuit('后端服务启动失败：\n' + (err && err.message ? err.message : String(err)) +
      `\n\n日志文件：${backendLogPath()}`);
  }
}

function showErrorAndQuit(message) {
  dialog.showErrorBox('闲鱼管家', message);
  app.quit();
}

// ---------- 窗口 ----------

function createSplash() {
  splashWindow = new BrowserWindow({
    width: 420,
    height: 260,
    frame: false,
    resizable: false,
    movable: true,
    show: false,
    backgroundColor: '#0f172a',
    center: true,
    webPreferences: { contextIsolation: true, nodeIntegration: false },
  });
  splashWindow.loadFile(path.join(__dirname, 'splash.html'));
  splashWindow.once('ready-to-show', () => splashWindow.show());
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1320,
    height: 860,
    minWidth: 1080,
    minHeight: 700,
    show: false,
    title: '闲鱼管家',
    backgroundColor: '#f1f5f9',
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      spellcheck: false,
    },
  });

  // 外部链接（闲鱼页面、文档等）一律交给系统默认浏览器
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:\/\//i.test(url)) shell.openExternal(url);
    return { action: 'deny' };
  });

  // 主窗口只允许停留在本地后端上
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!url.startsWith(`http://127.0.0.1:${backendPort}/`)) {
      event.preventDefault();
      if (/^https?:\/\//i.test(url)) shell.openExternal(url);
    }
  });

  // 调试模式：XIANYU_DESKTOP_DEBUG=1 时加载完成后自动截图，供 CI/无头环境验证
  mainWindow.webContents.on('did-finish-load', () => {
    if (!process.env.XIANYU_DESKTOP_DEBUG) return;
    setTimeout(async () => {
      try {
        const image = await mainWindow.webContents.capturePage();
        const out = path.join(app.getPath('userData'), 'debug-home.png');
        fs.writeFileSync(out, image.toPNG());
        appendLog(`[debug] 截图已保存: ${out}\n`);
      } catch (err) {
        appendLog(`[debug] 截图失败: ${err}\n`);
      }
    }, 3000);
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (splashWindow && !splashWindow.isDestroyed()) splashWindow.close();
  });

  mainWindow.on('closed', () => { mainWindow = null; });
}

// ---------- 应用生命周期 ----------

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  app.whenReady().then(async () => {
    if (isDev) app.setAppUserModelId('com.xianyubutler.desktop');
    createSplash();

    try {
      fs.mkdirSync(userDataDir(), { recursive: true });
    } catch (err) {
      showErrorAndQuit('无法创建用户数据目录：' + String(err));
      return;
    }

    await relaunchBackendAndWindow();
  });

  app.on('window-all-closed', () => {
    // 桌面工具型应用：关窗即退出（macOS 也保持一致，避免后台残留进程）
    app.quit();
  });

  app.on('before-quit', () => {
    quitting = true;
    stopBackend();
  });

  process.on('exit', () => { if (!quitting) { quitting = true; stopBackend(); } });
}
