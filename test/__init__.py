#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def main():
    import requests
    s = requests.Session()
    s.get('https://kyfw.12306.cn/otn/')
    print(s.cookies)


if __name__ == '__main__':
    main()
