# -*- coding: utf-8 -*-

import os
import re
import codecs

DATA_FOLDER = r'.\data'
reg_noisy = re.compile('(<[^\u4e00-\u9fa5]*>)')
reg_note = re.compile('(（.*)')
reg_note2 = re.compile('(.*）)')

if __name__ == '__main__':
    input_file_name = os.path.join(DATA_FOLDER, '唐诗语料库.txt')
    output_file_name = os.path.join(DATA_FOLDER, 'poem.txt')
    fd = codecs.open(input_file_name, 'r', 'utf-8')
    fw = codecs.open(output_file_name, 'w', 'utf-8')
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