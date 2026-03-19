import re
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

import log
from config import retry_limit
from utils import md5_encrypt, base64_to_image, img_to_code

class BaseModule(ABC):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0"
        }

    @abstractmethod
    def login(self, username, password):
        pass
    
    @abstractmethod
    def sign_in(self, cookie):
        pass


class NSSCTF(BaseModule):
    # NSSCTF平台
    def __init__(self):
        super().__init__()

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
            "password": password
            }

        # 登录请求
        try:
            res = requests.post(url, json=post_data)
            log.debug(f"NSSCTF: 登录完成，响应：{res.text}")
        except Exception as err:
            log.error(f"NSSCTF: 网络链接出错：{err}")
            return ""

        # 结果处理
        code = res.json()["code"]
        if code == 200:
            set_cookie = res.headers.get("Set-Cookie", "")
            if not set_cookie:
                log.error("NSSCTF: 获取cookie失败！")
                return ""

            match = re.search(r'token=([a-f0-9]+)', set_cookie)
            token = match.group(1) if match else None

            if not token:
                log.error("NSSCTF: 获取token失败！")
                return ""

            log.info(f"NSSCTF: 登录成功！Token：{token}")
            return token
        else:
            if code == 201:
                log.error("NSSCTF: 登录失败！账户或密码错误！")
            else:
                log.error(f"NSSCTF: 登录失败！错误码：{code}")
            return ""

    def sign_in(self, token: str) -> bool:
        """
        NSSCTF签到
        :param token: Token
        :return: 是否签到成功
        """
        if token == "":
            log.error("NSSCTF: Token不能为空")
            return False

        url = "https://www.nssctf.cn/"

        self.headers["Cookie"] = f"token={token}"

        requests.get(url, headers=self.headers)

        # 后续状态
        res = self.get_person_information(token)
        if res["code"] != 200:
            log.error("NSSCTF: 未登录，签到失败！")
            return False

        coin = res["data"]["coin"]
        log.info(f"NSSCTF: 今日已签到，金币余额: {coin}")

        return True

    def get_person_information(self, token: str) -> dict:
        """
        获取个人信息
        :param token: Token
        :return: 个人信息
        """
        url = "https://www.nssctf.cn/api/user/info/opt/setting/"

        self.headers["Cookie"] = f"token={token}"

        # 发送请求
        res = requests.get(url, headers=self.headers)
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


class Bugku(BaseModule):
    # Bugku平台
    def __init__(self):
        super().__init__()
        self.headers["X-Requested-With"] = "XMLHttpRequest"

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

        while flag < retry_limit:
            flag += 1
            post_data = {
                "username": username,
                "password": password,
                "vcode": self.classification(r_session),
                "autologin": "0"
            }

            try:
                res = r_session.post(url, headers=self.headers, data=post_data)
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
        code = img_to_code(res.content)
        log.debug(f"bugku: 识别登录验证码: {code}")
        return code

    def sign_in(self, PHPSESSID: str) -> bool:
        """
        Bugku签到
        :param PHPSESSID: 
        :return: 是否签到成功
        """

        url = "https://ctf.bugku.com/user/checkin"

        self.headers["Cookie"] = f"PHPSESSID={PHPSESSID};"

        start_coin = self.get_coin(PHPSESSID)

        try:
            res = requests.get(url, headers=self.headers)
        except Exception as err:
            log.error(f"Bugku: 网络链接出错：{err}")
            return False

        final_coin = self.get_coin(PHPSESSID)

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

    def get_coin(self, PHPSESSID: str) -> int:
        """
        获取当前金币数
        :param PHPSESSID:
        :return: 当前金币余额
        """
        url = "https://ctf.bugku.com/user/recharge.html"

        self.headers["Cookie"] = f"PHPSESSID={PHPSESSID};"

        try:
            res = requests.get(url, headers=self.headers)
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


class CTFHub(BaseModule):
    # CTFHub平台
    def __init__(self):
        super().__init__()

    def login(self, username: str, password: str) -> str:
        """
        CTFHub登录
        :param username: 用户名
        :param password: 密码
        :return:
        """

        if not username or not password:
            log.error("CTFHub: 账户或密码不能为空")
            return ""

        cookie = self.get_base_cookie()

        url = "https://api.ctfhub.com/User_API/User/Login"

        flag = 0  # 重试次数
        while flag < retry_limit:
            flag += 1

            self.headers["Authorization"] = f"ctfhub_sessid={cookie}"

            post_json = {
                "account": username,
                "captcha": self.classification(cookie),
                "password": md5_encrypt(password)
            }

            try:
                res = requests.post(url, headers=self.headers, json=post_json).json()
            except Exception as err:
                log.error(f"CTFHub: 网络链接出错：{err}")
                return ""

            if res.get("status", False):
                log.info(f"CTFHub: 【第{flag}次尝试】登录成功，Cookie: {cookie}")
                return cookie
            else:
                log.error(f"CTFHub: 【第{flag}次尝试】登录失败，原因：{res.get('msg')}")

        log.error("CTFHub: 登录失败，超过最大重试次数！")
        return ""

    def get_base_cookie(self) -> str:
        """
        获取基础cookie
        :return: cookie
        """
        url = "https://api.ctfhub.com/User_API/Other/getCookie"

        try:
            res = requests.get(url).json()
        except Exception as err:
            log.error(f"CTFHub: 网络链接出错：{err}")
            return ""

        if res.get("status", False):
            cookie = res.get("data").get("cookie").replace("ctfhub_sessid=","")
            log.info(f"CTFHub: 获取Cookie成功，Cookie: {cookie}")
            return cookie
        else:
            log.error(f"CTFHub: 获取Cookie失败，原因：{res.get('msg')}")
            return ""

    def classification(self, cookie: str) -> str:
        """
        验证码识别
        :param cookie:
        :return: 识别出的验证码
        """
        url = "https://api.ctfhub.com/User_API/User/getCaptcha"

        self.headers["Authorization"] = f"ctfhub_sessid={cookie}"

        code = ""
        while len(code) != 4:
            try:
                res = requests.get(url, headers=self.headers).json()
            except Exception as err:
                log.error(f"CTFHub: 网络链接出错：{err}")
                return ""

            if not res.get("status", False):
                log.error(f"CTFHub: 获取验证码失败，原因：{res.get('msg')}")
                return ""

            b64_img = res.get("data").get("captcha")
            img = base64_to_image(b64_img)

            code = img_to_code(img)
            log.debug(f"CTFHub: 识别验证码: {code}")
        return code

    def get_person_information(self, cookie: str) -> dict:
        """
        获取个人信息
        :param cookie:
        :return: 个人信息
        """
        url = "https://api.ctfhub.com/User_API/User/getUserinfo"

        self.headers["Authorization"] = f"ctfhub_sessid={cookie}"

        post_json = {
            "target": "self"
        }

        res = requests.post(url, headers=self.headers, json=post_json).json()

        if res.get("status", False):
            log.info("CTFHub：查询个人信息成功")
            log.debug(f"CTFHub：个人信息: {res.get('data')}")
            return res.get("data")
        else:
            log.error(f"CTFHub：查询个人信息失败，原因：{res.get('msg')}")
            return {}

    def sign_in(self, cookie: str) -> bool:
        """
        CTFHub签到
        :param cookie:
        :return: 签到是否成功
        """
        url = "https://api.ctfhub.com/User_API/User/checkIn"

        self.headers["Authorization"] = f"ctfhub_sessid={cookie}"

        start_coin = self.get_person_information(cookie).get("coin", "-1")

        res = requests.get(url, headers=self.headers).json()

        if res.get("status", False):
            final_coin = self.get_person_information(cookie).get("coin", "-1")
            log.info(f"CTFHub: 签到成功！金币余额: {start_coin}->{final_coin}")
            return True
        else:
            if "已经签到" in res.get("msg"):
                log.info(f"CTFHub: 今日已签到，金币余额: {start_coin}")
                return True
            log.error(f"CTFHub: 签到失败！原因：{res.get('msg')}")
            return False


class ADWorld(BaseModule):
    # 攻防世界平台
    def __init__(self):
        super().__init__()

    def login(self, username: str, password: str) -> str:
        """
        攻防世界登录
        :param username: 用户名
        :param password: 密码
        :return: 用户ID,登录token
        """
        url = "https://adworld.xctf.org.cn/api/ad/auth/web/login/"

        flag = 0  # 重试次数
        while flag < retry_limit:
            flag += 1
            captcha = "null"

            json_data = {
                "username": username,
                "password": password,
                "captcha": captcha
            }

            try:
                res = requests.post(url, headers=self.headers, json=json_data).json()
            except Exception as err:
                log.error(f"攻防世界: 网络链接出错：{err}")
                return "", ""
            
            if res.get("code", "") == "AD-000000":
                ret_data = res.get("data", None)

                jwt_token = ret_data.get("token", None)
                user_id = ret_data.get("user",{}).get("id", None)
                log.info(f"攻防世界: 【第{flag}次尝试】登录成功, 用户id: {user_id}, jwtToken: {jwt_token}")
                log.debug(f"攻防世界: 登录信息: {res.get('data')}")
                return jwt_token
            else:
                log.debug(f"攻防世界：登录返回：{res}")
                log.error(f"攻防世界: 【第{flag}次尝试】登录失败，原因：{res.get('message', None)}")

        log.error("攻防世界: 登录失败！超过最大重试次数！")
        return "", ""

    def get_person_information(self, jwt_token: str) -> dict:
        """
        获取个人信息
        :param user_id: 用户ID
        :param jwt_token: 登录Token
        :return: 个人信息
        """
        url = f"https://adworld.xctf.org.cn/api/ad/auth/web/current_auth/"

        self.headers["Authorization"] = jwt_token

        res = requests.get(url, headers=self.headers).json()

        if res.get("code", "") == "AD-000000":
            ret_data = res.get("data", {})

            ret_user_data = ret_data.get("user", None)

            log.info(f"攻防世界: 获取个人信息成功")
            log.debug(f"攻防世界: 个人信息: {ret_user_data}")
            return ret_user_data
        else:
            log.error(f"攻防世界: 获取个人信息失败！原因：{res.get('message')}")
            return {}

    def sign_in(self, cookie):
        pass


class QSNCTF(BaseModule):
    # 青少年CTF练习平台
    def __init__(self):
        super().__init__()

    def login(self, username, password) -> str:
        """
        青少年CTF训练平台登录
        :param username: 用户名
        :param password: 密码
        :return: 登录凭证
        """
        url = "https://www.qsnctf.com/api/login"

        flag = 0
        while flag < retry_limit:
            flag += 1

            post_json = {
                "username": username,
                "password": password,
                "captcha": self.classification(),
                "code": "02c9ad84-d17d-47e8-8a6f-a1228d2b81f9"
            }

            try:
                res = requests.post(url, json=post_json).json()
            except Exception as err:
                log.error(f"青少年CTF练习平台: 网络链接出错：{err}")
                return ""

            access = res.get("access", None)
            if access is not None:
                log.info(f"青少年CTF练习平台: 【第{flag}次尝试】登录成功! access: {access}")
                return access
            
            log.error(f"青少年CTF练习平台: 【第{flag}次尝试】登录失败, 原因: {res.get('detail', '未知原因')}")

        log.error(f"青少年CTF练习平台: 登录失败，超过最大重试次数！")
        return ""

    def classification(self) -> str:
        """
        识别验证码
        :return: 识别出的验证码
        """
        code = ""
        while len(code) < 4:
            url = "https://www.qsnctf.com/api/captcha/02c9ad84-d17d-47e8-8a6f-a1228d2b81f9"

            try:
                img = requests.get(url).content
            except Exception as err:
                log.error(f"青少年CTF练习平台: 网络链接出错：{err}")
                return ""

            code = img_to_code(img)
        return code

    def sign_in(self, access: str) -> bool:
        """
        青少年CTF练习平台签到
        :param access: 登录凭证
        :return: 是否签到成功
        """
        url = "https://www.qsnctf.com/api/api/sign_in"

        self.headers["Authorization"] = f"Bearer {access}"

        start_coin = self.get_person_information(access).get("gold_coins", -1)

        try:
            res = requests.post(url, headers=self.headers).json()
        except Exception as err:
            log.error(f"青少年CTF练习平台: 网络链接出错：{err}")
            return False

        final_coin = self.get_person_information(access).get("gold_coins", -1)

        msg = res.get("detail")

        if "成功" in msg:
            log.info(f"青少年CTF练习平台: 签到成功！金币余额: {start_coin}->{final_coin}")
            return True
        elif "已经签到" in msg:
            log.info(f"青少年CTF练习平台: 今日已经签到！当前金币余额: {final_coin}")
            return True
        else:
            log.error(f"青少年CTF练习平台: 签到失败！原因: {msg}")
            return False

    def get_person_information(self, access: str) -> dict:
        """
        获取个人信息
        :param access: 登录凭证
        :return: 个人信息
        """
        url = "https://www.qsnctf.com/api/profile"

        self.headers["Authorization"] = f"Bearer {access}"

        try:
            res = requests.get(url, headers=self.headers).json()
        except Exception as err:
            log.error(f"青少年CTF练习平台: 网络链接出错：{err}")
            return {}

        msg = res.get("detail", None)
        log.debug(f"青少年CTF练习平台: 获取到的个人信息: {res}")

        if msg is not None:
            log.error(f"青少年CTF练习平台: 获取个人信息失败！原因: {msg}")
            return {}

        return res