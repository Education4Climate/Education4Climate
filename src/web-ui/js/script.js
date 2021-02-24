/*jshint esversion: 8 */

const DATA_FOLDER = "data";
const SCHOOLS_FILE = DATA_FOLDER + "/" + "schools.json";
const THEMES = ["decarbonization", "energy", "consumption", "environment", "climatology", "durability", "society"];

var schoolsCount = [];
var themesCount = [];
var languagesCount = [];

var table;

/* NAVIGATION */

window.addEventListener('load', function () {

    showPage(new URLSearchParams(window.location.search).get('page'));
});

function showPage(page) {

    page = !page ? "home" : page; // la page d'accueil est la valeur par défaut si on ne passe pas d'argument page

    ["home", "courses-finder", "teachers-directory", "methodology"].forEach(value => { document.getElementById(value).style.display = page == value ? "block" : "none"; });

    switch (page) {
        case "home": break;
        case "courses-finder": showCoursesFinder(); break;
        case "teachers-directory": break;
        case "methodology": break;
        default: document.getElementById("home").style.display = "block";
    }
}

function showCoursesFinder() {

    getCourses().then(courses => {

        buildCoursesFinderFilters(courses);
        buildCoursesFinderTable(courses);
    });
}

function buildCoursesFinderFilters(courses) {

    courses.forEach(course => {

        // On parcourt les thématiques du cours et on peuple chaque compteur

        course.themes.forEach(theme => {

            if (!themesCount.includes(theme)) {

                themesCount.push(theme);
                themesCount[theme] = 0;
            }

            themesCount[theme]++;
        });

        // On parcourt les langues du cours et on peuple chaque compteur

        course.languages.forEach(language => {

            if (!languagesCount.includes(language)) {

                languagesCount.push(language);
                languagesCount[language] = 0;
            }

            languagesCount[language]++;
        });

        // On peuple chaque compteur d'université

        if (!schoolsCount.includes(course.schoolShortName)) {

            schoolsCount.push(course.schoolShortName);
            schoolsCount[course.schoolShortName] = 0;
        }

        schoolsCount[course.schoolShortName]++;
    });

    // On trie les thématiques et les langues alphabétiquement

    schoolsCount.sort((a, b) => { return a.localeCompare(b); }); // a.localCompare(b) permet de trier sans prendre en compte les accents (e/é/è)
    themesCount.sort((a, b) => { return a.localeCompare(b); });
    languagesCount.sort((a, b) => { return a.localeCompare(b); });

    // On crée les 3 filtres

    schoolsCount.forEach(school => {

        var line = "<div class='custom-control custom-checkbox'><span class='float-right badge badge-light round'>" + schoolsCount[school] + "</span>" +
            "<input type='checkbox' class='custom-control-input' id='checkbox-" + school + "' value='" + school + "' onclick='setFilters()' checked>" +
            "<label class='custom-control-label' for='checkbox-" + school + "'>" + school + "</label></div>";
        document.querySelector("#schools-selector").innerHTML += line;
    });

    themesCount.forEach(theme => {

        var line = "<div class='custom-control custom-checkbox'><span class='float-right badge badge-light round'>" + themesCount[theme] + "</span>" +
            "<input type='checkbox' class='custom-control-input' id='checkbox-" + theme + "' value='" + theme + "' onclick='setFilters()' checked>" +
            "<label class='custom-control-label' for='checkbox-" + theme + "'>" + theme + "</label></div>";
        document.querySelector("#themes-selector").innerHTML += line;
    });

    languagesCount.forEach(language => {

        var line = "<div class='custom-control custom-checkbox'><span class='float-right badge badge-light round'>" + languagesCount[language] + "</span>" +
            "<input type='checkbox' class='custom-control-input' id='checkbox-" + language + "' value='" + language + "' onclick='setFilters()' checked>" +
            "<label class='custom-control-label' for='checkbox-" + language + "'>" + getLanguageFromISOCode(language) + "</label></div>";
        document.querySelector("#languages-selector").innerHTML += line;
    });
}

function buildCoursesFinderTable(courses) {

    $('[data-toggle="tooltip"]').tooltip();

    // On instancie la table

    table = new Tabulator("#courses-table-container", {

        data: courses,
        pagination: "local",
        paginationSize: 20,
        initialSort: [{ column: "climateScore", dir: "desc" }],
        rowClick: function (e, row) { openModal(e, row); },
        locale: true,
        columns: [
            { title: "Score", field: "climateScore", formatter: "star", sorter: "number", tooltip: true },
            { title: "Université", field: "schoolShortName", sorter: "string" },
            { title: "Intitulé", field: "name", sorter: "string" },
            { title: "Code", field: "shortName", formatter: "link", formatterParams: { labelField: "shortName", urlField: "url", target: "_blank" } },
            {
                title: "Thématiques", field: "themes", headerSort: false, formatter: function (cell, formatterParams, onRendered) {

                    var cellValue = "";
                    cell.getValue().forEach(value => { cellValue += "<span class='badge badge-primary badge-theme'>" + value + "</span>&nbsp;"; });

                    return cellValue;
                }
            },
            {
                title: "Langues", field: "languages", headerSort: false, formatter: function (cell, formatterParams, onRendered) {

                    var cellValue = "";
                    cell.getValue().forEach(function (value, i, values) { cellValue += i < values.length - 1 ? getLanguageFromISOCode(value) + " | " : getLanguageFromISOCode(value); });

                    return cellValue;
                }
            },
        ]
    });

    buildCoursesFinderCount();
}

function buildCoursesFinderCount() {

    document.getElementById("results-count").innerHTML = "<strong>" + table.getDataCount("active") + " cours sur un total de " + table.getDataCount() + " correspondent à vos critères</strong>";
}

/* FILTRES */

function setFilters() {

    // On chaîne les différents filtres

    table.setFilter([getSelectedSchoolsFilter(), getSelectedThemesFilter(), getSelectedLanguagesFilter(), getSearchedCourseFilter()]);

    // On recalcule le compteur de résultats

    buildCoursesFinderCount();
}

function getSearchedCourseFilter() {

    return { field: "name", type: "like", value: document.getElementById("courses-search").value };
}

function getSelectedSchoolsFilter() {

    var selectedSchools = "";

    document.querySelectorAll("#schools-selector input[type='checkbox']:checked").forEach(checkbox => {
        selectedSchools += checkbox.value + " ";
    });

    // Si aucune école n'est sélectionnée, on envoie un filtre qui fait d'office échouer la recherche ("-")

    return { field: "schoolShortName", type: "keywords", value: selectedSchools == "" ? "-" : selectedSchools.trim() };
}

function getSelectedThemesFilter() {

    var selectedThemes = "";

    document.querySelectorAll("#themes-selector input[type='checkbox']:checked").forEach(checkbox => {
        selectedThemes += checkbox.value + " ";
    });

    // Si aucune thématique n'est sélectionnée, on envoie un filtre qui fait d'office échouer la recherche ("-")

    return { field: "themes", type: "keywords", value: selectedThemes == "" ? "-" : selectedThemes.trim() };
}

function getSelectedLanguagesFilter() {

    var selectedLanguages = "";

    document.querySelectorAll("#languages-selector input[type='checkbox']:checked").forEach(checkbox => {
        selectedLanguages += checkbox.value + " ";
    });

    // Si aucune école n'est sélectionnée, on envoie un filtre qui fait d'office échouer la recherche ("-")

    return { field: "languages", type: "keywords", value: selectedLanguages == "" ? "-" : selectedLanguages.trim() };
}

function toggleFilters() {

    var sidebar = document.getElementById("courses-finder-sidebar");
    var button = document.getElementById("courses-finder-show-filters");

    button.innerHTML = sidebar.style.display == "block" ? "Afficher les filtres" : "Cacher les filtres";
    sidebar.style.display = sidebar.style.display == "block" ? "none" : "block";
}

/* MODAL */

function openModal(e, row) {

    course = row.getData();

    document.getElementById("course-details-name").innerHTML = course.name;
    document.getElementById("course-details-short-name").innerHTML = course.shortName;
    document.getElementById("course-details-years").innerHTML = course.years;
    document.getElementById("course-details-abstract").innerHTML = course.abstract;
    document.getElementById("course-details-university").innerHTML = course.schoolShortName;
    document.getElementById("course-details-campus").innerHTML = "&nbsp;(" + course.campus + ")";
    document.getElementById("course-details-climate-score").innerHTML = course.climateScore;
    document.getElementById("course-details-shift-score").innerHTML = course.shiftScore;
    document.getElementById("course-details-url").href = course.url;
    document.getElementById("course-details-url").innerHTML = "Site de l'" + course.schoolShortName;
    document.getElementById("course-details-credits").innerHTML = course.credits;

    var themes = "";
    course.themes.forEach(value => { themes += "<span class='badge badge-primary badge-theme'>" + value + "</span>&nbsp;"; });
    document.getElementById("course-details-themes").innerHTML = themes;

    var teachers = "";
    course.teachers.forEach(function (value, i, values) { teachers += i < values.length - 1 ? "<a href='?page=teachers-directory&teacher=" + value + "' target='_blank'>" + value + "</a>" + ", " : "<a href='?page=teachers-directory&teacher=" + value + "' target='_blank'>" + value + "</a>"; });
    document.getElementById("course-details-teachers").innerHTML = teachers;

    var languages = "";
    course.languages.forEach(function (value, i, values) { languages += i < values.length - 1 ? getLanguageFromISOCode(value) + ", " : getLanguageFromISOCode(value); });
    document.getElementById("course-details-languages").innerHTML = languages;

    $('#course-details-modal').modal();
}

function closeModal() {

    document.getElementById("course-details-modal").style.display = "none";
}

/* DATA */

async function getSchools() {

    if (!sessionStorage.schools) {

        var schools = [];

        await fetch(SCHOOLS_FILE).then((response) => {
            return response.json();
        }).then((data) => {

            data.schools.forEach(school => {

                schools.push({
                    id: school.id,
                    name: school.name,
                    shortName: school.shortName,
                    file: school.file
                });
            });
        });

        sessionStorage.schools = JSON.stringify(schools);
    }

    return JSON.parse(sessionStorage.schools);
}

async function getCourses() {

    if (!sessionStorage.courses) {

        var courses = [];

        const schools = await getSchools();

        await Promise.all(schools.map(school => fetch("data/" + school.file)))
            .then(responses => Promise.all(responses.map(res => res.json())))
            .then(results => {

                for (var i = 0; i < results.length; i++) {

                    // On agrège les données de toutes les écoles dans un même tableau

                    results[i].forEach(course => {

                        courses.push({

                            schoolShortName: schools[i].shortName,
                            name: course.name,
                            shortName: course.id,
                            years: course.year,
                            teachers: course.teacher,
                            url: course.url,
                            languages: course.language,
                            themes: getThemes(course), //course.themes,
                            //abstract: course.abstract,
                            //campus: course.campus,
                            //shiftScore: course.shiftScore,
                            //climateScore: course.climateScore,
                            //credits: course.credits                          
                        });
                    });
                }
            });

        sessionStorage.courses = JSON.stringify(courses);
    }

    return JSON.parse(sessionStorage.courses);
}

/* HELPERS */

function getLanguageFromISOCode(code) {

    dictionary = { "fr": "Français", "nl": "Néerlandais", "en": "Anglais", "de": "Allemand", "ar": "Arabe" };

    return dictionary.hasOwnProperty(code) ? dictionary[code] : "Inconnu";
}

function getThemes(course) {

    var themes = [];

    THEMES.forEach(theme => { if (course[theme]) { themes.push(theme); } });

    return themes;
}

document.querySelectorAll('.smooth-scroll').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});