import json
from sys import argv, stdin, stdout, setrecursionlimit
from codecs import getreader, getwriter
import re
import logging

from utils import DIALOGUE_SEPARATOR

# comment chaining is implemented via recursion - so likely we'll go really deep
# setrecursionlimit(100000)

MAXIMUM_CHAIN_DEPTH = 100

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


class CommentTreeNode(object):
    def __init__(self, in_id, in_body):
        self.body = in_body
        if self.body:
            self.body = re.sub('\s', ' ', self.body.strip().lower())
        self.children = []
        self.node_id = in_id

    def adopt_child(self, in_node):
        self.children.append(in_node)


def write_comment_chains(in_root_node, in_output_stream, in_previous_context=[]):
    try:
        own_content = [] \
            if in_root_node.node_id == 0 \
            else [(in_root_node.node_id, in_root_node.body)]
        comment_chain = in_previous_context + own_content
        if (
            MAXIMUM_CHAIN_DEPTH == len(comment_chain) or
            not len(in_root_node.children)
        ):
            print >>in_output_stream, u'\n'.join([
                '\t'.join(node_content)
                for node_content in comment_chain
            ])
            print >>in_output_stream, DIALOGUE_SEPARATOR
        if MAXIMUM_CHAIN_DEPTH == len(comment_chain):
            return
        for child in in_root_node.children:
            write_comment_chains(child, in_output_stream, comment_chain)
    except RuntimeError as exc:
        print in_previous_context
        raise


def build_comment_chains(in_stream):
    document_root = CommentTreeNode(0, None)
    all_nodes = {}

    with getreader('utf-8')(in_stream) as reddit_in:
        for line in reddit_in:
            comment_json = json.loads(line)
            comment_id, parent_id, body = (
                comment_json['id'],
                comment_json.get('parent_id', None),
                comment_json['body']
            )
            parent_id = parent_id.partition('_')[2] if parent_id else None
            comment_node = CommentTreeNode(comment_id, body)
            all_nodes[comment_id] = comment_node
            if not parent_id:
                parent_node = document_root
            elif not parent_id in all_nodes:
                parent_node = CommentTreeNode(parent_id, '__CONTENT_MISSING__')
                document_root.adopt_child(parent_node)
                all_nodes[parent_id] = parent_node
            else:
                parent_node = all_nodes[parent_id]
            parent_node.adopt_child(comment_node)
    return document_root


if __name__ == '__main__':
    if len(argv) == 2 and argv[1] == '--help':
        print 'Usage: extract_conversations.py < <input filename> > <output_filename>'
        exit()
    comments_tree_root = build_comment_chains(stdin)

    with getwriter('utf-8')(stdout) as OUTPUT_WRITER:
        stats = 0
        write_comment_chains(comments_tree_root, OUTPUT_WRITER)

