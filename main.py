# -*- coding: utf-8 -*-
# @Time    : 2025/4/17 下午4:18
# @Author  : BR
# @File    : main.py
# @description:

import requests
import ddddocr
from bs4 import BeautifulSoup
import time
import log
from config import *


class NSSCTF:
    def login(self, username: str, password: str) -> str:
        """
        NSSCTF登录
        :param username: 用户名
        :param password: 密码
        :return: Token
        """
        if not username or not password:
            log.error("NSSCTF: 账户或密码不能为空")
            return ""

        url = "https://www.nssctf.cn/api/user/login/"

        post_data = {
            "username": username,
            "password": password,
            "remember": "0"
            }

        # 登录请求
        try:
            res = requests.post(url, data=post_data)
            log.debug(f"NSSCTF: 登录完成，响应：{res.text}")
        except Exception as err:
            log.error(f"NSSCTF: 网络链接出错：{err}")
            return ""

        # 结果处理
        code = res.json()["code"]
        if code == 200:
            token = res.json()["data"]["token"]
            log.info(f"NSSCTF: 登录成功！Token：{token}")
            return token
        else:
            if code == 201:
                log.error("NSSCTF: 登录失败！账户或密码错误！")
            else:
                log.error(f"NSSCTF: 登录失败！错误码：{code}")
            return ""

    def sign_in(self, token) -> bool:
        """
        NSSCTF签到
        :param token: Token
        :return: 是否签到成功
        """
        if token == "":
            log.error("NSSCTF: Token不能为空")
            return False

        url = "https://www.nssctf.cn/"
        headers = {
            "Cookie": f"token={token}"
        }

        # 开始状态
        start_res = self.person_information(token)
        if start_res["code"] != 200:
            log.error("NSSCTF: 未登录，签到失败！")
            return False

        # requests.get(url, headers=headers)

        # 后续状态
        final_res = self.person_information(token)
        if final_res["code"] != 200:
            log.error("NSSCTF: 未登录，签到失败！")
            return False

        # 前后金币余额对比
        start_coin = start_res["data"]["coin"]
        final_coin = final_res["data"]["coin"]
        if final_coin > start_coin:
            log.info(f"NSSCTF: 签到成功！金币余额: {start_coin}->{final_coin}")
        else:
            log.info(f"NSSCTF: 今日已签到，金币余额: {final_coin}")

        return True

    def person_information(self, token) -> dict:
        """
        获取个人信息
        :param token: Token
        :return: 个人信息
        """
        url = "https://www.nssctf.cn/api/user/info/opt/setting/"
        headers = {
            "Cookie": f"token={token}"
        }

        # 发送请求
        res = requests.get(url, headers=headers)
        log.debug(f"NSSCTF: 获取个人信息完成，响应：{res.text}")

        # 结果处理
        code = res.json()["code"]
        if code == 200:
            log.info(f"NSSCTF: 获取个人信息成功！")
        else:
            if code == 402:
                log.error("NSSCTF: 获取个人信息失败！无效的Token")
            else:
                log.error(f"NSSCTF: 获取个人信息失败！错误码: {code}")

        return res.json()


class Bugku:
    def login(self, username: str, password: str) -> str:
        """
        Bugku登录
        :param username: 用户名
        :param password: 密码
        :return: PHPSESSID
        """
        if not username or not password:
            log.error("Bugku: 账户或密码不能为空")
            return ""

        url = "https://ctf.bugku.com/login/check.html"

        flag = 0
        r_session = requests.session()

        while flag < 5:
            flag += 1
            post_data = {
                "username": username,
                "password": password,
                "vcode": self.classification(r_session),
                "autologin": "0"
            }

            headers = {
                "X-Requested-With": "XMLHttpRequest"
            }

            try:
                res = r_session.post(url, headers=headers, data=post_data)
            except Exception as err:
                log.error(f"Bugku: 网络链接出错：{err}")
                return ""

            log.debug(f"Bugku: 登录返回结果：{res.text}")

            if res.json()["code"] == 1:
                PHPSESSID = r_session.cookies.get('PHPSESSID')
                log.info(f"Bugku: 【第{flag}次尝试】登录成功，PHPSESSID: {PHPSESSID}")
                return PHPSESSID
            else:
                msg = res.json()['msg']
                log.error(f"Bugku: 【第{flag}次尝试】登录失败！{msg}")
                if "验证码" not in msg:
                    return ""

        log.error("Bugku: 超过最大尝试上限，登录失败！")
        return ""

    def classification(self, r_session: requests.Session = None) -> str:
        """
        获取并识别验证码
        :param r_session:
        :return: 识别的验证码
        """
        if r_session is None:
            r_session = requests.session()

        # 获取验证码
        url_captcha = "https://ctf.bugku.com/captcha.html"

        try:
            res = r_session.get(url_captcha)
        except Exception as err:
            log.error(f"Bugku: 网络链接出错：{err}")
            return ""

        # 验证码识别
        ocr = ddddocr.DdddOcr(show_ad=False)
        ocr.set_ranges(6)
        code = ocr.classification(res.content)
        log.debug(f"bugku: 识别登录验证码: {code}")
        return code

    def sign_in(self, PHPSESSID: str) -> bool:

        url = "https://ctf.bugku.com/user/checkin"

        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": f"PHPSESSID={PHPSESSID};"
        }

        start_coin = self.getCoin(PHPSESSID)

        try:
            res = requests.get(url, headers=headers)
        except Exception as err:
            log.error(f"Bugku: 网络链接出错：{err}")
            return False

        final_coin = self.getCoin(PHPSESSID)

        if res.json()["code"] == 1:
            log.info(f"Bugku: 签到成功！金币余额: {start_coin}->{final_coin}")
            return True
        else:
            if "签到过" in res.json()['msg']:
                log.info(f"Bugku: 今日已签到，金币余额: {final_coin}")
                return True
            else:
                log.error(f"Bugku: 签到失败！原因：{res.json()['msg']}")
                return False

    def getCoin(self, PHPSESSID: str) -> int:
        """
        获取当前金币数
        :param PHPSESSID:
        :return: 当前金币余额
        """
        url = "https://ctf.bugku.com/user/recharge.html"
        headers = {
            "Cookie": f"PHPSESSID={PHPSESSID};"
        }

        try:
            res = requests.get(url, headers=headers)
        except Exception as err:
            log.error(f"Bugku: 网络链接出错：{err}")
            return -1

        # log.debug(f"Bugku: 获取数据: {res.text}")
        try:
            soup = BeautifulSoup(res.text, "html.parser")
            coin = int(soup.find("span", class_="alert-link text-warning").text)
        except Exception as e:
            log.error(f"Bugku: 数据处理失败: {e}")
            return -1

        return coin


if __name__ == "__main__":
    flag = True
    start_time = time.time()
    while True:
        if not flag:
            if time.time() - start_time > interval_time:
                flag = True
                start_time = time.time()
            continue

        if nss_username != "" and nss_password != "":
            log.info("NSSCTF: 开始签到")
            token = NSSCTF().login(nss_username, nss_password)
            NSSCTF().sign_in(token)
            log.info("NSSCTF: 签到操作结束")
        else:
            log.info("NSSCTF: 未配置账号密码，跳过")

        if bugku_username != "" and bugku_password != "":
            log.info("Bugku: 开始签到")
            PHPSESSID = Bugku().login(bugku_username, bugku_password)
            Bugku().sign_in(PHPSESSID)
            log.info("Bugku: 签到操作结束")
        else:
            log.info("Bugku: 未配置账号密码，跳过")

        flag = False
