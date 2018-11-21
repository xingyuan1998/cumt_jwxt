import re
import base64
from datetime import datetime

import requests
import rsa
from bs4 import BeautifulSoup

BASE_URL = "http://jwxt.cumt.edu.cn"


class Craw(object):
    def __init__(self, username, password):
        self.username = username
        self.password = str.encode(password)
        self.session = requests.Session()
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
        }
        self.csrf = None
        self.rsa_mm = None

    def get_crsf_token(self):
        content = self.session.get(BASE_URL + "/jwglxt/xtgl/login_slogin.html", headers=self.headers).text
        # print(content)
        soup_obj = BeautifulSoup(content, "html5lib")
        try:
            csrf = soup_obj.find(id="csrftoken")['value']
        # csrf = csrf_form.find_all("input")
        except Exception as e:
            print(e)
            csrf = None
            print("csrf获取失败")
        self.csrf = csrf

    def get_res_key(self):
        content = self.session.get(
            BASE_URL + "/jwglxt/xtgl/login_getPublicKey.html?language=zh_CN&_time=" + str(
                int(datetime.now().timestamp()))).json()
        print(content)
        try:
            return content['modulus'], content['exponent']
        except Exception as e:
            print(e)
            print("res_key获取失败sa")

    def rsa_encrypt(self):
        self.get_crsf_token()
        res_key = self.get_res_key()
        mm_key = rsa.PublicKey(int.from_bytes(base64.b64decode(res_key[0]), 'big'),
                               int.from_bytes(base64.b64decode(res_key[1]), 'big'))
        rsa_mm = base64.b64encode(rsa.encrypt(self.password, mm_key))
        self.rsa_mm = rsa_mm
        return rsa_mm

    def login(self):
        self.rsa_encrypt()
        content = self.session.post(BASE_URL + "/jwglxt/xtgl/login_slogin.html",
                                    data={'csrftoken': self.csrf, 'yhm': self.username, 'mm': self.rsa_mm})
        if content.status_code == 200:
            return True
        else:
            return False

    def get_curriculum(self):
        data = {
            'xnm': 2018,
            'xqm': 3,
            '_search': False,
            'nd': datetime.now().timestamp(),
            'queryModel.showCount': 15,
            'queryModel.currentPage': 1,
            'queryModel.sortOrder': 'asc',
            'time': 1
        }
        try:
            content = self.session.post(
                BASE_URL + "/jwglxt/xssygl/sykbcx_cxSykbcxxsIndex.html?doType=query&gnmkdm=N2151", data=data).json()
        except Exception as e:
            print(e)
            content = None
        return content

    def get_records(self):
        data = {
            'xnm': 2018,
            'xqm': 3,
            '_search': False,
            'nd': datetime.now().timestamp(),
            'queryModel.showCount': 15,
            'queryModel.currentPage': 1,
            'queryModel.sortOrder': 'asc',
            'time': 0
        }
        try:
            content = self.session.post(
                BASE_URL + "/jwglxt/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005", data=data).json()
        except Exception as e:
            print(e)
            content = None
        return content

    def get_exams(self):
        data = {
            'xnm': 2018,
            'xqm': 3,
            '_search': False,
            'nd': datetime.now().timestamp(),
            'queryModel.showCount': 15,
            'queryModel.currentPage': 1,
            'queryModel.sortOrder': 'asc',
            'time': 0
        }
        try:
            content = self.session.post(
                BASE_URL + "/jwglxt/kwgl/kscx_cxXsksxxIndex.html?doType=query&gnmkdm=N358105&su=" + self.username,
                data=data).json()
        except Exception as e:
            print(e)
            content = None
        return content


if __name__ == '__main__':
    crawer = Craw("用户名", "密码")
    crawer.login()
    crawer.get_exams()
