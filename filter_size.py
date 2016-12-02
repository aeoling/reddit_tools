import json
import sys

MAX_UTTERANCE_SIZE = 60


def getSubreddits(input_stream, output_stream, max_len=MAX_UTTERANCE_SIZE):
    for line in input_stream:
        json_line = json.loads(line)
        body = json_line.get('body', None)

        if len(body.split()) < max_len:
            print >>output_stream, line.strip()


if __name__ == '__main__':
    maxlen = int(sys.argv[1]) if 1 < len(sys.argv) else MAX_UTTERANCE_SIZE
    getSubreddits(sys.stdin, sys.stdout, maxlen)
