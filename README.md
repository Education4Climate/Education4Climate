# unicrawl

Unicrawl is a tool for crawling and analyzing data from higher education schools.

This tool is developed in the context of the project Education4Climate by the volunteering
group 'The Shifters' - Belgium.

The scope of the project is the higher education schools in Belgium but the methods used here could easily 
extended to other countries.

## Composition

The tool is composed of three main parts:
- [Crawling](src/crawl/README.md)
- [Scoring](src/score/README.md)
- [Web UI](src/web-ui/README.md)

described in their respective READMEs
  
## Run

TODO: check those and remove one if not need

All requirements for running the different parts of Unicrawl are listed in requirements.yaml
and requirements.txt.

## Usage

TODO: update Makefile and see if we keep that here or in other READMEs

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
