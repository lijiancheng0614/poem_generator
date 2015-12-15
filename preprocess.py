# -*- coding: utf-8 -*-

import os
import re
import time
import codecs
import argparse

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATA_FOLDER = r'data'
DEFAULT_FIN = os.path.join(DATA_FOLDER, '唐诗语料库.txt')
DEFAULT_FOUT = os.path.join(DATA_FOLDER, 'poem.txt')
reg_noisy = re.compile('(<[^\u4e00-\u9fa5]*>)')
reg_note = re.compile('(（.*)')
reg_note2 = re.compile('(.*）)')

def set_arguments():
    parser = argparse.ArgumentParser(description='Pre process')
    parser.add_argument('--fin', type=str, default=DEFAULT_FIN,
                        help='Input file path, default is {}'.format(DEFAULT_FIN))
    parser.add_argument('--fout', type=str, default=DEFAULT_FOUT,
                        help='Output file path, default is {}'.format(DEFAULT_FOUT))
    return parser


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START'.format(time.strftime(TIME_FORMAT)))

    fd = codecs.open(cmd_args.fin, 'r', 'utf-8')
    fw = codecs.open(cmd_args.fout, 'w', 'utf-8')
    reg = re.compile('〖(.*)〗')
    start_flag = False
    for line in fd:
        line = line.strip()
        if not line or '《全唐诗》' in line or '<http'  in line:
            continue
        elif '〖' in line and '〗' in line:
            if start_flag:
                fw.write('\n')
            start_flag = True
            g = reg.search(line)
            if g:
                fw.write(g.group(1))
                fw.write('\n')
            else:
                # noisy data
                print(line)
        else:
            line = reg_noisy.sub('', line)
            line = line.replace(' .', '')
            fw.write(line)

    fd.close()
    fw.close()

    print('{} STOP'.format(time.strftime(TIME_FORMAT)))