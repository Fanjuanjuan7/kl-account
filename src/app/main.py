import sys
from pathlib import Path
try:
    from ..utils.logger import get_logger, init_logging
    from ..gui.ui_ctk import launch
except ImportError:
    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT))
    from src.utils.logger import get_logger, init_logging
    from src.gui.ui_ctk import launch


def ensure_runtime_dirs():
    # 创建跨平台运行目录
    base = Path.home() / ".kl_zhanghao"
    (base / "logs").mkdir(parents=True, exist_ok=True)
    (base / "data").mkdir(parents=True, exist_ok=True)
    return base


def run():
    # 初始化日志
    runtime = ensure_runtime_dirs()
    init_logging(runtime / "logs" / "app.log")
    log = get_logger(__name__)
    log.info("starting UI")

    launch(runtime)


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        # 顶层异常处理，保证错误可见
        print(f"fatal error: {e}", file=sys.stderr)
        raise
