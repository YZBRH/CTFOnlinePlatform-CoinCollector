# -*- coding: utf-8 -*-
# @Time    : 2025/1/25 下午11:28
# @Author  : BR
# @File    : log.py
# @description: 日志模块

import time
import os
import sys
from config import debug_status, save_log

LOG_DIR = os.path.join(os.getcwd(), "log")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "log.txt")
MAX_SIZE = 10 * 1024 * 1024  # 10MB

def get_now_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def rotate_log():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) >= MAX_SIZE:
        # 重命名 log.txt -> log.txt.bak 或带时间戳
        import shutil
        backup_name = LOG_FILE + "." + time.strftime("%Y%m%d_%H%M%S")
        shutil.move(LOG_FILE, backup_name)
        # 可选：删除旧备份文件，保留最近 N 个

def save_log_to_file(message: str):
    if not save_log:
        return
    try:
        rotate_log()  # 每次写入前检查是否需要轮转
        with open(LOG_FILE, "a", encoding="utf-8") as fp:
            fp.write(message + "\n")
    except Exception as e:
        print(f"[ERROR] 日志写入失败: {e}")  # 不要静默失败


def info(message: str):
    message = f"[{get_now_time()}][INFO] {message}"
    print("\033[32m" + message + "\033[0m")
    save_log_to_file(message)


def warning(message: str):
    message = f"[{get_now_time()}][WARNING] {message}"
    print("\033[33m" + message + "\033[0m")
    save_log_to_file(message)


def error(message: str):
    message = f"[{get_now_time()}][ERROR] {message}"
    print("\033[31m" + message + "\033[0m")
    save_log_to_file(message)


def debug(message: str):
    if debug_status:
        message = f"[{get_now_time()}][DEBUG] {message}"
        print("\033[34m" + message + "\033[0m")
        save_log_to_file(message)


if __name__ == "__main__":
    info("这是一条信息")
    warning("这是一条警告")
    error("这是一条错误")
    debug("这是一条调试信息")

