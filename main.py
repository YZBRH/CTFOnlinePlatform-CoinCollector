# -*- coding: utf-8 -*-
# @Time    : 2025/4/17 下午4:18
# @Author  : BR
# @File    : main.py
# @description:

import time
import log
from config import *
from module import *


# 防止onnxruntime警告刷屏
if not onnxruntime_warning:
    import onnxruntime
    onnxruntime.set_default_logger_severity(3)

if __name__ == "__main__":
    try_time = 0
    while True:
        try_time += 1
        log.info(f"第{try_time}轮签到开始...")

        # NSSCTF
        print("-"*20+"\n"+"-"*20)
        if nss_username != "" and nss_password != "":
            log.info("NSSCTF: 开始签到")
            token = NSSCTF().login(nss_username, nss_password)
            NSSCTF().sign_in(token)
            log.info("NSSCTF: 签到操作结束")
        else:
            log.info("NSSCTF: 未配置账号密码，跳过")

        # Bugku
        print("-"*20+"\n"+"-"*20)
        if bugku_username != "" and bugku_password != "":
            log.info("Bugku: 开始签到")
            PHPSESSID = Bugku().login(bugku_username, bugku_password)
            Bugku().sign_in(PHPSESSID)
            log.info("Bugku: 签到操作结束")
        else:
            log.info("Bugku: 未配置账号密码，跳过")

        # CTFHub
        print("-"*20+"\n"+"-"*20)
        if ctfhub_username != "" and ctfhub_password != "":
            log.info("CTFHub: 开始签到")
            cookie = CTFHub().login(ctfhub_username, ctfhub_password)
            CTFHub().sign_in(cookie)
            log.info("CTFHub: 签到操作结束")
        else:
            log.info("CTFHub: 未配置账号密码，跳过")

        # 青少年CTF练习平台
        print("-"*20+"\n"+"-"*20)
        if qsnctf_username != "" and qsnctf_password != "":
            log.info("青少年CTF练习平台: 开始签到")
            access = QSNCTF().login(qsnctf_username, qsnctf_password)
            QSNCTF().sign_in(access)
            log.info("青少年CTF练习平台: 签到操作结束")
        else:
            log.info("青少年CTF练习平台: 未配置账号密码，跳过")

        log.info(f"第{try_time}轮签到结束，将在{interval_time}秒({interval_time//3600.0}小时)后开始下一轮签到...")
        time.sleep(interval_time)



