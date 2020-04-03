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

Execute the UCL crawler, fetching all courses and saving them in the output file in JSON format.

Arguments:

- *output* : destination where crawler results are saved.  

```bash
python3 crawler/ucl.py --output data/ucl_test.json
```

###  Word count

From an input data file, generate a wordcount and save in CSV.

Arguments:
- *input* : input data file with course catalog in JSON format. 
- *output* : destination where wordcount results are saved. 
- *field*: name of the field to use as input for building the word count.

````bash
python process/wordcount.py --input data/ucl_courses.json --output tag_cloud.csv --data content
````

### Scoring

From an input data file, score and filter all entries.

Arguments:
- *input* : input data file with course catalog in JSON format. 
- *output* : destination where scoring results are saved. 
- *field*: name of the field to use as input for running the scoring.
- *key*: name of field to use as reference key

```bash
python process/score.py --input data/ucl_courses.json --output test.csv --key shortname --field content
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