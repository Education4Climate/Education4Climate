<a href="https://theshiftproject.org/equipe/#benevoles"><img src="https://theshiftproject.org/wp-content/uploads/2021/09/Fichier-1@2x-300x152.png" alt="The Shifters" width="230px"></a>

# Education4Climate

[Education4Climate](https://education4climate.be/) is a tool for crawling and analyzing data from higher education schools.

This tool is developed in the context of the project Education4Climate by the volunteering
group 'The Shifters' - Belgium.

The scope of the project is the higher education schools in Belgium but the methods used here could easily be
extended to other countries.

## Composition

The tool is composed of three main parts:
- [Crawling](src/crawl/README.md)
- [Scoring](src/score/README.md)
- [Web UI](docs/README.md)

described in their respective READMEs.
  

### Requirements

All requirements for running the different parts of Unicrawl are listed in requirements.yaml
and requirements.txt.

### Run using Snakemake

Crawling and scoring results can be automatically generated using 
the workflow management system [Snakemake](https://snakemake.readthedocs.io/en/stable/index.html).

Snakemake allows defining rules which describe how to generate a given output file by specifying
which inputs are required and through which script. There can be dependencies between rules such that
the output of one rule is the input of another rule. Snakemake then automatically determines which rules
and in which order it should execute them.

For example, calling:

```bash
snakemake -j1 data/scoring-output/unamur_scoring_2020.csv
```

will first execute the rule ```crawl_courses``` if the file *data/crawling-output/unamur_courses_2020.json* has not been 
yet generated as it is a required input for the rule ```score_courses```, which will then be called to generate
the desired file.

All these rules are defined in a [Snakefile](Snakefile). Special rules such
as ```score_programs_for_all_school``` allow to automatically generate for all schools defined in the Snakefile
the program score files by running

```bash
snakemake -j1 score_programs_for_all_school
```
