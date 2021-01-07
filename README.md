# unicrawl

A universal crawler for stuff.

## Setup in DEV mode

```bash
sudo pip3 install virtualenv
python3 -m venv venv
source ./venv/bin/activate
pip3 install Scrapy
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

###  Word count

From an input data file, generate a wordcount and save in CSV.

Arguments:
- *input* : input data file with course catalog in JSON format. 
- *output* : destination where wordcount results are saved. 
- *field*: name of the field to use as input for building the word count.

````bash
python score/wordcount.py --input data/ucl_courses.json --output tag_cloud.csv --field content
````

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

## Using the Scrapy shell

When developing a crawler, the Scrapy shell is useful to experiment with CSS or XPATH querie.

```
scrapy shell https://uclouvain.be/cours-2019-ledph1028

# Example CSS query
response.css("h1.header-school::text").get()

# Example XPath query
response.xpath("normalize-space(.//div[div[contains(text(),'Enseignants')]]/div/a/text())").getall()

# Goodbye !
quit()
``` 
