# -*- coding: utf-8 -*-

import os
import re
import time
import jieba
import codecs
import argparse

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATA_FOLDER = r'data'
DEFAULT_FIN = os.path.join(DATA_FOLDER, 'poem.txt')
DEFAULT_FOUT = os.path.join(DATA_FOLDER, 'collocations.txt')
reg_sep = re.compile('([^\u4e00-\u9fa5]+)')

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
                score.append((word_pair, self.bigram_fd[word_pair] / self.N))
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
    finder = BigramCollocationFinder()
    title_flag = 0
    fd = codecs.open(fin, 'r', 'utf-8')
    for line in fd:
        line = line.strip()
        title_flag = 1 - title_flag
        if title_flag == 1:
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
                    finder.add_word_pair((sentences[i][j], sentences[i + 1][j]))
                else:
                    break
    fd.close()
    print('Read data done.')
    return finder


def write_collocations(fout, finder):
    measure = 'frequency'
    collocations = finder.score_bigram(measure)
    collocations = sorted(collocations, key=lambda x:x[1], reverse=True)
    fw = codecs.open(fout, 'w', 'utf-8')
    for (w1, w2), score in collocations:
        fw.write('{} {} {} {}\n'.format(w1, w2, score, finder.bigram_fd[(w1, w2)]))
    fw.close()
    print('Write collocations done.')


def set_arguments():
    parser = argparse.ArgumentParser(description='Get collocations')
    parser.add_argument('--fin', type=str, default=DEFAULT_FIN,
                        help='Input file path, default is {}'.format(DEFAULT_FIN))
    parser.add_argument('--fout', type=str, default=DEFAULT_FOUT,
                        help='Output file path, default is {}'.format(DEFAULT_FOUT))
    return parser


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START'.format(time.strftime(TIME_FORMAT)))

    finder = read_data(cmd_args.fin)
    write_collocations(cmd_args.fout, finder)

    print('{} STOP'.format(time.strftime(TIME_FORMAT)))