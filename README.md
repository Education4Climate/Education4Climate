# unicrawl

A universal crawler for stuff.

## Setup in DEV mode

```bash
sudo pip3 install virtualenv
python3 -m venv venv
source ./venv/bin/activate
pip3 install Scrapy
python3 -m spacy download fr
#python3 -m spacy download nl
#python3 -m spacy download en
```

If you want to leave the virtual-environment, just run:
```
deactivate
```

When you are returning and need to load the virtual environment:
````bash
source ./venv/bin/activate
````

## Usage

### Crawler

Testing: 

```bash
make test-ucl
```

Execute the UCL crawler, fetching all courses and saving them in the output file in JSON format.

Arguments: arguments are set up in the Makefile
- *year*: year of the analyzed courses (*2020 means the academic year 2020-2021*). 
- *output file*: output file path, directly linked to the year. (*data/ucl_2020.json*)

```bash
make generate-ucl
```

### Scoring

From an input data file, score and filter all entries.

Arguments:
- *school* : code of the school. 
- *year* : year. 
- *field*: name of the field to use as input for running the scoring.
- *language*: code of the main language of the corpus (fr, nl or en)

```bash
python score/main.py --school ucl --year 2020 --field content --language fr
```
