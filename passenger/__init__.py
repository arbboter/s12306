#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from json import loads


def main():
    from auth.login import Login
    au = Login()
    # 为了测试方便，此处直接使用浏览器登录后的cookies，存到文件后再加载
    au.loads_cookies('cookies.txt')
    passengers = Passengers(au.session)
    passengers.pull_data()
    if not passengers.data:
        mp('未获取到乘客信息')
        return

    data = passengers.data
    # 组装信息
    import prettytable
    tab = prettytable.PrettyTable()
    # 标题头
    tab.field_names = data[0].key_info().keys()
    # 组装乘客信息
    for t in data:
        tab.add_row(t.key_info(data).values())
    # 表格显示乘客信息
    mp(tab)


class Passenger:
    def __init__(self):
        # *姓名
        self.passenger_name = ''
        # 性别代码
        self.sex_code = ''
        # 性别名称
        self.sex_name = ''
        # *出生年月
        self.born_date = ''
        # 国籍
        self.country_code = ''
        # 证件类型代码
        self.passenger_id_type_code = ''
        # *证件类型名称
        self.passenger_id_type_name = ''
        # *证件号码
        self.passenger_id_no = ''
        # 乘客类型代码
        self.passenger_type = ''
        # 乘客标志
        self.passenger_flag = ''
        # *乘客类型名称
        self.passenger_type_name = ''
        # 手机号码
        self.mobile_no = ''
        # 电话号码
        self.phone_no = ''
        # 邮箱
        self.email = ''
        # 地址
        self.address = ''
        # 邮政编码
        self.postalcode = ''
        # 姓名首字母
        self.first_letter = ''
        # 记录数
        self.recordCount = ''
        # 是否账户本人
        self.isUserSelf = ''
        # 总次数
        self.total_times = ''
        # 删除日期
        self.delete_time = ''
        # 总加密字符串
        self.allEncStr = ''
        # 是否成人
        self.isAdult = ''
        # 大于10岁儿童
        self.isYongThan10 = ''
        # 大于14岁儿童
        self.isYongThan14 = ''
        # 大于60岁老人
        self.isOldThan60 = ''
        # 出生日期
        self.gat_born_date = ''
        # 有效起始日期
        self.gat_valid_date_start = ''
        # 有效截止日期
        self.gat_valid_date_end = ''
        # 版本号
        self.gat_version = ''

    def loads(self, json_data):
        """
        json数据转换为当前对象
        :param json_data: json数据
        :return: 无
        """
        self.passenger_name = json_data.get('passenger_name')
        self.sex_code = json_data.get('sex_code')
        self.sex_name = json_data.get('sex_name')
        self.born_date = json_data.get('born_date')
        self.country_code = json_data.get('country_code')
        self.passenger_id_type_code = json_data.get('passenger_id_type_code')
        self.passenger_id_type_name = json_data.get('passenger_id_type_name')
        self.passenger_id_no = json_data.get('passenger_id_no')
        self.passenger_type = json_data.get('passenger_type')
        self.passenger_flag = json_data.get('passenger_flag')
        self.passenger_type_name = json_data.get('passenger_type_name')
        self.mobile_no = json_data.get('mobile_no')
        self.phone_no = json_data.get('phone_no')
        self.email = json_data.get('email')
        self.address = json_data.get('address')
        self.postalcode = json_data.get('postalcode')
        self.first_letter = json_data.get('first_letter')
        self.recordCount = json_data.get('recordCount')
        self.isUserSelf = json_data.get('isUserSelf')
        self.total_times = json_data.get('total_times')
        self.delete_time = json_data.get('delete_time')
        self.allEncStr = json_data.get('allEncStr')
        self.isAdult = json_data.get('isAdult')
        self.isYongThan10 = json_data.get('isYongThan10')
        self.isYongThan14 = json_data.get('isYongThan14')
        self.isOldThan60 = json_data.get('isOldThan60')
        self.gat_born_date = json_data.get('gat_born_date')
        self.gat_valid_date_start = json_data.get('gat_valid_date_start')
        self.gat_valid_date_end = json_data.get('gat_valid_date_end')
        self.gat_version = json_data.get('gat_version')

    def key_info(self):
        """
        乘客关键信息
        :return:
        """
        return {
            '旅客姓名': self.passenger_name,
            '旅客性别': self.sex_name,
            '出生年月': self.born_date[:10],
            '证件类型': self.passenger_id_type_name,
            '证件号码': self.passenger_id_no,
            '电话号码': self.mobile_no,
            '旅客类型': self.passenger_type_name,
        }


class Passengers:
    def __init__(self, session):
        self.session = session
        self.url_query = 'https://kyfw.12306.cn/otn/passengers/query'
        self.headers_query = {
            'Host': 'kyfw.12306.cn',
            'Origin': 'https://kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/view/passengers.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/79.0.3945.88 Safari/537.36'
        }
        self.data = []

    def pull_data(self):
        try:
            passengers = []
            # 获取乘客信息
            data = {
                'pageIndex': 1,
                'pageSize': 32
            }
            while True:
                resp = self.session.post(self.url_query, headers=self.headers_query, data=data)
                print(resp.content)
                content = loads(resp.content)
                if not content['status']:
                    break
                datas = content['data']['datas']
                # 无数据
                if not datas:
                    break
                for p in datas:
                    passenger = Passenger()
                    passenger.loads(p)
                    passengers.append(passenger)
                # 判断查询结果是否完毕，根据分页大小和查询结果数判断
                if len(datas) < data['pageSize']:
                    break
                data['pageIndex'] += data['pageSize']
            self.data = passengers
        except Exception as e:
            mp('获取乘客信息失败, {0}->{1}'.format(Exception, e))


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
