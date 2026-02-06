# coding: utf-8
"""
日志配置模块

提供统一的日志系统配置，支持文件和控制台输出，
支持日志轮转，防止日志文件过大。

@author: OsKhQuant
@version: 1.0
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Union

# 默认日志级别
DEFAULT_LOG_LEVEL = logging.DEBUG

# 默认日志文件大小（10MB）
DEFAULT_MAX_BYTES = 10 * 1024 * 1024

# 默认保留日志文件数量
DEFAULT_BACKUP_COUNT = 5


def get_log_filename(base_name: str = None) -> str:
    """生成日志文件名（带日期）

    Args:
        base_name: 日志基础名称，默认使用当前脚本名

    Returns:
        str: 日志文件名
    """
    if base_name is None:
        # 获取当前脚本名称
        base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        if not base_name or base_name == '__main__':
            base_name = 'khquant'

    return f"{base_name}_{datetime.now().strftime('%Y%m%d')}.log"


def setup_logging(
    log_dir: str = None,
    log_level: int = DEFAULT_LOG_LEVEL,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
    logger_name: str = None,
    add_console: bool = True,
    add_file: bool = True
) -> logging.Logger:
    """设置项目日志系统

    Args:
        log_dir: 日志目录，默认在程序所在目录创建logs文件夹
        log_level: 日志级别
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的日志文件数量
        logger_name: 日志器名称，None表示根日志器
        add_console: 是否添加控制台处理器
        add_file: 是否添加文件处理器

    Returns:
        logging.Logger: 配置好的日志器
    """
    # 获取或创建日志器
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # 清除现有处理器（避免重复）
    if logger.handlers:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    # 创建logs目录
    if log_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(base_dir, 'logs')

    if add_file and log_dir:
        os.makedirs(log_dir, exist_ok=True)

        # 文件处理器（带轮转）
        log_filename = get_log_filename()
        log_file = os.path.join(log_dir, log_filename)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 控制台处理器
    if add_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_module_logger(module_name: str, log_level: int = DEFAULT_LOG_LEVEL) -> logging.Logger:
    """获取模块日志器

    使用示例:
        logger = get_module_logger(__name__)
        logger.info("这是一条日志")

    Args:
        module_name: 模块名称，建议使用 __name__
        log_level: 日志级别

    Returns:
        logging.Logger: 配置好的模块日志器
    """
    # 标准化模块名称
    if not module_name.startswith('OsKhQuant.'):
        module_name = f"OsKhQuant.{module_name}"

    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)

    # 确保处理器已添加（如果还没有）
    if not logger.handlers:
        setup_logging(logger_name=logger.name)

    return logger


class LoggerMixin:
    """日志混入类

    为类添加日志功能，子类自动获得logger属性。

    使用示例:
        class MyClass(LoggerMixin):
            def my_method(self):
                self.logger.info("日志消息")

    Attributes:
        logger: 类级别的日志器
    """

    @property
    def logger(self) -> logging.Logger:
        """获取类日志器"""
        if not hasattr(self, '_logger'):
            self._logger = get_module_logger(self.__class__.__name__)
        return self._logger


def log_function_call(func):
    """函数调用日志装饰器

    自动记录函数的调用信息和执行结果。

    使用示例:
        @log_function_call
        def my_function(a, b):
            return a + b
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_module_logger(func.__module__)
        logger.debug(f"调用函数: {func.__name__}(args={args}, kwargs={kwargs})")

        result = func(*args, **kwargs)

        logger.debug(f"函数返回: {func.__name__} -> {result}")
        return result

    return wrapper


class PerformanceLogger:
    """性能日志记录器

    用于记录代码块或函数的执行时间。

    使用示例:
        with PerformanceLogger("my_operation"):
            # 执行代码
            pass

        # 输出: [PERF] my_operation 耗时: 0.123s
    """

    def __init__(self, operation_name: str, logger: logging.Logger = None):
        self.operation_name = operation_name
        self.logger = logger or get_module_logger('performance')
        self.start_time = None

    def __enter__(self):
        import time
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self.start_time
        self.logger.info(f"[PERF] {self.operation_name} 耗时: {elapsed:.3f}s")
        return False  # 不抑制异常


# 便捷函数：快速设置日志
def quick_setup(log_level: int = logging.INFO) -> logging.Logger:
    """快速设置日志（使用默认配置）"""
    return setup_logging(log_level=log_level)


# 便捷函数：禁用指定名称的日志
def disable_logger(logger_name: str):
    """禁用指定日志器的所有输出"""
    logging.getLogger(logger_name).setLevel(logging.CRITICAL + 1)


# 便捷函数：设置控制台日志级别
def set_console_level(logger_name: str, level: int):
    """设置指定日志器的控制台日志级别"""
    logger = logging.getLogger(logger_name)
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            handler.setLevel(level)
