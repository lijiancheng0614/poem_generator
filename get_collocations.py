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
DEFAULT_FCOLLOCATIONS_V = os.path.join(DATA_FOLDER, 'collocations_v')
DEFAULT_FCOLLOCATIONS_H = os.path.join(DATA_FOLDER, 'collocations_h')
reg_sep = re.compile(u'([^\u4e00-\u9fa5]+)')

class BigramCollocationFinder():
    def __init__(self):
        # self.unigram_fd = dict()
        self.bigram_fd = dict()
        self.N = 0
    def add_word_pair(self, word_pair):
        self.N += 1
        # for i in range(2):
        #     self.unigram_fd[word_pair[i]] = self.unigram_fd.get(word_pair[i], 0) + 1
        self.bigram_fd[word_pair] = self.bigram_fd.get(word_pair, 0) + 1
    def score_bigram(self, measure):
        score = []
        if measure == 'frequency':
            for word_pair in self.bigram_fd:
                score.append((word_pair, float(self.bigram_fd[word_pair]) / self.N))
        # elif measure == 'Pearson\'s chi-square':
        #     for word_pair in self.bigram_fd:
        #         O11 = self.bigram_fd[word_pair]
        #         O12 = self.unigram_fd[word_pair[0]] - O11
        #         O21 = self.unigram_fd[word_pair[1]] - O11
        #         O22 = self.N - O11 - O12 - O21
        #         X2 = self.N * (O11 * O22 - O12 * O21) ** 2 / (O11 + O12) / (O11 + O21) / (O12 + O22) / (O21 + O22)
        #         score.append((word_pair, X2))
        else:
            print('Unknown measure!')
        return score


def read_data(fin):
    finder_v = BigramCollocationFinder()
    finder_h = BigramCollocationFinder()
    title_flag = False
    fd = codecs.open(fin, 'r', 'utf-8')
    for line in fd:
        line = line.strip()
        title_flag = not title_flag
        if title_flag:
            continue
        sentences = reg_sep.sub(' ', line).split()
        if len(sentences) % 2 > 0:
            continue
        sentences = [list(jieba.cut(i)) for i in sentences]
        for i in range(0, len(sentences), 2):
            if len(sentences[i]) != len(sentences[i + 1]):
                continue
            for j in range(len(sentences[i])):
                if len(sentences[i][j]) == len(sentences[i + 1][j]):
                    finder_v.add_word_pair((sentences[i][j], sentences[i + 1][j]))
                else:
                    break
                if j + 1 < len(sentences[i]):
                    finder_h.add_word_pair((sentences[i][j], sentences[i][j + 1]))
                    finder_h.add_word_pair((sentences[i + 1][j], sentences[i + 1][j + 1]))
    fd.close()
    print('Read data done.')
    return (finder_v, finder_h)


def get_collocations_from_finder(finder):
    measure = 'frequency'
    collocations = finder.score_bigram(measure)
    collocations = sorted(collocations, key=lambda x:x[1], reverse=True)
    collocations_dict = dict()
    for (w1, w2), score in collocations:
        l = len(w2)
        if w1 in collocations_dict:
            if l in collocations_dict[w1]:
                collocations_dict[w1][l].append((score, w2))
            else:
                collocations_dict[w1][l] = [(score, w2)]
        else:
            collocations_dict[w1] = {l : [(score, w2)]}
    return collocations_dict
    # return ['{} {} {} {}'.format(w1, w2, score, finder.bigram_fd[(w1, w2)])\
    #     for (w1, w2), score in collocations]

def write_collocations(fout, collocations):
    fw = codecs.open(fout, 'wb')
    pickle.dump(collocations, fw)
    fw.close()
    print('Write collocations done.')


def set_arguments():
    parser = argparse.ArgumentParser(description='Get collocations')
    parser.add_argument('--fin', type=unicode, default=DEFAULT_FIN,
                        help=u'Input file path, default is {}'.format(DEFAULT_FIN))
    parser.add_argument('--fcollocations_v', type=unicode, default=DEFAULT_FCOLLOCATIONS_V,
                        help=u'Output collocations_v file path, default is {}'.format(DEFAULT_FCOLLOCATIONS_V))
    parser.add_argument('--fcollocations_h', type=unicode, default=DEFAULT_FCOLLOCATIONS_H,
                        help=u'Output collocations_h file path, default is {}'.format(DEFAULT_FCOLLOCATIONS_H))
    return parser


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START'.format(time.strftime(TIME_FORMAT)))

    (finder_v, finder_h) = read_data(cmd_args.fin)
    collocations_v = get_collocations_from_finder(finder_v)
    collocations_h = get_collocations_from_finder(finder_h)
    write_collocations(cmd_args.fcollocations_v, collocations_v)
    write_collocations(cmd_args.fcollocations_h, collocations_h)

    print('{} STOP'.format(time.strftime(TIME_FORMAT)))