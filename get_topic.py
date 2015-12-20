# -*- coding: utf-8 -*-

import os
import re
import time
import jieba
import codecs
import pickle
import argparse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn import decomposition

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
BASE_FOLDER = os.path.abspath(os.path.dirname(__file__)).decode('gb2312')
DATA_FOLDER = os.path.join(BASE_FOLDER, 'data')
DEFAULT_FIN = os.path.join(DATA_FOLDER, 'poem.txt')
DEFAULT_FTOPICS = os.path.join(DATA_FOLDER, 'topics.txt')
DEFAULT_FWORDS = os.path.join(DATA_FOLDER, 'words')
DEFAULT_FTOPIC_WORDS = os.path.join(DATA_FOLDER, 'topic_words')
DEFAULT_N_TOPIC = 10
DEFAULT_N_TOPIC_WORDS = 20
reg_sep = re.compile(u'([^\u4e00-\u9fa5]+)')

n_topic = 10
n_topic_words = 20

count_vect = CountVectorizer()

def read_data(fin):
    poem_words = list()
    title_flag = False
    title = ''
    fd = codecs.open(fin, 'r', 'utf-8')
    for line in fd:
        line = line.strip()
        line = reg_sep.sub(' ', line)
        title_flag = not title_flag
        if title_flag:
            title = line
        else:
            words = ' '.join(jieba.cut(title + line))
            poem_words.append(words)
    fd.close()
    print('Read data done.')
    return poem_words


def write_topics(ftopics, fwords, ftopics_words, poem_words, n_topic, n_topic_words):
    count_matrix = count_vect.fit_transform(poem_words)
    tfidf = TfidfTransformer().fit_transform(count_matrix)
    nmf = decomposition.NMF(n_components=n_topic).fit(tfidf)
    feature_names = count_vect.get_feature_names()
    fw = codecs.open(ftopics, 'w', 'utf-8')
    for topic in nmf.components_:
        fw.write(' '.join([feature_names[i] for i in topic.argsort()[:-n_topic_words - 1:-1]]) + '\n')
    fw.close()
    print('Write topics done.')
    fw = codecs.open(fwords, 'wb')
    pickle.dump(feature_names, fw)
    fw.close()
    print('Write words done.')
    fw = codecs.open(ftopics_words, 'wb')
    pickle.dump(nmf.components_, fw)
    fw.close()
    print('Write topic_words done.')


def set_arguments():
    parser = argparse.ArgumentParser(description='Get topics')
    parser.add_argument('--fin', type=unicode, default=DEFAULT_FIN,
                        help=u'Input file path, default is {}'.format(DEFAULT_FIN))
    parser.add_argument('--ftopics', type=unicode, default=DEFAULT_FTOPICS,
                        help=u'Output topics file path, default is {}'.format(DEFAULT_FTOPICS))
    parser.add_argument('--ftopics_words', type=unicode, default=DEFAULT_FTOPIC_WORDS,
                        help=u'Output topic_words file path, default is {}'.format(DEFAULT_FTOPIC_WORDS))
    parser.add_argument('--fwords', type=unicode, default=DEFAULT_FWORDS,
                        help=u'Output words file path, default is {}'.format(DEFAULT_FWORDS))
    parser.add_argument('--n_topic', type=int, default=DEFAULT_N_TOPIC,
                        help='Topics count, default is {}'.format(DEFAULT_N_TOPIC))
    parser.add_argument('--n_topic_words', type=int, default=DEFAULT_N_TOPIC_WORDS,
                        help='Topic words count, default is {}'.format(DEFAULT_N_TOPIC_WORDS))
    return parser


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START'.format(time.strftime(TIME_FORMAT)))

    poem_words = read_data(cmd_args.fin)
    write_topics(cmd_args.ftopics, cmd_args.fwords, cmd_args.ftopics_words,\
        poem_words, cmd_args.n_topic, cmd_args.n_topic_words)

    print('{} STOP'.format(time.strftime(TIME_FORMAT)))