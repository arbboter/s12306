# -*- coding: utf-8 -*-
import json
import requests
import datetime


def main():
    """
    测试代码
    :return:
    """
    import prettytable

    # 获取票信息
    train_date = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    para = LeftTicketDTO(from_station='GZQ', to_station='SZQ', train_date=train_date)
    trains = get_trains(para)
    if not trains:
        print('未找到符合条件的车次信息')
        return

    # 获取车站信息
    from station import station_name
    stations = station_name.stations()

    # 组装信息
    tab = prettytable.PrettyTable()
    # 标题头
    tab.field_names = trains[0].key_info().keys()
    # 组装车次信息
    for t in trains:
        tab.add_row(t.key_info(stations).values())
    # 表格显示车次信息
    mp(tab)


class Train:
    """
    车次信息
    """
    def __init__(self, item):
        """
        使用列表顺序初始化火车信息
        :param item: 12306火车信息列表
        :return:
        """
        # self.field_0 = item[0]
        # 状态
        self.status = item[1]
        # 车票号
        self.train_no = item[2]
        # 车次
        self.station_train_code = item[3]
        # 起始站代号
        self.start_station_code = item[4]
        # 终点站代号
        self.end_station_code = item[5]
        # 出发站代号
        self.from_station_code = item[6]
        # 到达站代号
        self.to_station_code = item[7]
        # 出发时间
        self.start_time = item[8]
        # 到达时间
        self.arrive_time = item[9]
        # 运行时长
        self.run_time = item[10]
        # 是否可买
        self.can_buy = item[11]
        self.yp_info = item[12]
        # 出发日期
        self.start_train_date = item[13]
        self.train_seat_feature = item[14]
        self.location_code = item[15]
        self.from_station_no = item[16]
        self.to_station_no = item[17]
        self.is_support_card = item[18]
        self.controlled_train_flag = item[19]
        self.gg_num = item[20]
        self.gr_num = item[21]
        self.qt_num = item[22]
        # 软卧
        self.rw_num = item[23]
        # 软座
        self.rz_num = item[24]
        self.tz_num = item[25]
        # 无座
        self.wz_num = item[26]
        self.yb_num = item[27]
        # 硬卧
        self.yw_num = item[28]
        self.yz_num = item[29]
        # 二等座
        self.edz_num = item[30]
        # 一等座
        self.ydz_num = item[31]
        # 商务特等座
        self.swz_num = item[32]
        # 动卧
        self.dw_num = item[33]
        self.yp_ex = item[34]
        self.seat_types = item[35]
        self.exchange_train_flag = item[36]

    def key_info(self, stations=None):
        """
        获取车次的关键信息
        :return:
        """
        # 起始站点信息转换
        start_station = self.start_station_code
        end_station = self.end_station_code
        from_station = self.from_station_code
        to_station = self.to_station_code
        if stations:
            sc = stations.code
            start_station = sc.get(start_station)[0].name if start_station in sc else start_station
            end_station = sc.get(end_station)[0].name if end_station in sc else end_station
            from_station = sc.get(from_station)[0].name if from_station in sc else from_station
            to_station = sc.get(to_station)[0].name if to_station in sc else to_station
        return {
            '状态': self.status,
            '车次': self.station_train_code,
            '起始站': start_station,
            '终点站': end_station,
            '出发站': from_station,
            '到达站': to_station,
            '出发时间': self.start_time,
            '到达时间': self.arrive_time,
            '运行时长': self.run_time,
            '是否可买': self.can_buy,
            '出发日期': self.start_train_date,
            '软卧': self.rw_num,
            '软座': self.rz_num,
            '无座': self.wz_num,
            '硬卧': self.yw_num,
            '二等座': self.edz_num,
            '一等座': self.ydz_num,
            '商务特等座': self.swz_num,
            '动卧': self.dw_num
        }


class LeftTicketDTO:
    """
    查询余票参数信息
    """
    def __init__(self, train_date=datetime.date.today().strftime('%Y-%m-%d'), from_station='SZQ',
                 to_station='GZQ', purpose_codes='ADULT'):
        self.train_date = train_date
        self.from_station = from_station
        self.to_station = to_station
        self.purpose_codes = purpose_codes

    def encode_url_para(self):
        paras = ['train_date=' + self.train_date,
                 'from_station=' + self.from_station,
                 'to_station=' + self.to_station]
        p = '&'.join(['leftTicketDTO.' + v for v in paras])
        return p + '&purpose_codes=' + self.purpose_codes


def get_trains(dto):
    """
    获取余票信息
    :param dto:
    :return:
    """
    # 余票查询链接地址可能会变，其中结尾处的Z可能会被替换为[A-Z]，注意！！！
    url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ'
    url = url + '?' + dto.encode_url_para()
    # 请求头
    hds = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/74.0.3729.157 Safari/537.36',
        'Cookie': 'JSESSIONID=F8909A46584B13B74DE18535CC9DFE4;'
    }
    try:
        trains = []
        mp('正在查询余票信息:{0}'.format(url))
        # 访问请求链接
        rsp = requests.get(url, headers=hds)
        text = json.loads(rsp.content.decode())

        # 检查返回码
        if text['httpstatus'] != 200:
            mp('获取余票信息异常,{0}'.format(text))
            return

        # 获取想要的数据
        result = text['data']['result']
        mp('共获取到{0}趟车次信息：'.format(len(result)))
        for v in result:
            item = [f for f in v.split('|')]
            t = Train(item)
            trains.append(t)
    except Exception as e:
        mp('获取数据异常, {0} -> {1}'.format(Exception, e))
    return trains


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
