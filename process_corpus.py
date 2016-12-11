from os import path, walk
import logging
from argparse import ArgumentParser
from codecs import getreader, getwriter

from task_list import add_task, execute_tasks, tasks
from filter_size import getSubreddits
from extract_conversations import write_comment_chains, build_comment_chains
from utils import DIALOGUE_SEPARATOR

DEFAULT_TASKS_NUMBER = 64

MIN_UTTERANCE_LENGTH = 3
MAX_UTTERANCE_LENGTH = 30

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def filter_callback(in_params):
    input_file, output_file, max_len = in_params
    logger.info('Processing file {}'.format(input_file))
    with open(input_file) as reddit_in, open(output_file, 'w') as reddit_out:
        getSubreddits(reddit_in, reddit_out)


def chain_callback(in_params):
    input_file, output_file = in_params
    logger.info('Processing file {}'.format(input_file))
    with getreader('utf-8')(open(input_file)) as reddit_in:
        with getwriter('utf-8')(open(output_file, 'w')) as reddit_out:
            comments_tree_root = build_comment_chains(reddit_in)
            write_comment_chains(comments_tree_root, reddit_out)
    logger.info('Done - {}'.format(input_file))


def to_easy_seq2seq(in_params):
    input_file, output_file = in_params
    logger.info('Processing file {}'.format(input_file))
    with getreader('utf-8')(open(input_file)) as reddit_in:

            dialogs = reddit_in.read().split(DIALOGUE_SEPARATOR)
            for dialog in dialogs:
                utterances = [
                    utterance.partition('\t')[2].strip().split()
                    for utterance in dialog.split('\n')
                ]
                utterance_lengths = map(len, utterances)
                min_length, max_length = (
                    min(utterance_lengths),
                    max(utterance_lengths)
                )
                if (
                    MIN_UTTERANCE_LENGTH <= min_length and
                    max_length <= MAX_UTTERANCE_LENGTH
                ):
                    write_easy_seq2seq_format(utterances, output_file)
    logger.info('Done - {}'.format(input_file))


def write_easy_seq2seq_format(in_dialog, in_filename):
    enc_filename = path.join(in_filename, '.enc')
    dec_filename = path.join(in_filename, '.dec')
    with getwriter('utf-8')(open(enc_filename, 'w')) as encoder_out:
        with getwriter('utf-8')(open(dec_filename, 'w')) as decoder_out:
            for question, answer in zip(in_dialog, in_dialog[1:]):
                print >>encoder_out, question
                print >>decoder_out, answer


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
