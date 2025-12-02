import logging
import sys
from pathlib import Path


_LOGGER = None


def init_logging(log_file: Path):
    # 初始化标准日志到文件与控制台
    global _LOGGER
    logger = logging.getLogger("kl")
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    # 控制台处理器 - 使用UTF-8编码
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    # 设置UTF-8编码，避免Windows GBK编码问题
    if hasattr(ch.stream, 'reconfigure'):
        try:
            ch.stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    logger.addHandler(ch)

    # 文件处理器 - 使用UTF-8编码
    fh = logging.FileHandler(str(log_file), encoding='utf-8')
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    _LOGGER = logger


def get_logger(name: str):
    # 获取模块日志器
    global _LOGGER
    return _LOGGER if _LOGGER else logging.getLogger(name)

