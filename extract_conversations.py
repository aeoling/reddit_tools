import json
from sys import argv
from collections import defaultdict
from codecs import getreader


def main(in_file_name):
    comment_ids = defaultdict(lambda: [])
    conversation_roots = {}
    with getreader('utf-8')(open(in_file_name)) as reddit_in:
        for line in reddit_in:
            comment_json = json.loads(line)
            comment_id, parent_id = comment_json.get('id', None), comment_json.get('parent_id', None)
            if not parent_id:
                comment_ids[comment_id].append(comment_id)
                conversation_roots[comment_id] = comment_id
            else:
                parent_id = parent_id.partition('_')[2]
                conversation_roots[comment_id] = conversation_roots[parent_id]
                comment_ids[conversation_roots[comment_id]].append(comment_id)
    return comment_ids


if __name__ == '__main__':
    if len(argv) < 2:
        print 'Usage: extract_conversations.py <input filename>'
        exit()
    print main(argv[1]).values()[:5]
