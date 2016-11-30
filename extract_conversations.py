import json
from sys import argv, stdout
from collections import defaultdict
from codecs import getreader, getwriter
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def build_comment_chains(in_file_name):
    comment_chains = defaultdict(lambda: [])
    conversation_roots = {}

    with getreader('utf-8')(open(in_file_name)) as reddit_in:
        for line in reddit_in:
            comment_json = json.loads(line)
            comment_id, parent_id = (
                comment_json.get('id', None),
                comment_json.get('parent_id', None)
            )
            # we have the root of the comment chain - probably, top level comment
            if not parent_id or parent_id.partition('_')[2] not in conversation_roots:
                comment_chains[comment_id].append(comment_json['body'])
                conversation_roots[comment_id] = comment_id
            else:
                parent_id = parent_id.partition('_')[2]
                conversation_roots[comment_id] = conversation_roots[parent_id]
                comment_chains[conversation_roots[comment_id]].append(comment_json['body'])
    return comment_chains


if __name__ == '__main__':
    if len(argv) < 2:
        print 'Usage: extract_conversations.py <input filename>'
        exit()
    comment_chains = build_comment_chains(argv[1])
    logger.info('#chains found: {}'.format(len(comment_chains)))

    with getwriter('utf-8')(stdout) as OUTPUT_WRITER:
        for chain_id, chain in comment_chains.iteritems():
            print >>OUTPUT_WRITER, u'\n'.join(chain)

