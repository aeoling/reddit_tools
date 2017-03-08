import json
from os import path, walk, makedirs
import logging
from argparse import ArgumentParser
from codecs import getreader, getwriter

from nltk.tokenize import sent_tokenize

from task_list import add_task, execute_tasks, tasks
from extract_conversations import write_comment_chains, build_comment_chains
from utils import DIALOGUE_SEPARATOR

DEFAULT_TASKS_NUMBER = 64

MIN_UTTERANCE_LENGTH = 3
MAX_UTTERANCE_LENGTH = 30
UTTERANCE_STOP_LIST = ['__content_missing__', '[deleted]']
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def filter_length(input_stream, output_stream):
    for line in input_stream:
        json_line = json.loads(line)
        body = json_line.get('body', '')

        if MIN_UTTERANCE_LENGTH <= len(body.split()) <= MAX_UTTERANCE_LENGTH:
            print >>output_stream, line.strip()


def filter_questions(in_src, in_dst):
    for line in in_src:
        json_line = json.loads(line)
        body = json_line.get('body', '')
        for sentence in sent_tokenize(body):
            if '?' in sentence and MIN_UTTERANCE_LENGTH <= len(sentence.split()) <= MAX_UTTERANCE_LENGTH:
                print >>in_dst, sentence.encode('utf-8')


def filter_callback(in_params):
    input_file, output_file, max_len = in_params
    logger.info('Processing file {}'.format(input_file))
    with open(input_file) as reddit_in, open(output_file, 'w') as reddit_out:
        filter_length(reddit_in, reddit_out)


def filter_questions_callback(in_params):
    input_file, output_file = in_params
    logger.info('Processing file {}'.format(input_file))
    with open(input_file) as reddit_in, open(output_file, 'w') as reddit_out:
        filter_questions(reddit_in, reddit_out)


def chain_callback(in_params):
    input_file, output_file = in_params
    logger.info('Processing file {}'.format(input_file))
    with getreader('utf-8')(open(input_file)) as reddit_in:
        with getwriter('utf-8')(open(output_file, 'w')) as reddit_out:
            comments_tree_root = build_comment_chains(reddit_in)
            write_comment_chains(comments_tree_root, reddit_out)
    logger.info('Done - {}'.format(input_file))


def to_easy_seq2seq_callback(in_params):
    input_file, output_file = in_params
    enc_filename = output_file + '.enc'
    dec_filename = output_file + '.dec'
    logger.info('Processing file {}'.format(input_file))
    with getreader('utf-8')(open(input_file)) as reddit_in:
        with getwriter('utf-8')(open(enc_filename, 'w')) as encoder_out:
            with getwriter('utf-8')(open(dec_filename, 'w')) as decoder_out:
                dialogs = reddit_in.read().split(DIALOGUE_SEPARATOR)
                for dialog in dialogs:
                    utterances = [
                        utterance.partition('\t')[2].strip()
                        for utterance in dialog.strip().split('\n')
                    ]
                    utterances = filter(
                        lambda utterance: utterance not in UTTERANCE_STOP_LIST,
                        utterances
                    )
                    if not len(utterances):
                        continue
                    utterances_tokenized = [
                        utterance.split()
                        for utterance in utterances
                    ]
                    utterance_lengths = map(len, utterances_tokenized)
                    min_length, max_length = (
                        min(utterance_lengths),
                        max(utterance_lengths)
                    )
                    if (
                        MIN_UTTERANCE_LENGTH <= min_length and
                        max_length <= MAX_UTTERANCE_LENGTH
                    ):
                       for question, answer in zip(utterances, utterances[1:]):
                           print >>encoder_out, question
                           print >>decoder_out, answer
    logger.info('Done - {}'.format(input_file))


def collect_tasks(in_src_root, in_dst_root):
    for root, dirs, files in walk(in_src_root):
        for filename in files:
            if not filename.startswith('RC'):
                continue
            full_filename = path.join(root, filename)
            result_filename = path.join(in_dst_root, filename)
            add_task((full_filename, result_filename))


def build_argument_parser():
    parser = ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('src_root')
    parser.add_argument('result_root')
    parser.add_argument('--jobs', type=int, default=DEFAULT_TASKS_NUMBER)
    return parser


def main(in_text_root, in_result_folder, in_callback, in_tasks_number):
    if not path.exists(in_result_folder):
        makedirs(in_result_folder)
    collect_tasks(in_text_root, in_result_folder)
    logger.info('got {} tasks'.format(len(tasks)))
    if 1 < in_tasks_number:
        retcodes = execute_tasks(in_callback, in_tasks_number)
    else:
        retcodes = [in_callback(task) for task in tasks]


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()
    callback = locals()[args.command + '_callback']
    main(args.src_root, args.result_root, callback, args.jobs)

