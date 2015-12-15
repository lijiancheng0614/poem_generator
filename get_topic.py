# -*- coding: utf-8 -*-

import os
import re
import time
import jieba
import jieba.analyse
import codecs
import argparse
from sklearn.cluster import KMeans

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATA_FOLDER = r'data'
DEFAULT_FIN = os.path.join(DATA_FOLDER, 'poem.txt')
DEFAULT_FOUT = os.path.join(DATA_FOLDER, 'topics.txt')
DEFAULT_FOUT2 = os.path.join(DATA_FOLDER, 'word_topic.txt')
DEFAULT_N_CLUSTERS = 10
DEFAULT_N_CANDIDATE = 20
reg_sep = re.compile('([^\u4e00-\u9fa5]+)')

def read_data(fin):
    tags_list = list()
    poem_words = list()
    title_flag = 0
    title = ''
    fd = codecs.open(fin, 'r', 'utf-8')
    for line in fd:
        line = line.strip()
        title_flag = 1 - title_flag
        if title_flag == 1:
            title = line
        else:
            sentences = reg_sep.sub(' ', line).split()
            words = [list(jieba.cut(i)) for i in sentences]
            poem_words.append(words)
            tags = jieba.analyse.extract_tags(title + line, topK=3)
            tags_list.append(tags)
    fd.close()
    print('Read data done.')
    return (tags_list, poem_words)

def write_topics(fout, fout2, tags_list, poem_words, N_CLUSTERS, N_CANDIDATE):
    tag_dict = dict()
    for tags in tags_list:
        for t in tags:
            tag_dict[t] = tag_dict.get(t, 0) + 1
    tag_keys = list()
    for k, v in tag_dict.items():
        if v > 1:
            tag_keys.append(k)
    print(len(tag_keys))
    for i in range(len(tags_list)):
        tags_list[i] = [1 if j in tags_list[i] else 0 for j in tag_keys]
    est = KMeans(n_clusters=N_CLUSTERS)
    est.fit(tags_list)
    clusters = [[] for i in range(N_CLUSTERS)]
    for i in range(len(est.labels_)):
        clusters[est.labels_[i]].append(i)
    for i in range(N_CLUSTERS):
        clusters[i] = sorted(clusters[i], key=lambda x:tag_dict[tag_keys[x]], reverse=True)[:N_CANDIDATE]
    fw = codecs.open(fout, 'w', 'utf-8')
    for i in clusters:
        fw.write(' '.join(i) + '\n')
    fw.close()
    print('Write topics done.')
    word_topic = dict()
    for i in range(len(poem_words)):
        for w in poem_words[i]:
            if w not in word_topic:
                word_topic[w] = [0 for t in range(N_CLUSTERS)]
            word_topic[w][est.labels_[i]] += 1
    fw = codecs.open(fout2, 'w', 'utf-8')
    for k, v in word_topic.items():
        fw.write(k + ' ' + ' '.join(v) + '\n')
    fw.close()
    print('Write word_topic done.')


def set_arguments():
    parser = argparse.ArgumentParser(description='Get topics')
    parser.add_argument('--fin', type=str, default=DEFAULT_FIN,
                        help='Input file path, default is {}'.format(DEFAULT_FIN))
    parser.add_argument('--fout', type=str, default=DEFAULT_FOUT,
                        help='Output file path, default is {}'.format(DEFAULT_FOUT))
    parser.add_argument('--fout2', type=str, default=DEFAULT_FOUT2,
                        help='Output file2 path, default is {}'.format(DEFAULT_FOUT2))
    parser.add_argument('--n_clusters', type=int, default=DEFAULT_N_CLUSTERS,
                        help='Clusters count, default is {}'.format(DEFAULT_N_CLUSTERS))
    parser.add_argument('--n_candidate', type=int, default=DEFAULT_N_CANDIDATE,
                        help='Clusters size, default is {}'.format(DEFAULT_N_CANDIDATE))
    return parser


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START'.format(time.strftime(TIME_FORMAT)))

    (tags_list, poem_words) = read_data(cmd_args.fin)
    write_topics(cmd_args.fout, cmd_args.fout2, tags_list, poem_words, cmd_args.n_clusters, cmd_args.n_candidate)

    print('{} STOP'.format(time.strftime(TIME_FORMAT)))