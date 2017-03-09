from argparse import ArgumentParser

from os import path, makedirs, listdir

from collections import defaultdict

import numpy as np
from nltk import word_tokenize

MIN_CONTENT_WORD_FREQUENCY = 10


def load_questions(in_stream):
    result = set([])
    for line in in_stream:
        result.add(line.strip().lower())
    return result


def build_freq_dictionary(in_questions_set):
    dictionary = defaultdict(lambda: 0)
    for question in in_questions_set:
        for token in word_tokenize(question):
            dictionary[token] += 1
    return dictionary


def filter_dictionary(in_freq_dict):
    frequencies = in_freq_dict.values()
    mean, variance = np.mean(frequencies), np.std(frequencies)
    min_frequency = max(MIN_CONTENT_WORD_FREQUENCY, mean - 2 * variance)
    max_frequency = mean + 2 * variance
    filtered_dictionary = {
        word: frequency
        for word, frequency in in_freq_dict.iteritems()
        if min_frequency <= frequency <= max_frequency
    }
    return filtered_dictionary


def build_argument_parser():
    parser = ArgumentParser()
    parser.add_argument('src_root')
    return parser


def main(in_text_root):
    all_questions = set([])
    for questions_file in listdir(in_text_root):
        with open(path.join(in_text_root, questions_file)) as questions_in:
            questions = load_questions(questions_in)
        all_questions.update(questions)
    freq_dict = build_freq_dictionary(all_questions)
    filtered_dictionary = filter_dictionary(freq_dict)
    filtered_questions = []
    for question in all_questions:
        tokens = word_tokenize(question)
        for token in tokens:
            if token in filtered_dictionary:
                filtered_questions.append(question)
                break 
    return filtered_questions


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()
    for question in main(args.src_root):
        print question
