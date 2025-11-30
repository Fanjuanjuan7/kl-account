import logging
from pathlib import Path


_LOGGER = None


def init_logging(log_file: Path):
    # 初始化标准日志到文件与控制台
    global _LOGGER
    logger = logging.getLogger("kl")
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = logging.FileHandler(str(log_file))
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    _LOGGER = logger


def get_logger(name: str):
    # 获取模块日志器
    global _LOGGER
    return _LOGGER if _LOGGER else logging.getLogger(name)

