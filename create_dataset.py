import os
from argparse import ArgumentParser
from codecs import getreader, getwriter
import logging
from collections import deque

from utils import DIALOGUE_SEPARATOR, DIALOGUE_STOP_LIST

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

DEFAULT_CONTEXT_LENGTH = 1
DEFAULT_TESTSET_SIZE_RATIO = 0.1


def build_argument_parser():
    parser = ArgumentParser()
    parser.add_argument('src_root')
    parser.add_argument('result_root')
    parser.add_argument(
        '--context_length',
        type=int,
        default=DEFAULT_CONTEXT_LENGTH
    )
    parser.add_argument(
        '--testset_ratio',
        type=float,
        default=DEFAULT_TESTSET_SIZE_RATIO
    )
    return parser


def collect_dialogues(in_src_root):
    for root, dirs, files in os.walk(in_src_root):
        for filename in files:
            full_filename = os.path.join(root, filename)
            with getreader('utf-8')(open(full_filename)) as reddit_in:
                dialogues = reddit_in.read().split(DIALOGUE_SEPARATOR)
                dialogues = [dialogue.split('\n') for dialogue in dialogues]
                dialogues_filtered = []
                for dialogue in dialogues:
                    dialogues_filtered.append([
                        turn.strip()
                        for turn in dialogue
                        if turn.strip() not in DIALOGUE_STOP_LIST
                    ])
                dialogues_filtered = filter(len, dialogues_filtered)
    return dialogues_filtered


def main(in_src_root, in_result_root, in_context_length, in_testset_ratio):
    if not os.path.exists(in_result_root):
        os.makedirs(in_result_root)
    dialogues = collect_dialogues(in_src_root)
    test_set_size = int(len(dialogues) * in_testset_ratio)
    train_set, test_set = dialogues[:-test_set_size], dialogues[-test_set_size:]
    logger.info('Dataset info: {} train, {} test dialogs'.format(
        len(train_set),
        len(test_set)
    ))
    train_enc = os.path.join(in_result_root, 'train.enc')
    train_dec = os.path.join(in_result_root, 'train.dec')
    with getwriter('utf-8')(open(train_enc, 'w')) as train_enc_out:
        with getwriter('utf-8')(open(train_dec, 'w')) as train_dec_out:
            dialogue_context = deque([], maxlen=in_context_length + 1)
            for dialogue in train_set:
                for question, answer in zip(dialogue[:-1], dialogue[1:]):
                    dialogue_context.append(question)
                    print >>train_enc_out, ' '.join(dialogue_context)
                    print >>train_dec_out, answer
    test_enc = os.path.join(in_result_root, 'test.enc')
    test_dec = os.path.join(in_result_root, 'test.dec')
    with getwriter('utf-8')(open(test_enc, 'w')) as test_enc_out:
        with getwriter('utf-8')(open(test_dec, 'w')) as test_dec_out:
            dialogue_context = deque([], maxlen=in_context_length + 1)
            for dialogue in test_set:
                for question, answer in zip(dialogue[:-1], dialogue[1:]):
                    dialogue_context.append(question)
                    print >>test_enc_out, ' '.join(dialogue_context)
                    print >>test_dec_out, answer


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()

    main(
        args.src_root,
        args.result_root,
        args.context_length,
        args.testset_ratio
    )
