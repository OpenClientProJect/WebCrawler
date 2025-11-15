import json
import os
import random
import time


class TokenManager:

    @classmethod
    def gen_real_msToken(cls) -> str:
        cookies = TokenManager().getCookie()  # 从文件读取cookies
        if cookies:
            # 从cookies列表中查找msToken的value
            for cookie in cookies:
                if cookie["name"] == "msToken":
                    return cookie["value"]
        else:
            tokens = [
                "-3v1Rj6heZXUgDIZeIVfYCzCJ4v-g75K_9vWQcQWxD-GIxvP9zccyRvPUKUQbQH0iuySB5z0v6m_Gw1q0bm2wMqk38hCRuPmQ8bP9T0ksvU8MD5PIuCQpVhnQTc7xGhAhj0uh2idkl9yHkpyZy8ZuoDHVQ==",
                "rXNoOsBHqGi3EWKby8cOWzyNygptWzwvt3GWfmkOoX9b4hLdLSzK4JNMrLSzZeQ2_U8Gn-wSM4FIXaHa_zjGDVwbZ6Bv5wp_lMidQhGhH8DquyAnX7bGP5Y0UQ8rrT7vSKzRB8HsgS08cAtOolQUdn0RVw=="
            ]
            return random.choice(tokens)

    @classmethod
    def getCookie(cls) -> list:

        if not os.path.exists("tiktok.json"):
            return []
        with open("tiktok.json", "r") as f:
            try:
                return json.load(f)
            except:
                return []

    @classmethod
    def generate_x_bogus(cls) -> str:
        """
        生成X-Bogus参数
        """
        url_str = "https://www.douyin.com/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&browser_language=zh-CN&browser_platform=Win32&browser_name=Firefox&browser_online=true&engine_name=Gecko&os_name=Windows&os_version=10&platform=PC&screen_width=1920&screen_height=1080&browser_version=124.0&engine_version=122.0.0.0&cpu_core_num=12&device_memory=8&aweme_id=7345492945006595379"
        # 将url参数转换为字典
        url_params = dict([param.split("=")
                           for param in url_str.split("?")[1].split("&")])
        from abogus import ABogus as AB
        if not isinstance(url_params, dict):
            raise TypeError("参数必须是字典类型")

        try:
            ab_value = AB().get_value(url_params, )
        except Exception as e:
            raise RuntimeError("生成A-Bogus失败: {0})".format(e))
        return ab_value

    @classmethod
    def generate_x_gnarly(cls) -> str:
        """
        生成X-Gnarly参数
        """
        # 这里应该实现实际的生成逻辑
        gnarly_values = [
            "M5RxOXqBq8cvBGJ1r8/xMqVOG9LQ3HQpSIArjwF/NlrWO61j3Q7fRMd/Uj7fM-1YjUeHrQw8VhoF4HojJvoyxRgq7BXq2hxC5NqIFvQjtuZX0xOEIY2xBauKxoETfkVL-Z6zrQQwtP35ykKbsC1OJTqyi46J1qoucnIopM0DsiwhHB5F95/7AFd6ZjN-Js9IJzTls0rfo5ei3KZZZ2nO2jn9qg1Yj6jh-/iKUvfpXG4QAu-PTq12TJhyaC2yYn7OVgJ1zXfpZ7ltalgUUIEXLDy3hGOsZ8ITzBGdUDo5/mZW4ef3fqszcBfTSqKLucq7U-k=",
            "MPni/0dnLhPWEOnUnbqewMVaifUb2Dq5fk23m4Rk8uPAYwMkOeTlR0S5IpQ1JghO-xT5yCpSZ3h52Tr9cc4dxWqg86Xk796PlpTw1aw2e05F52oJ0EIdKsDU8xPCjJ-owWdLazTU2ZokAQSkn0Cu1UgcgOTAtBAg4exaCwPQXAEoWMCKhl/NPZRG3mLuqhdMif8BBJFNiF9oPt-f/rWH1ZU0Zq1sqL-ofL-XJK-vfmRHOO-xZCFJOJTodj51MxRkf6v3iz3bsqEmQNUVQuuJpR89iCLCH8QOIwBa7azeqlAJxUjShd3OIoVmoKsPhlaYwYk=",
            "Mx7qGGB-h5MWFhjFgnivWwt8r2Qr4kU3wjDr0pIzKJ-0etz3HXoVnG5dCheIpx-P3Xj9QXbfFSqVvLW7en6-Xu/kpt5XyvHuLKVZQotXEpZN/GYWWhPOPuzGasF/9Tg8bXOh5JmEVp/8eE9L42N9xzavLmJ2NuRyMF1G6oRqoWAerlLUMCqfV7Yz161rxElpBewjMzY9IAf7fzsOitBzpQqo7NgwBcAJm0QMbS-XrkS1r7cY9bl-hwHyWKuYDyM-/OYPOd7-gSQPROBz0bN/Z/BKkzM0-cOuoDELKtlCt4E7njZW2RTi9sf0h7pgRzcvRRZ="
        ]
        return random.choice(gnarly_values)

    @classmethod
    def get_fresh_cookie(cls) -> str:
        """
        获取cookie - 需要从浏览器复制
        """
        # 这里应该从浏览器复制实际的cookie
        return "tt_webid_v2=YOUR_WEBID; tt_csrf_token=YOUR_CSRF_TOKEN; sessionid=YOUR_SESSIONID"

    @classmethod
    def gen_verify_fp(cls) -> str:
        """
        生成verifyFp 与 s_v_web_id (Generate verifyFp)
        """
        base_str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        t = len(base_str)
        milliseconds = int(round(time.time() * 1000))
        base36 = ""
        while milliseconds > 0:
            remainder = milliseconds % 36
            if remainder < 10:
                base36 = str(remainder) + base36
            else:
                base36 = chr(ord("a") + remainder - 10) + base36
            milliseconds = int(milliseconds / 36)
        r = base36
        o = [""] * 36
        o[8] = o[13] = o[18] = o[23] = "_"
        o[14] = "4"

        for i in range(36):
            if not o[i]:
                n = 0 or int(random.random() * t)
                if i == 19:
                    n = 3 & n | 8
                o[i] = base_str[n]

        return "verify_" + r + "_" + "".join(o)