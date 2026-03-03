"""统一日志配置模块"""
import logging
import sys
from typing import Optional


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    创建标准化的 logger

    Args:
        name: logger 名称（通常使用 __name__）
        level: 日志级别（DEBUG/INFO/WARNING/ERROR），默认 INFO

    Returns:
        配置好的 Logger 对象
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 设置日志级别
    log_level = getattr(logging, (level or "INFO").upper(), logging.INFO)
    logger.setLevel(log_level)

    # 创建控制台 handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # 设置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
