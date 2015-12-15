# -*- coding: utf-8 -*-

import os
import re
import codecs
import jieba
import jieba.analyse
from sklearn.cluster import KMeans

DATA_FOLDER = r'.\data'
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


# def output_word_dict(word_dict):
#     word_list = sorted(word_dict.keys(), key=lambda x:word_dict[x], reverse=True)
#     with codecs.open(os.path.join(DATA_FOLDER, 'word_dict.txt'), 'w', 'utf-8') as fw:
#         for k in word_list:
#             fw.write('{}\n'.format(k))
#         fw.close()
#     print('Output word_dict done.')


def output_collocations(finder):
    measure = 'frequency'
    collocations = finder.score_bigram(measure)
    collocations = sorted(collocations, key=lambda x:x[1], reverse=True)
    with codecs.open(os.path.join(DATA_FOLDER, 'collocations.txt'), 'w', 'utf-8') as fw:
        for (w1, w2), score in collocations:
            fw.write('{} {} {} {}\n'.format(w1, w2, score, finder.bigram_fd[(w1, w2)]))
        fw.close()
    print('Output collocations done.')


def output_topics(tags_list, poem_words):
    tag_dict = dict()
    for tags in tags_list:
        for t in tags:
            tag_dict[t] = tag_dict.get(t, 0) + 1
    tag_keys = list()
    for k, v in tag_dict.items():
        if v > 1:
            tag_keys.append(k)
    for i in range(len(tags_list)):
        tags_list[i] = [1 if j in tags_list[i] else 0 for j in tag_keys]
    N_CLUSTERS = 10
    est = KMeans(n_clusters=N_CLUSTERS)
    est.fit(tags_list)
    clusters = [[] for i in range(N_CLUSTERS)]
    for i in range(len(est.labels_)):
        clusters[est.labels_[i]].append(i)
    N_CANDIDATE = 20
    for i in range(N_CLUSTERS):
        clusters[i] = sorted(clusters[i], key=lambda x:tag_dict[tag_keys[x]], reverse=True)[:N_CANDIDATE]
    with codecs.open(os.path.join(DATA_FOLDER, 'topics.txt'), 'w', 'utf-8') as fw:
        for i in clusters:
            fw.write(' '.join(i) + '\n')
        fw.close()
    print('Output topics done.')
    word_topic = dict()
    for i in range(len(poem_words)):
        for w in poem_words[i]:
            if w not in word_topic:
                word_topic[w] = [0 for t in range(N_CLUSTERS)]
            word_topic[w][est.labels_[i]] += 1
    with codecs.open(os.path.join(DATA_FOLDER, 'word_topic.txt'), 'w', 'utf-8') as fw:
        for k, v in word_topic.items():
            fw.write(k + ' ' + ' '.join(v) + '\n')
        fw.close()
    print('Output word_topic done.')



if __name__ == '__main__':
    input_file_name = os.path.join(DATA_FOLDER, 'poem.txt')
    tags_list = list()
    poem_words = list()
    finder = BigramCollocationFinder()
    title_flag = 0
    title = ''
    fd = codecs.open(input_file_name, 'r', 'utf-8')
    for line in fd:
        line = line.strip()
        title_flag = 1 - title_flag
        if title_flag == 1:
            title = line
        else:
            sentences = reg_sep.sub(' ', line).split()
            sentences = [list(jieba.cut(i)) for i in sentences]
            if len(sentences) % 2 > 0:
                continue
            tags = jieba.analyse.extract_tags(title + line, topK=3)
            tags_list.append(tags)
            words = []
            for s in sentences:
                for w in s:
                    words.append(w)
            poem_words.append(words)
            for i in range(0, len(sentences), 2):
                if len(sentences[i]) != len(sentences[i + 1]):
                    continue
                for j in range(len(sentences[i])):
                    if len(sentences[i][j]) == len(sentences[i + 1][j]):
                        finder.add_word_pair((sentences[i][j], sentences[i + 1][j]))
                    else:
                        break
    fd.close()
    output_collocations(finder)
    output_topics(tags_list, poem_words)