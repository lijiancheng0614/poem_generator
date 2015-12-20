# -*- coding: utf-8 -*-

import os
import math
import time
import jieba
import codecs
import pickle
import random
import argparse

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
BASE_FOLDER = os.path.abspath(os.path.dirname(__file__)).decode('gb2312')
DATA_FOLDER = os.path.join(BASE_FOLDER, 'data')
DEFAULT_FCOLLOCATIONS_V = os.path.join(DATA_FOLDER, 'collocations_v')
DEFAULT_FCOLLOCATIONS_H = os.path.join(DATA_FOLDER, 'collocations_h')
DEFAULT_FWORDS = os.path.join(DATA_FOLDER, 'words')
DEFAULT_FTOPIC_WORDS = os.path.join(DATA_FOLDER, 'topic_words')
DEFAULT_FSTART_WORDS = os.path.join(DATA_FOLDER, 'start_words.txt')
LOG_DELTA = 20

def read_dump(fin):
    fd = codecs.open(fin, 'rb')
    data = pickle.load(fd)
    fd.close()
    print(u'Read from {} done.'.format(fin))
    return data


def read_txt(fin):
    fd = codecs.open(fin, 'r', 'utf-8')
    data = [i.strip() for i in fd]
    fd.close()
    print(u'Read from {} done.'.format(fin))
    return data


def generate_first_sentence_brute_force(start_word, sentence_len, topic_vector, words):
    sentence = [start_word]
    l = len(start_word)
    avg = 1e-7
    while l < sentence_len:
        w2 = random.choice(words)
        if len(w2) > 2:
            continue
        if topic_vector[words.index(w2)] < avg:
            continue
        sentence.append(w2)
        l += len(w2)
    return sentence


# topic_words max: 3.1424917513724737
# topic_words min: 0.0
def generate_first_sentence(start_word, sentence_len, topic_vector, words, collocations_h):
    f = [dict() for i in range(sentence_len + 1)]
    p = [dict() for i in range(sentence_len + 1)]
    start_len = len(start_word)
    f[start_len][start_word] = topic_vector[words.index(start_word)] if start_word in words else 0
    p[start_len][start_word] = ''
    for i in range(start_len, sentence_len):
        for j in f[i]:
            if j not in collocations_h:
                continue
            topic_score = topic_vector[words.index(j)] if j in words else 0
            for k in collocations_h[j]:
                if i + k <= sentence_len:
                    for test_count in range(2):
                        (score, w2) = random.choice(collocations_h[j][k])
                        temp = f[i][j] + math.log(score) + LOG_DELTA + topic_score
                        if w2 not in f[i + k] or temp > f[i + k][w2]:
                            f[i + k][w2] = temp
                            p[i + k][w2] = j
    ans = 0
    last_word = ''
    if not f[sentence_len]:
        return generate_first_sentence_brute_force(start_word, sentence_len, topic_vector, words)
    for j in f[sentence_len]:
        if f[sentence_len][j] > ans:
            ans = f[sentence_len][j]
            last_word = j
    if ans == 0:
        return generate_first_sentence_brute_force(start_word, sentence_len, topic_vector, words)
    sentence = []
    i = sentence_len
    while i > 0:
        sentence.append(last_word)
        last_word, i = p[i][last_word], i - len(last_word)
    return sentence[::-1]


def generate_next_sentence_brute_force(pre_sentence, topic_vector, words, collocations_v):
    sentence = []
    avg = 1e-7
    for prei in pre_sentence:
        k = len(prei)
        w2 = ''
        if prei in collocations_v and k in collocations_v[prei]:
            (score, w2) = random.choice(collocations_v[prei][k])
        else:
            while True:
                w2 = random.choice(words)
                if len(w2) != k:
                    continue
                if topic_vector[words.index(w2)] < avg:
                    continue
                break
        sentence.append(w2)
    return sentence


def generate_next_sentence(pre_sentence, topic_vector, words, collocations_h, collocations_v):
    word_count = len(pre_sentence)
    f = [dict() for i in range(word_count)]
    p = [dict() for i in range(word_count)]
    prei = pre_sentence[0]
    k = len(prei)
    if prei not in collocations_v or k not in collocations_v[prei]:
        return generate_next_sentence_brute_force(pre_sentence, topic_vector, words, collocations_v)
    for test_count in range(2):
        (score2, w2) = random.choice(collocations_v[prei][k])
        topic_score = topic_vector[words.index(w2)] if w2 in words else 0
        temp = math.log(score2) + LOG_DELTA + topic_score
        if w2 not in f[0] or temp > f[0][w2]:
            f[0][w2] = temp
            p[0][w2] = ''
    for i in range(word_count - 1):
        for j in f[i]:
            if j not in collocations_h:
                continue
            topic_score = topic_vector[words.index(j)] if j in words else 0
            prei = pre_sentence[i + 1]
            k = len(prei)
            if k not in collocations_h[j]:
                continue
            for test_count in range(3):
                (score, w2) = random.choice(collocations_h[j][k])
                # score2 = 1e-8
                # if prei in collocations_v:
                #     for (temp, tempw) in collocations_v[prei][k]:
                #         if tempw == w2:
                #             score2 = temp
                #             break
                temp = f[i][j] + math.log(score) * 2 + LOG_DELTA + topic_score
                if w2 not in f[i + 1] or temp > f[i + 1][w2]:
                    f[i + 1][w2] = temp
                    p[i + 1][w2] = j
    ans = 0
    last_word = ''
    word_count -= 1
    if not f[word_count]:
        return generate_next_sentence_brute_force(pre_sentence, topic_vector, words, collocations_v)
    for j in f[word_count]:
        if f[word_count][j] > ans:
            ans = f[word_count][j]
            last_word = j
    if ans == 0:
        return generate_next_sentence_brute_force(pre_sentence, topic_vector, words, collocations_v)
    sentence = []
    i = word_count
    while i >= 0:
        sentence.append(last_word)
        last_word = p[i][last_word]
        i -= 1
    return sentence[::-1]


def get_start_word(pre_start_word, topic_vector, words, collocations_v):
    avg = 1e-7
    while True:
        (score, start_word) = random.choice(collocations_v[pre_start_word][len(pre_start_word)])
        if len(start_word) != len(pre_start_word):
            continue
        if start_word in words and topic_vector[words.index(start_word)] < avg:
            continue
        break
    return start_word


def generate_poem(topic_id, sentence_len, sentences_count, start_word,\
    collocations_v, collocations_h, words, topic_vector, start_words):
    poem = [generate_first_sentence(start_word, sentence_len, topic_vector, words, collocations_h)]
    poem.append(generate_next_sentence(poem[0], topic_vector, words, collocations_h, collocations_v))
    sentences_count -= 2
    while sentences_count > 1:
        start_word = get_start_word(start_word, topic_vector, words, collocations_v)
        first_sentence = generate_first_sentence(start_word, sentence_len, topic_vector, words, collocations_h)
        poem.append(first_sentence)
        poem.append(generate_next_sentence(first_sentence, topic_vector, words, collocations_h, collocations_v))
        sentences_count -= 2
    return [''.join(i) for i in poem]


def generate_poem_with_poem4(poem, collocations_v, collocations_h, words, topic_vector, start_words):
    if poem[0] and poem[1] and poem[2] and poem[3]:
        return poem
    sentence_len = len(poem[0])
    for i in range(4):
        if poem[i]:
            poem[i] = list(jieba.cut(poem[i]))
    if poem[0] and poem[1] and poem[2]:
        poem[3] = generate_next_sentence(poem[2], topic_vector, words, collocations_h, collocations_v)
    elif poem[0]:
        if not poem[1]:
            poem[1] = generate_next_sentence(poem[0], topic_vector, words, collocations_h, collocations_v)
        avg = 1e-7
        pre_start_word = poem[0][0]
        while True:
            (score, start_word) = random.choice(collocations_v[pre_start_word][len(pre_start_word)])
            if len(start_word) != len(pre_start_word):
                continue
            if start_word in words and topic_vector[words.index(start_word)] < avg:
                continue
            break
        start_word = get_start_word(start_word, topic_vector, words, collocations_v)
        first_sentence = generate_first_sentence(start_word, sentence_len, topic_vector, words, collocations_h)
        poem[2] = first_sentence
        poem[3] = generate_next_sentence(first_sentence, topic_vector, words, collocations_h, collocations_v)
    return [''.join(i) for i in poem]

def set_arguments():
    parser = argparse.ArgumentParser(description='Generate poem')
    parser.add_argument('--fcollocations_v', type=unicode, default=DEFAULT_FCOLLOCATIONS_V,
                        help=u'Collocations_v file path, default is {}'.format(DEFAULT_FCOLLOCATIONS_V))
    parser.add_argument('--fcollocations_h', type=unicode, default=DEFAULT_FCOLLOCATIONS_H,
                        help=u'Collocations_h file path, default is {}'.format(DEFAULT_FCOLLOCATIONS_H))
    parser.add_argument('--fwords', type=unicode, default=DEFAULT_FWORDS,
                        help=u'Words file path, default is {}'.format(DEFAULT_FWORDS))
    parser.add_argument('--ftopic_words', type=unicode, default=DEFAULT_FTOPIC_WORDS,
                        help=u'Topic_words file path, default is {}'.format(DEFAULT_FTOPIC_WORDS))
    parser.add_argument('--fstart_words', type=unicode, default=DEFAULT_FSTART_WORDS,
                        help=u'Start_words file path, default is {}'.format(DEFAULT_FSTART_WORDS))
    return parser


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START'.format(time.strftime(TIME_FORMAT)))

    collocations_v = read_dump(cmd_args.fcollocations_v)
    collocations_h = read_dump(cmd_args.fcollocations_h)
    words = read_dump(cmd_args.fwords)
    topic_words = read_dump(cmd_args.ftopic_words)
    start_words = read_txt(cmd_args.fstart_words)
    topic_id = 8
    sentence_len = 7
    sentences_count = 4
    start_word = random.choice(start_words)
    poem = generate_poem(topic_id, sentence_len, sentences_count, start_word,\
        collocations_v, collocations_h, words, topic_words[topic_id], start_words)
    print(poem)

    print('{} STOP'.format(time.strftime(TIME_FORMAT)))