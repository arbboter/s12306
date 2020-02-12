#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def parse_by_dict(text, udim=';', fdim='='):
    """
    将字符串解析为字典格式
    :param text: 待解析字符串
    :param udim: 单元间隔符,默认为【;】
    :param fdim: 字段间隔符,默认为【=】
    :return: 解析后的字典数据
    """
    rd = {}
    item = [v for v in text.split(udim)]
    for v in item:
        field = [u for u in v.split(fdim)]
        if len(field) != 2:
            continue
        rd[field[0]] = field[1]
    return rd
