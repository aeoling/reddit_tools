import json
import sys
import csv

def getSubreddits(input_file, output_file):
    subreddits = {}
    with open(input_file, 'r') as f:
        for line in f:
            json_line = json.loads(line)
            print json_line, '\n'
            body = json_line.get('body', None)
            subreddit_id = json_line.get('subreddit_id', None)

            if len(body.split()) < 60:
                subreddits[subreddit_id] = body
    print 'Filter completed. Found ', subreddits.keys().__len__(), 'items'

    o = csv.writer(open("output.csv", "w"))
    for key, val in subreddits.items():
        o.writerow([key, val])


if __name__ == '__main__':
    getSubreddits(sys.argv[1], sys.argv[2])
