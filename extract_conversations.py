import json
from sys import argv, stdout
from codecs import getreader, getwriter
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


class CommentTreeNode(object):
    def __init__(self, in_id, in_body):
        self.body = in_body
        self.children = []
        self.node_id = in_id

    def adopt_child(self, in_node):
        self.children.append(in_node)


def get_comment_chains(in_root_node):
    own_content = [] \
        if in_root_node.node_id == 0 \
        else [(in_root_node.node_id, in_root_node.body)]
    if not len(in_root_node.children):
        yield own_content
    for child in in_root_node.children:
        for child_chain in get_comment_chains(child):
            yield own_content + child_chain


def build_comment_chains(in_file_name):
    document_root = CommentTreeNode(0, None)
    all_nodes = {}

    with getreader('utf-8')(open(in_file_name)) as reddit_in:
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
    if len(argv) < 2:
        print 'Usage: extract_conversations.py <input filename>'
        exit()
    comments_tree_root = build_comment_chains(argv[1])

    with getwriter('utf-8')(stdout) as OUTPUT_WRITER:
        for comment_chain in get_comment_chains(comments_tree_root):
            print >>OUTPUT_WRITER, u'\n'.join(
                ['\t'.join(node_content) for node_content in comment_chain]
            )
