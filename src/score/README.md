## Scoring

The goal of the scoring part of unicrawl is to identify which courses and programs in each school
cover certain *themes*.

### Themes, ontologies and patterns

A theme is an abstract notions defined based on an ontology.
While themes can be of any type, in the context of the Education4Climate project, we have defined
7 such themes:
- Climatology
- Consumption
- Decarbonization
- Durability
- Energy
- Environment
- Society

A theme's ontology is composed of a list of regular expressions that match to compounds of terms. 
For example, some compounds associated to the theme 'Climatology' could be 'climate action' and 'climate action**s**'.
A pattern ```climate actions?``` allows to capture both those compounds.

In Belgium, courses are described in French, Dutch and English. Thus, each
ontology is translated in those different languages.

The ontologies of patterns (in each language) for the 7 themes cited above are listed in the file 
```themes_patterns.json``` stored in [data/patterns/](../../data/patterns).

### Scoring courses

One of the fields extracted for each course via the crawling is ```content``` (see [Crawling](../crawl/README.md)
for more information). This field contains text describing the content of the course.

This text is first analyzed using the [langdetect](https://pypi.org/project/langdetect/) library 
to identify in which language the course is described. Then for each theme, 
all patterns in the corresponding ontology are searched in the text. If at least one pattern is found in the text,
the course is given a score of 1 for that theme, otherwise it scores 0.

The first output of the courses scoring is a table (courses x themes) that is saved in
[data/scoring-output/](../../data/scoring-output) under the name ```{School code}_scoring_{YEAR}.csv```.

The second output is a json file containing for each theme, the courses that scored 1, which patterns 
were found in each course description and to what compounds these patterns matched.
This output is saved in the same directory under the name ```{School code}_matches_{YEAR}.json```.

### Scoring programs

Once courses are scored, a score can be computed per theme for each program by computing the number of 
courses in that program that have score 1 in each theme.
A table containing this information is saved in the output scoring directory under the name 
```{School code}_programs_scoring_{YEAR}.csv```.