"""闲鱼管家桌面版 —— 冻结模式启动入口。

Electron 壳通过环境变量传入运行参数（XIANYU_HOME / API_PORT /
PLAYWRIGHT_BROWSERS_PATH）；冻结的 exe 被直接运行时使用默认数据目录，
行为等价于源码目录里的 python Start.py。

打包布局（PyInstaller onedir，_MEIPASS 即 <dist>/XianyuButlerBackend/_internal）：
  _MEIPASS/payload/static/           前端构建产物（首次启动复制到数据目录）
  _MEIPASS/payload/global_config.yml 默认配置（仅首次启动复制）
  _MEIPASS/playwright/driver/node    playwright 自带的 node，供 execjs 使用
  _MEIPASS/patchright/driver/node    patchright 自带的 node，备用
"""

import asyncio
import os
import shutil
import sys
from pathlib import Path


def _is_frozen() -> bool:
    return bool(getattr(sys, 'frozen', False))


def _meipass() -> Path:
    if _is_frozen() and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def _default_home() -> Path:
    if sys.platform == 'darwin':
        base = Path.home() / 'Library' / 'Application Support'
    elif sys.platform == 'win32':
        base = Path(os.getenv('APPDATA') or (Path.home() / 'AppData' / 'Roaming'))
    else:
        base = Path(os.getenv('XDG_DATA_HOME') or (Path.home() / '.local' / 'share'))
    return base / 'xianyu-butler'


def _sync_payload(meipass: Path, home: Path) -> None:
    """把只读载荷复制到用户数据目录。

    static 每次启动都覆盖同步（保证前端与后端版本一致），但用 dirs_exist_ok
    合并而不是先删除，这样用户上传的 static/uploads 等运行期文件能保留；
    global_config.yml 只在缺失时复制，避免升级覆盖用户配置。
    """
    home.mkdir(parents=True, exist_ok=True)

    payload_static = meipass / 'payload' / 'static'
    if payload_static.is_dir():
        shutil.copytree(payload_static, home / 'static', dirs_exist_ok=True)

    payload_config = meipass / 'payload' / 'global_config.yml'
    target_config = home / 'global_config.yml'
    if payload_config.is_file() and not target_config.exists():
        shutil.copy2(payload_config, target_config)


def _prepend_js_runtimes(meipass: Path) -> None:
    """execjs 编译签名脚本需要一个 JS 运行时。

    桌面版不要求用户安装 Node.js：playwright / patchright 自带的 driver
    目录里有完整的 node 可执行文件，把它放到 PATH 最前面即可被 execjs 检出。
    """
    for driver in (meipass / 'playwright' / 'driver', meipass / 'patchright' / 'driver'):
        if (driver / 'node').exists() or (driver / 'node.exe').exists():
            os.environ['PATH'] = str(driver) + os.pathsep + os.environ.get('PATH', '')


def main() -> None:
    # Start.py 在冻结模式下找不到浏览器时会用 sys.executable -m playwright
    # 尝试补装；冻结的 exe 不认识 -m 参数，这里直接退出，避免递归拉起第二个实例。
    if '-m' in sys.argv[1:]:
        sys.exit(0)

    if _is_frozen():
        meipass = _meipass()
        home = Path(os.environ.get('XIANYU_HOME') or _default_home())
        _sync_payload(meipass, home)
        os.environ['XIANYU_HOME'] = str(home)
        os.chdir(home)
        _prepend_js_runtimes(meipass)
    else:
        # 源码模式：与上游行为一致，不做任何重定向。
        os.chdir(_meipass())

    import Start  # noqa: E402  上游入口；导入时完成浏览器检测等初始化
    asyncio.run(Start.main())


if __name__ == '__main__':
    main()
