import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class Logger:
    """日志管理类"""

    def __init__(self, name='my_app', log_dir='logs', level=logging.INFO):
        """
        初始化logger

        Args:
            name: logger名称
            log_dir: 日志目录
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 避免重复添加handler
        if self.logger.handlers:
            return

        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 文件handler - 按大小轮转
        log_file = os.path.join(log_dir, f'{name}.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 错误日志单独记录
        error_file = os.path.join(log_dir, f'{name}_error.log')
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

    def get_logger(self):
        """返回logger对象"""
        return self.logger


# 便捷函数
def get_logger(name='my_app', log_dir='logs', level=logging.INFO):
    """快速获取logger"""
    return Logger(name, log_dir, level).get_logger()