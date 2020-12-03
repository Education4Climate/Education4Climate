import json
import re
import csv
import argparse

class Tagcloud:
    dictionary = {}

    def load(self, data, field):
        dictionary = {}
        for item in data:
            self.process(item[field])

    def process(self, text):
        words = re.findall(r'\w+', text)
        for word in words:
            word = word.lower()
            if not word in self.dictionary:
                self.dictionary[word] = 1
            else:
                self.dictionary[word] = self.dictionary[word] + 1

    def dump(self, output):
        with open(output,'w',newline='',encoding='utf-8-sig') as f:
            w = csv.writer(f)
            for word in self.dictionary:
                w.writerow([word, self.dictionary[word]])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate a wordcount from an input data file.')
    parser.add_argument("--input", type=str, help="Input file")
    parser.add_argument("--output", type=str, help="Output file")
    parser.add_argument("--field", type=str, help="Field to use as input data")
    args = parser.parse_args()

    with open(args.input, 'r') as fd:
        tagcloud = Tagcloud()
        tagcloud.load(json.load(fd), args.field)
        tagcloud.dump(args.output)