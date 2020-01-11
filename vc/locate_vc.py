#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
from keras import models

import pretreatment
from mlearn_for_image import preprocess_input


# 全局变量
g_text_model = None
g_image_model = None
g_option_texts = []
g_init = False


def main():
    """
    测试代码，读取本地文件夹下的数据
    依赖数据模型资源文件:model.h5和12306.image.model.h5
    依赖其他文件:pretreatment.py 和 mlearn_for_image.py
    :return:
    """
    import pathlib
    # 创建验证码图片目录
    vc_path = pathlib.Path(pretreatment.PATH)
    vc_path.mkdir(exist_ok=True)

    # 下载图片
    # [pretreatment.download_image() for _ in range(5)]

    # 验证码识别结果
    for file in vc_path.rglob("*.jpg"):
        abs_file = os.path.abspath(file)
        mp('[{0}]识别结果位置:{1} \n{2}'.format(file, locate_vc(abs_file), '-'*64))


def get_text(img, offset=0):
    """
    获取图片文本信息
    :param img: 验证码图片句柄，cv2.imread返回值
    :param offset:
    :return: 图片处理后的文本信息
    """
    text = pretreatment.get_text(img, offset)
    text = cv2.cvtColor(text, cv2.COLOR_BGR2GRAY)
    text = text / 255.0
    h, w = text.shape
    text.shape = (1, h, w, 1)
    return text


def init():
    """
    初始化，预加载模型
    :return:
    """
    global g_text_model
    global g_image_model
    global g_option_texts
    global g_init

    if g_init:
        return True
    try:
        # 调低日志级别，屏蔽tensorflow警告(强迫症)
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        # 额外参数compile=False屏蔽警告
        g_text_model = models.load_model('model.h5', compile=False)
        g_image_model = models.load_model('12306.image.model.h5', compile=False)
        with open('texts.txt', encoding='utf-8') as fd:
            g_option_texts = [text.rstrip('\n') for text in fd]
        g_init = True
    except Exception as e:
        mp('资源初始化失败 {0} -> {1}'.format(Exception, e))
    return False


def locate_vc(vc_file):
    """
    12306验证码文件识别，获取识别结果
    :param vc_file: 12306图片验证码
    :return:识别结果索引列表
    """
    try:
        loc = []
        # 初始化
        init()

        # 读取文件信息
        img, text_info, imgs_info = get_vc_info(vc_file)

        # 标题文字识别
        texts = guess_text(img, text_info)
        mp('问题关键字:' + ','.join(texts))

        # 验证码内容识别
        image_name = guess_image(imgs_info)
        mp('图片识别结果:' + ','.join(image_name))

        for i, name in enumerate(image_name):
            if name in texts:
                loc.append(i)
    except Exception as e:
        mp('验证码识别异常：{0} -> {1}'.format(Exception, e))
    return loc


def get_vc_info(vc_file):
    """
    根据12306的图片信息，解析出文字和图片信息
    :param vc_file:
    :return: [图片句柄,文字信息,图片信息]
    """
    try:
        img = cv2.imread(vc_file)
        text = get_text(img)
        imgs = np.array(list(pretreatment.i_get_imgs(img)))
        imgs = preprocess_input(imgs)
    except Exception as e:
        mp('获取验证码图片信息异常 {0} -> {1}'.format(Exception, e))
    return img, text, imgs


def guess_text(img, itxt):
    """
    文字识别
    :param img: 验证码图片
    :param itxt: 待识别的文字信息
    :return: 识别结果文字列表
    """
    otxt = []
    # 识别文字
    label = g_text_model.predict(itxt)
    label = label.argmax()
    text = g_option_texts[label]
    otxt.append(text)

    # 获取下一个词
    # 根据第一个词的长度来定位第二个词的位置
    if len(text) == 1:
        offset = 27
    elif len(text) == 2:
        offset = 47
    else:
        offset = 60
    text = get_text(img, offset=offset)
    if text.mean() < 0.95:
        label = g_text_model.predict(text)
        label = label.argmax()
        text = g_text_model[label]
        otxt.append(text)
    return otxt


def guess_image(imgs):
    """
    图片验证码识别
    :param imgs:
    :return: 图片识别结果名称列表
    """
    img_name = []
    labels = g_image_model.predict(imgs)
    labels = labels.argmax(axis=1)
    for pos, label in enumerate(labels):
        # print(pos // 4, pos % 4, g_option_texts[label])
        img_name.append(g_option_texts[label])
    return img_name


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
