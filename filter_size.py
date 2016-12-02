import json
import sys

def getSubreddits(input_file):

    with open(input_file, 'r') as f:
        for line in f:
            json_line = json.loads(line)
            print json_line, '\n'
            body = json_line.get('body', None)

            if len(body.split()) < 60:
                print line

if __name__ == '__main__':
    getSubreddits(sys.argv[1])
