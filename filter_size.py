import json
import sys

MAX_UTTERANCE_SIZE = 60


def getSubreddits(input_stream, in_max_len):
    for line in input_stream:
        json_line = json.loads(line)
        body = json_line.get('body', None)

        if len(body.split()) < in_max_len:
            print line.strip()


if __name__ == '__main__':
    maxlen = int(sys.argv[1]) \
        if 1 < len(sys.argv) \
        else MAX_UTTERANCE_SIZE
    getSubreddits(sys.stdin, maxlen)

