# education4climate.be

education4climate.be allows you to explore a selection of courses data of most belgian (french and dutch speaking) universities.  Only programmes and courses that address certain environmental themes were selected.  Thoses data can be explored and filtered through 3 tools : 

* **The programmes finder** where the course programmes are sorted on the basis of a score which is the total number of courses in this programme that address one of the themes.  For each theme is also displayed the total number of courses that address this one.
* **The courses finder** where the courses are sorted depending on the number of themes they address.
* **The teachers directory**

The website is available in three languages : french, dutch and english.

## Quickstart for developers

The website runs entirely client-side and relies on Vue.js to display data fetched from JSON files.  Each school has two JSONs, one for its programmes and one for its courses.  This way, developers that only work on the data crawler can easily test their data without having to dive in the JavaScript or having to deal with Node/npm.

To run locally the website, just clone the repo and serve the ```\docs``` folder (e.g. with [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension on VSCode).

## Used technologies

* JavaScript (ECMAScript 8)
* Bootstrap 5
* Vue.js 3
* JSON

## Web hosting

* GitHub Pages
* Domain name on Gandi

## Supported browser

* All modern desktop browsers : Chrome, Firefox, Edge, Safari, Opera
* All modern Android/iOS browsers : Safari on iOS, Android Browser, Chrome for Android, Firefox for Android

## JSON files

All the following JSON files are located in ```\data```.  Those data are cached in a Session Storage object as soon has they have been fetched and processed for performance reasons.

### Schools file

In addition to the two JSON files required to add a school, the file ```schools.json``` gathers few information about every schools.  It contains an array of school objects as follows : 

```
{
   "schools":[
      {
         "name":"Université catholique de Louvain",
         "shortName":"UCLouvain",
         "coursesFile":"ucl_data_2020_light.json",
         "programsFile":"ucl_data_2020_programs.json",
         "teachersDirectoryUrl":"https://uclouvain.be/fr/repertoires"
      }
   ]
}
```

### Programmes files

A programmes file contains and array of programme objects as follows : 

```
[
   {
      "id":"BA-INFO",
      "name":"Bachelier en sciences informatiques",
      "faculty":"Faculté des Sciences",
      "cycle":"bac",
      "campus":"Plaine",
      "url":"https://www.ulb.be/fr/programme/ba-info",
      "courses":[
         "ELEC-H201",
         "ENVI-F1001",
         "ETHI-F1001"
      ],
      "field":"sciences",
      "themes":[
         "energy",
         "climatology"
      ],
      "themes_scores":[
         1,
         2
      ]
   }
]
```

### Courses files

A programmes file contains and array of course objects as follows : 

```
[
   {
      "id":"ARCH-H300",
      "name":"Projet d'architecture III",
      "year":"2020-2021",
      "teachers":[
         "Samia BEN RAJEB",
         "Daniel DETHIER"
      ],
      "languages":[
         "fr"
      ],
      "url":"https://www.ulb.be/fr/programme/arch-h300",
      "themes":[
         "durability"
      ]
   }
]
```

### Translations files

Each language has a translations file named after the two first letters returned by ```navigator.language```.  It's a hierarchical file (as many levels as wanted) that can be used through the ```translate()``` method.

```{{ translate("menu.programs") }}``` will for example display ```Find a programme``` assuming the current selected language is english.


Here's an extract of the ```en.json``` file : 

```
{
   "menu":{
      "programs":"Find a programme",
      "courses":"Find a course",
      "teachers":"Teachers directory"
   },
   "shared":{
      "schools":"Universities",
      "themes":"Themes",
      "fields":"Fields",
      "languages":"Languages",
      "name":"Name",
      "code":"Code : ",
      "external-website":"read more",
      "name-exemple":"exemple : environment",
      "show-filters":"Show filters",
      "hide-filters":"Hide filters",
      "loading":"Loading",
      "close":"Close",
      "load-more":"Load more"
   }
]
```