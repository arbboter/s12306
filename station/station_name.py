#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import prettytable as pt


def main():
    # 测试获取列表信息
    url_station_name = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
    citys = get_citys(url_station_name)

    # 数据结构测试
    result = Stations(citys)

    # 站点信息表格打印
    mp(str(result))

    # 测试信息搜索
    rst = [
        result.py_simple['bjx'],
        result.name['广州南'],
        result.code['IZQ'],
        result.py_full['chongqingnan'],
        result.py_first['gzd'],
    ]
    for r in rst:
        print('\t'.join([str(v) for v in r]))

    print(result.by_code('SZQ'))


def stations():
    """
    获取车站站点列表信息
    :return:
    """
    url_station_name = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
    citys = get_citys(url_station_name)
    return Stations(citys)


def get_citys(u='https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'):
    """
    功能:获取每个站点信息保存到本地，并返回解析的列表信息(首项为列表头)
    :return: 无
    """
    city_tab = []
    filename = 'station_name.txt'
    try:
        resp = requests.get(u)
        if resp.status_code == 200:
            # 去除结尾的【';】
            valide_text = resp.text.strip().strip(';').strip("'")
            citys = [v for v in valide_text.split('=')[1].split('@') if len(v)>4]
            with open(filename, 'w') as f:
                f.write('\n'.join(citys))
            for c in citys:
                items = c.split('|')
                city_tab.append(items)
        else:
            mp('获取站点信息失败。 Code:{}, Url: {}'.format(resp.status_code, resp.url))
    except Exception as e:
        mp('获取站点信息异常, {0} -> {1}'.format(Exception, e))
    return city_tab


class Stations:
    """
    站点信息，支持按列字段值查找数据
    """
    header = "拼音缩写|站名称|站代码|全拼|站首字母|站顺序号".split('|')

    def __init__(self, station_items=[]):
        # 初始化数据
        self._ori_data = station_items[:]
        self._data = []
        for s in self._ori_data:
            self._data.append(StationInfo(s))

        # 建立索引支持数据查询
        # 注意：查询结果均为列表！！！
        self.py_simple = {}
        self.name = {}
        self.code = {}
        self.py_full = {}
        self.py_first = {}
        self.upd_index()

    def upd_index(self):
        """
        更新索引
        :return:
        """
        for s in self._data:
            self._index_apd(self.py_simple, s.py_simple, s)
            self._index_apd(self.name, s.name, s)
            self._index_apd(self.code, s.code, s)
            self._index_apd(self.py_full, s.py_full, s)
            self._index_apd(self.py_first, s.py_first, s)

    def by_code(self, c):
        """
        根据站代码获取站点信息
        :param c:
        :return:
        """
        r = self.code.get(c)
        return r[0] if r else None

    @staticmethod
    def _index_apd(d, k, v):
        elem = d.get(k)
        if elem:
            elem.append(v)
        else:
            d[k] = [v]

    def __str__(self):
        """
        转为字符串信息
        :return:
        """
        s = ""
        if self._ori_data:
            from prettytable import PrettyTable
            p = PrettyTable()
            p.field_names = self.header
            [p.add_row(v) for v in self._ori_data]
            s = str(p)
        return s


class StationInfo:
    def __init__(self, items=[]):
        """
        从列表初创建站点信息
        :param items: items的字段顺序：拼音缩写 站名称 站代码 全拼 站首字母 站顺序号
        """
        self.py_simple = items[0]
        self.name = items[1]
        self.code = items[2]
        self.py_full = items[3]
        self.py_first = items[4]
        self.sno = items[5]

    def __str__(self):
        items = [self.py_simple, self.name, self.code, self.py_full, self.py_first, self.sno]
        dd = dict(zip(Stations.header, items))
        return repr(dd)


def show_tab(tab):
    """
    使用PrettyTable显示TAB表信息，首项为标题头
    :param tab:首项为标题头TAB表
    :return: 无
    """
    p = pt.PrettyTable()
    if not tab:
        return
    p.field_names = tab[0]
    [p.add_row(v) for v in tab[1:]]
    mp(p)


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
