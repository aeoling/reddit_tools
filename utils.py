import json


DIALOGUE_SEPARATOR = '#' * 60
DIALOGUE_STOP_LIST = [
    '__content_missing__',
    '[deleted]'
]


def extract_ids(in_stream):
    ids_set = {}
    for line in in_stream:
        comment_json = json.loads(line)
        comment_id = comment_json.get('id', None)
        if comment_id is not None:
            ids_set.add(comment_id)
    return ids_set
