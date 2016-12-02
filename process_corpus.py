from sys import argv
from os import path, walk
import logging

from task_list import add_task, execute_tasks, tasks
from filter_size import getSubreddits, MAX_UTTERANCE_SIZE

DEFAULT_TASKS_NUMBER = 64

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def filter_file_callback(in_params):
    try:
        input_file, output_file, max_len = in_params
        logger.info('Processing file {}'.format(input_file))
        with open(input_file) as reddit_in, open(output_file, 'w') as reddit_out:
            getSubreddits(reddit_in, reddit_out, max_len)
        return 0
    except:
        return 1


def collect_tasks(in_src_root, in_dst_root):
    for root, dirs, files in walk(in_src_root):
        for filename in files:
            if not filename.startswith('RC'):
                continue
            full_filename = path.join(root, filename)
            result_filename = path.join(in_dst_root, filename)
            add_task((full_filename, result_filename, MAX_UTTERANCE_SIZE))


def main(in_text_root, in_result_folder, in_tasks_number):
    collect_tasks(in_text_root, in_result_folder)
    logger.info('got {} tasks'.format(len(tasks)))
    if 1< in_tasks_number:
        retcodes = execute_tasks(filter_file_callback, in_tasks_number)
    else:
        retcodes = [filter_file_callback(task) for task in tasks]
    assert sum(retcodes) == 0, 'Some tasks failed!'


if __name__ == '__main__':
    if len(argv) < 2:
        print 'Usage: {} <root folder> <result folder> [tasks_number=64]'.format(argv[0])
        exit()
    root_folder, result_folder = argv[1:3]
    tasks_number = DEFAULT_TASKS_NUMBER if len(argv) < 4 else int(argv[3])
    main(root_folder, result_folder, tasks_number)
