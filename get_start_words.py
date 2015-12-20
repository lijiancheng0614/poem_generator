# -*- coding: utf-8 -*-

import os
import re
import time
import jieba
import codecs
import pickle
import argparse

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
BASE_FOLDER = os.path.abspath(os.path.dirname(__file__)).decode('gb2312')
DATA_FOLDER = os.path.join(BASE_FOLDER, 'data')
DEFAULT_FIN = os.path.join(DATA_FOLDER, 'poem.txt')
DEFAULT_FOUT = os.path.join(DATA_FOLDER, 'start_words.txt')

def read_data(fin):
    start_words = dict()
    title_flag = False
    fd = codecs.open(fin, 'r', 'utf-8')
    for line in fd:
        line = line.strip()
        title_flag = not title_flag
        if title_flag or not line:
            continue
        word = list(jieba.cut(line))[0]
        start_words[word] = start_words.get(word, 0) + 1
    fd.close()
    print('Read data done.')
    return start_words


def write_start_words(fout, start_words):
    fw = codecs.open(fout, 'w', 'utf-8')
    for k, v in start_words.items():
        if v > 10 and len(k) > 1:
            fw.write(k + '\n')
    fw.close()
    print('Write start_words done.')


def set_arguments():
    parser = argparse.ArgumentParser(description='Get topics')
    parser.add_argument('--fin', type=unicode, default=DEFAULT_FIN,
                        help=u'Input file path, default is {}'.format(DEFAULT_FIN))
    parser.add_argument('--fout', type=unicode, default=DEFAULT_FOUT,
                        help=u'Output start_words file path, default is {}'.format(DEFAULT_FOUT))
    return parser


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START'.format(time.strftime(TIME_FORMAT)))

    start_words = read_data(cmd_args.fin)
    write_start_words(cmd_args.fout, start_words)

    print('{} STOP'.format(time.strftime(TIME_FORMAT)))

    # count = [0, 14992, 3091, 1161, 614, 401, 254, 179, 103, 88, 79, 52, 49, 50, 41, 20, 23, 19, 15, 16, 13, 6, 12, 12, 6, 6, 7, 2, 7, 2, 3, 2, 3, 0, 4, 2, 4, 3, 2, 0, 0, 1, 3, 3, 1, 2, 1, 2, 2, 2, 1, 0, 2, 0, 2, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 1, 0, 1, 0, 2, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1]
    # 闻道 52
    # 忆 69
    # 十年 55
    # 去年 52
    # 为 63
    # 妾 54
    # 何处 74
    # 曾 74
    # 故人 90
    # 欲 73
    # 少年 69
    # 年 63
    # 长安 83
    # 君不见 65
    # 月 108
    # 谁 67
    # 上 54
    # 吾 75
    # 万里 102
    # 江南 61
    # 我 112
    # 洛阳 55
    # 去 61
    