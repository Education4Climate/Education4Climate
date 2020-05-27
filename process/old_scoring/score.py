import json
import re
import csv
import argparse
from functools import reduce

class Scoring:

    dictionary = ('environnement',
                  'climat', 'climatique',
                  'énergie',
                  'durable', 'développement',
                  'écosystème',
                  'nature', 'naturelle', 'naturelles',
                  'co2', 'gaz', 'serre',
                  'écologie', 'ecolo', 'écologique',
                  'resources'
    )

    results = list()

    def load(self, data, key_field, score_field):
        for item in data:
            self.process(item[key_field], item[score_field])

    def process(self, id, text):
        occurences = dict()
        words = re.findall(r'\w+', text)

        for word in words:
            word = word.lower()
            if word in self.dictionary:
                if not word in occurences:
                    occurences[word] = 1
                else:
                    occurences[word] = occurences[word] + 1

        if len(occurences) > 0:
            score = reduce(lambda x, value: x * value, occurences.values(), 1)
            if score > 1:
                self.results.append({'id': id, 'score': score, 'words': occurences})

    def dump(self, output):
        with open(output,'w',newline='',encoding='utf-8-sig') as f:
            w = csv.writer(f)
            for result in self.results:
                w.writerow([result['id'], result['score'], result['words']])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter entries with scoring rules.')
    parser.add_argument("--input", type=str, help="Input file")
    parser.add_argument("--output", type=str, help="Output file")
    parser.add_argument("--key", type=str, help="Field used as unique key")
    parser.add_argument("--field", type=str, help="Field used to run the scoring")
    args = parser.parse_args()

    with open(args.input, 'r') as fd:
        scoring = Scoring()
        scoring.load(json.load(fd), args.key, args.field)
        scoring.dump(args.output)