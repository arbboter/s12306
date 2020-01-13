#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from vc import locate_vc
import datetime
from json import loads
import os
import random
import time
import string


def main():
    from config import username, password
    login = Login(usr=username, passwd=password)
    num = 1
    while num > 0:
        if login.login():
            print('登录成功')
            break
        else:
            print('登录失败')
        num -= 1


class Login:
    """
    登录类
    """
    def __init__(self, usr=None, passwd=None):
        self.usr = usr
        self.passwd = passwd
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
            'Referer': 'https://kyfw.12306.cn/otn/login/init',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
        # 12306验证码的8个子图坐标（每个坐标为区间，非唯一）
        self.vc_coordinate = "24,37,128,38,177,44,259,46,36,113,116,119,196,119,256,120".strip().split(',')

        # 地址
        # 验证码地址
        self.url_image = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand'
        # 验证码校验地址
        self.url_image_check = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        self.url_image_check_data = {
                'answer': '',
                'login_site': 'E',
                'rand': 'sjrand'
        }
        # 登录地址
        self.url_login = 'https://kyfw.12306.cn/passport/web/login'
        self.url_login_data = {
                'username': self.usr,
                'password': self.passwd,
                'appid': 'otn',
                'answer': ''
            }

        # 设置cookies
        self.update_cookies()

    def login(self):
        """
        登录
        :return:
        """
        try:
            resp = self.session.get(self.url_image, headers=self.headers)
            vc_path = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.jpg'
            with open(vc_path, 'wb') as f:
                f.write(resp.content)
            # 获取验证码坐标
            vc_pos = locate_vc.locate_vc(vc_path)
            if not vc_pos:
                mp('验证码识别失败')
                return False
            vc_locate = []
            for i in vc_pos:
                vc_locate.extend(self.vc_coordinate[i*2:i*2+2])
            answer = ','.join(vc_locate)
            mp('验证码识别结果：{0} -> {1}'.format(vc_pos, answer))

            # 请求验证码校验
            self.url_image_check_data['answer'] = answer
            resp = self.session.post(self.url_image_check, data=self.url_image_check_data, headers=self.headers)
            content = loads(resp.content)

            # 判断验证码验证结果
            if content['result_code'] != '4':
                mp('验证码校验不通过:{0} <- {1}'.format(content, self.url_image_check_data))
                return False
            mp('验证码校验成功')

            # 请求登录
            headers = self.headers.copy()
            headers.update({
                'Host': 'kyfw.12306.cn',
                'Origin': 'https://kyfw.12306.cn',
                'Referer': 'https://kyfw.12306.cn/otn/resources/login.html'
            })
            self.url_login_data['answer'] = answer
            print('登录参数', self.url_login_data)
            resp = self.session.post(self.url_login, data=self.url_login_data, headers=headers)
            print('登录页结果:', resp.text)

            if resp.status_code != 200:
                raise '登录页返回状态码非正常:{0}'.format(resp.status_code)
            content = loads(resp.content)
            if content['result_code'] == 0:
                return True
            raise '登录页内容异常：{0}'.format(content)
        except Exception as e:
            mp('登录页内容解析异常 {0} -> {1} \n {2}'.format(Exception, e, resp.status_code))
        finally:
            pass
            # 删除临时验证码
            os.remove(vc_path)
        return False

    @staticmethod
    def make_rail_expiration():
        """
        生成12306的RAIL_EXPIRATION，取值如1578988284091
        :return: rail_expiration
        """
        return str(time.time()*1000).split('.')[0]

    @staticmethod
    def make_rail_deviceid():
        """
        生成12306的RAIL_DEVICEID，如gIqeetJacQ3FZfcClzxfRoJXpreji2i8C35HJWeDa8WzKeYpHZKBDwpmtcGzxmkn
        --9okajHoiazel5KDdtFZIFZ-GsC5GR-KOsyqEROyB600GMCxNbBwXpZpE4cNVoUQu-dtw4wrG7Kvlhh5JkjjbfodkBvjxEU
        :return: RAIL_DEVICEID
        """
        # 随机字符串，乘以五保证够长
        ops = string.ascii_letters + string.digits
        ops *= 5
        r = []
        nums = [64, 0, 22, 6, 34, 29]
        for n in nums:
            r.append(''.join(random.sample(ops, n)))
        return '-'.join(r)

    def update_cookies(self):
        """
        2020年1月13日：更新cookie,必须有RAIL_EXPIRATION和RAIL_DEVICEID
        """
        rail_expiration = self.make_rail_expiration()
        rail_deviceid = self.make_rail_deviceid()
        self.sesson.cookies.update({
            'RAIL_EXPIRATION': rail_expiration,
            'RAIL_DEVICEID': rail_deviceid,
        })


# 调试打印
def mp(v):
    """
    打印调试信息的，模块被调用时不打印信息
    :param v:
    :return:
    """
    if __name__ != '__main__':
        return
    print(v)


if __name__ == '__main__':
    main()
