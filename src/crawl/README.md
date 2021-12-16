## Crawling

The goal of crawling is to extract automatically information from web content.

In the context of this project, what we seek is information about higher education schools.
More particularly, information about the courses and programs they offer.

For each school, we therefore develop two crawlers (i.e. scripts for crawling): one for programs and one for courses.

### Academic year

Before explaining the two types of crawlers and their output, it is important to note that 
schools change their programs on a yearly basis. Thus, all of the scripts described below take as 
input the year for which the data should be extracted.

### Program crawler

A program is generally composed of a set of courses, compulsory or not, and under the completion of a sufficient number
of these courses, a diploma unique to this program is awarded.

The programs crawlers are contained in [src/crawl/unicrawl/spiders](unicrawl/spiders) and named in the following way: 
```{SchoolCode}_programs.py```.

For each program, we retrieve:
- ```id```: the code of the program (note: if there is none, we make up one)
- ```name```: the name of the program
- ```cycle```: its cycle (bac, master, ...)
- ```faculties```: the list of faculties/institutes organising the program
- ```campuses```: the list of campuses where it is organised
- ```url```: the url of the web page of the program
- ```courses```: the list of courses that are offered in this program
- ```ects```: the list of ECTS associated to these courses in the program

For the fields requiring a list, a list needs to be provided even if it contains only one or no elements.

The output of the crawler is saved in the directory [data/crawling-output/](../../data/crawling-output) 
under the name ```{SchoolCode}_programs_{YEAR}.json```.

#### Duplicate programs outputs
Due to the structure of certain school websites, program information can be split across different webpages
that cannot be access sequentially leading to the creation several lines corresponding
to this program in the output file

In that case (see for example the program crawler for [UCLouvain](unicrawl/spiders/ucl_programs.py)), the output
of the program crawler is saved to a file named ```{SchoolCode}_programs_{YEAR}_pre.csv```.
The duplicate program lines are then merged using the script [*merge.py*](merge.py) with arguments
```-t program -s {SchoolCode} -y {YEAR}```. The final results in the ```{SchoolCode}_programs_{YEAR}.json``` file.


### Course crawler

What we refer as course in the crawlers can actually be one of two things. 
The first, most straightforward one, is a class given by one or several teachers. 
The second one is actually a group of classes, usually called a 'teaching unit'.
This differentiation is made because a lot of schools do not provide unique web pages per class
but only per teaching unit, preventing from retrieving information per class.
In the following description, we will therefore use the word 'course' to refer both 
to individual classes and teaching units.

As for programs, the courses crawlers are contained in [src/crawl/unicrawl/spiders](unicrawl/spiders) 
and named: ```{SchoolCode}_courses.py```.

For each course, we retrieve:
- ```id```: the id of the course
- ```name```: the name of the course
- ```year```: the academic year (e.g. 2020-2021) (TODO: remove?)  
- ```languages```: the list of languages in which the course is given/evaluated
- ```teachers```: the list of teachers giving/organising the course
- ```url```: the url of the web page where the course is described
- ```content```: text describing the content of the course
- ```goal```: text describing the goals of the course
- ```activity```: text describing the activities organised during the course
- ```other```: other textual information deemed interesting

The last four fields can be crawled or not depending on the elements describing
the course on the course web page.

The output of the crawler is saved in the directory [data/crawling-output/](../../data/crawling-output) 
under the name ```{SchoolCode}_courses_{YEAR}.json```.

#### Duplicate courses outputs
As for programs, the script [*merge.py*](merge.py) can be used to update the output of some
course crawlers with the 'pre' suffix 
(see for example [UAntwerpen](unicrawl/spiders/uantwerpen_courses.py)).
The duplicate course lines can be merged using the arguments
```-t course -s {SchoolCode} -y {YEAR}```.


### Program fields in course crawling (and vice-versa)

For some schools, it can be the case that a field supposed to be crawled for programs (e.g. ```faculties```)
is more easily accessible from the course web pages.
In that case, the field is crawled and added to the corresponding
course file in the same name and format as it would have been in the program file.
For example, for the field ```faculties```, a list has to be provided even if the
course is only associated to one faculty.
The same logic applies when a course field is more easily accessible at the program level.


### Scrapy

All crawlers are developed using the Scrapy Python library.
For more information, check: https://scrapy.org/.

### For Developers
#### Why you should not use a 'hand-made' launcher and how to do then?

##### Why?
Because if you do, you are not using the parametrization of the scraper.

##### How?
To launch a crawler and the debugger with PyCharm :
- Run / Edit configurations
- Choose the configuration you want to modify
- Switch from "Script path" to "Module name" and write : scrapy.cmdline
- Parameters : runspider unicrawl/spiders/{name of the script.py}
- Working directory : {absolute path to your unicrawl folder}\src\crawl
