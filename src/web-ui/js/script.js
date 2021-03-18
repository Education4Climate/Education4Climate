/*jshint esversion: 8 */

const DATA_FOLDER = "data";
const SCHOOLS_FILE = DATA_FOLDER + "/" + "schools.json";
const THEMES = ["decarbonization", "energy", "consumption", "environment", "climatology", "durability", "society"];

var schoolsCount = [];
var coursesThemesCount = [];
var programsThemesCount = [];
var programsFieldsCount = [];
var languagesCount = [];

var table;

/* NAVIGATION */

window.addEventListener('load', function () {

    showPage(new URLSearchParams(window.location.search).get('page'));
});

function showPage(page) {

    page = !page ? "home" : page; // la page d'accueil est la valeur par défaut si on ne passe pas d'argument page

    ["home", "courses-finder", "programs-finder", "teachers-directory", "methodology"].forEach(value => { document.getElementById(value).style.display = page == value ? "block" : "none"; });

    switch (page) {
        case "home": break;
        case "courses-finder": showCoursesFinder(); break;
        case "teachers-directory": break;
        case "methodology": break;
        case "programs-finder": showProgramsFinder(); break;
        default: document.getElementById("home").style.display = "block";
    }
}

function showCoursesFinder() {

    getCourses().then(courses => {

        buildCoursesFinderFilters(courses);
        buildCoursesFinderTable(courses);
    });
}

function showProgramsFinder() {

    getPrograms().then(programs => {

        buildProgramsFinderFilters(programs);
        buildProgramsFinderTable(programs);
    });
}

function buildCoursesFinderFilters(courses) {

    courses.forEach(course => {

        // On parcourt les thématiques du cours et on peuple chaque compteur

        course.themes.forEach(theme => {

            if (!coursesThemesCount.includes(theme)) {

                coursesThemesCount.push(theme);
                coursesThemesCount[theme] = 0;
            }

            coursesThemesCount[theme]++;
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
    coursesThemesCount.sort((a, b) => { return a.localeCompare(b); });
    languagesCount.sort((a, b) => { return a.localeCompare(b); });

    // On crée les 3 filtres

    schoolsCount.forEach(school => {

        var schoolId = "school-" + school.toId();

        var line = "<div class=\"custom-control custom-checkbox\"><span class=\"float-right badge badge-light round\">" + schoolsCount[school] + "</span>" +
            "<input type=\"checkbox\" class=\"custom-control-input\" id=\"checkbox-" + schoolId + "\" value=\"" + schoolId + "\" onclick=\"setFilters('courses')\" checked>" +
            "<label class=\"custom-control-label\" for=\"checkbox-" + schoolId + "\">" + school + "</label></div>";
        document.querySelector("#courses-finder .schools-selector").innerHTML += line;
    });

    coursesThemesCount.forEach(theme => {

        var line = "<div class=\"custom-control custom-checkbox\"><span class=\"float-right badge badge-light round\">" + coursesThemesCount[theme] + "</span>" +
            "<input type=\"checkbox\" class=\"custom-control-input\" id=\"checkbox-" + theme + "\" value=\"" + theme + "\" onclick=\"setFilters('courses')\" checked>" +
            "<label class=\"custom-control-label\" for=\"checkbox-" + theme + "\">" + theme + "</label></div>";
        document.querySelector("#courses-finder .themes-selector").innerHTML += line;
    });

    languagesCount.forEach(language => {

        var line = "<div class=\"custom-control custom-checkbox\"><span class=\"float-right badge badge-light round\">" + languagesCount[language] + "</span>" +
            "<input type=\"checkbox\" class=\"custom-control-input\" id=\"checkbox-" + language + "\" value=\"" + language + "\" onclick=\"setFilters('courses')\" checked>" +
            "<label class=\"custom-control-label\" for=\"checkbox-" + language + "\">" + getLanguageFromISOCode(language) + "</label></div>";
        document.querySelector("#languages-selector").innerHTML += line;
    });
}

function buildProgramsFinderFilters(programs) {

    programs.forEach(program => {

        // On parcourt les thématiques du programme et on peuple chaque compteur

        program.themes.forEach(theme => {

            if (!programsThemesCount.includes(theme)) {

                programsThemesCount.push(theme);
                programsThemesCount[theme] = 0;
            }

            programsThemesCount[theme]++;
        });

        // On peuple chaque compteur d'université

        if (!schoolsCount.includes(program.schoolShortName)) {

            schoolsCount.push(program.schoolShortName);
            schoolsCount[program.schoolShortName] = 0;
        }

        schoolsCount[program.schoolShortName]++;

        // On parcourt les disciplines du programme et on peuple chaque compteur

        if (!programsFieldsCount.includes(program.field)) {

            programsFieldsCount.push(program.field);
            programsFieldsCount[program.field] = 0;
        }

        programsFieldsCount[program.field]++;
    });

    // On trie les écoles, les thématiques et les disciplines alphabétiquement

    schoolsCount.sort((a, b) => { return a.localeCompare(b); }); // a.localCompare(b) permet de trier sans prendre en compte les accents (e/é/è)
    programsThemesCount.sort((a, b) => { return a.localeCompare(b); });
    programsFieldsCount.sort((a, b) => { return a.localeCompare(b); });

    // On crée les 2 filtres

    schoolsCount.forEach(school => {

        var schoolId = "school-" + school.toId();

        var line = "<div class=\"custom-control custom-checkbox\"><span class=\"float-right badge badge-light round\">" + schoolsCount[school] + "</span>" +
            "<input type=\"checkbox\" class=\"custom-control-input\" id=\"checkbox-" + schoolId + "\" value=\"" + schoolId + "\" onclick=\"setFilters('programs')\" checked>" +
            "<label class=\"custom-control-label\" for=\"checkbox-" + schoolId + "\">" + school + "</label></div>";
        document.querySelector("#programs-finder .schools-selector").innerHTML += line;
    });

    programsThemesCount.forEach(theme => {

        var themeId = "theme-" + theme.toId();

        var line = "<div class=\"custom-control custom-checkbox\"><span class=\"float-right badge badge-light round\">" + programsThemesCount[theme] + "</span>" +
            "<input type=\"checkbox\" class=\"custom-control-input\" id=\"checkbox-" + themeId + "\" value=\"" + themeId + "\" onclick=\"setFilters('programs')\" checked>" +
            "<label class=\"custom-control-label\" for=\"checkbox-" + themeId + "\">" + theme + "</label></div>";
        document.querySelector("#programs-finder .themes-selector").innerHTML += line;
    });

    programsFieldsCount.forEach(field => {

        var fieldId = "field-" + field.toId();

        var line = "<div class=\"custom-control custom-checkbox\"><span class=\"float-right badge badge-light round\">" + programsFieldsCount[field] + "</span>" +
            "<input type=\"checkbox\" class=\"custom-control-input\" id=\"checkbox-" + fieldId + "\" value=\"" + fieldId + "\" onclick=\"setFilters('programs')\" checked>" +
            "<label class=\"custom-control-label\" for=\"checkbox-" + fieldId + "\">" + field + "</label></div>";
        document.querySelector("#programs-finder .fields-selector").innerHTML += line;
    });
}

function buildCoursesFinderTable(courses) {

    $('[data-toggle="tooltip"]').tooltip();

    // On instancie la table

    table = new Tabulator("#courses-table-container", {

        data: courses,
        pagination: "local",
        paginationSize: 20,
        rowClick: function (e, row) { openModal(e, row); },
        locale: true,
        columns: [
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
            { title: "ID thèmes", field: "themesIds", sorter: "string", visible: false },
            {
                title: "Langues", field: "languages", headerSort: false, formatter: function (cell, formatterParams, onRendered) {

                    var cellValue = "";
                    cell.getValue().forEach(function (value, i, values) { cellValue += i < values.length - 1 ? getLanguageFromISOCode(value) + " | " : getLanguageFromISOCode(value); });

                    return cellValue;
                }
            },
        ]
    });

    buildFinderCount("courses");
}

function buildProgramsFinderTable(programs) {

    $('[data-toggle="tooltip"]').tooltip();

    // On instancie la table

    table = new Tabulator("#programs-table-container", {

        data: programs,
        pagination: "local",
        paginationSize: 20,
        initialSort: [{ column: "score", dir: "desc" }],
        rowClick: function (e, row) { openProgramModal(e, row); },
        responsiveLayout: "collapse",
        locale: true,
        columns: [
            { title: "Score", field: "score", sorter: "int" },
            { title: "Université", field: "schoolShortName", sorter: "string" },
            { title: "ID Université", field: "schoolId", sorter: "string", visible: false },
            { title: "Intitulé", field: "name", sorter: "string" },
            {
                title: "Code", field: "id", formatter: function (cell, formatterParams, onRendered) {

                    var url = cell.getRow().getData().url;
                    var value = cell.getValue();

                    return url == null ? value : "<a href=\'" + url + "' target='_blank'>" + value + "</a>";
                }
            },
            { title: "Discipline", field: "field", sorter: "string" },
            { title: "ID Discipline", field: "fieldId", sorter: "string", visible: false },
            {
                title: "Thématiques", field: "themes", headerSort: false, formatter: function (cell, formatterParams, onRendered) {

                    var cellValue = "";
                    cell.getValue().forEach(value => { cellValue += "<span class='badge badge-primary badge-theme'>" + value + "</span>&nbsp;"; });

                    return cellValue;
                }
            },
            { title: "ID thèmes", field: "themesIds", sorter: "string", visible: false }
        ]
    });

    buildFinderCount("programs");
}

function buildFinderCount(mode) {

    var type = mode == "courses" ? "cours" : "programmes";

    document.querySelector("#" + mode + "-finder" + " .results-count").innerHTML = "<strong>" + table.getDataCount("active") + " " + type + " sur un total de " + table.getDataCount() + "</strong>";
}

/* FILTRES */

function setFilters(mode) {

    // On chaîne les différents filtres

    if (mode == "courses") table.setFilter([getSelectedSchoolsFilter(mode), getSelectedThemesFilter(mode), getSelectedLanguagesFilter(), getSearchedNameFilter(mode)]);
    else if (mode == "programs") table.setFilter([getSelectedSchoolsFilter(mode), getSelectedThemesFilter(mode), getSelectedFieldsFilter(), getSearchedNameFilter(mode)]);

    // On recalcule le compteur de résultats

    buildFinderCount(mode);
}

function getSearchedNameFilter(mode) {

    return { field: "name", type: "like", value: document.querySelector("#" + mode + "-finder .name-search").value };
}

function getSelectedSchoolsFilter(mode) {

    var selectedSchools = "";

    document.querySelectorAll("#" + mode + "-finder .schools-selector input[type='checkbox']:checked").forEach(checkbox => {
        selectedSchools += checkbox.value + " ";
    });

    // Si aucune école n'est sélectionnée, on envoie un filtre qui fait d'office échouer la recherche ("-")

    return { field: "schoolId", type: "keywords", value: selectedSchools == "" ? "-" : selectedSchools.trim() };
}

function getSelectedThemesFilter(mode) {

    var selectedThemes = "";

    document.querySelectorAll("#" + mode + "-finder .themes-selector input[type='checkbox']:checked").forEach(checkbox => {
        selectedThemes += checkbox.value + " ";
    });

    // Si aucune thématique n'est sélectionnée, on envoie un filtre qui fait d'office échouer la recherche ("-")

    return { field: "themesIds", type: "keywords", value: selectedThemes == "" ? "@" : selectedThemes.trim() };
}

function getSelectedLanguagesFilter() {

    var selectedLanguages = "";

    document.querySelectorAll("#languages-selector input[type='checkbox']:checked").forEach(checkbox => {
        selectedLanguages += checkbox.value + " ";
    });

    // Si aucune école n'est sélectionnée, on envoie un filtre qui fait d'office échouer la recherche ("-")

    return { field: "languages", type: "keywords", value: selectedLanguages == "" ? "-" : selectedLanguages.trim() };
}

function getSelectedFieldsFilter() {

    var selectedFields = "";

    document.querySelectorAll("#programs-finder .fields-selector input[type='checkbox']:checked").forEach(checkbox => {
        selectedFields += checkbox.value + " ";
    });

    // Si aucune discipline n'est sélectionnée, on envoie un filtre qui fait d'office échouer la recherche ("-")

    return { field: "fieldId", type: "keywords", value: selectedFields == "" ? "-" : selectedFields.trim() };
}

function toggleFilters(mode) {

    var sidebar = document.querySelector("#" + mode + "-finder .sidebar");
    var button = document.querySelector("#" + mode + "-finder .show-filters");

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

function openProgramModal(e, row) {

    program = row.getData();

    // []courses
    // []ects
    // [] themes + scores (?)

    var themes = "";
    program.themes.forEach(value => { themes += "<span class='badge badge-primary badge-theme'>" + value + "</span>&nbsp;"; });
    document.getElementById("program-details-themes").innerHTML = themes;

    document.querySelector("#program-details-name").innerHTML = program.name;
    document.querySelector("#program-details-id").innerHTML = program.id;

    document.querySelector("#program-details-school").innerHTML = program.schoolShortName;
    document.querySelector("#program-details-cycle").innerHTML = program.cycle;
    document.querySelector("#program-details-campus").innerHTML = program.campus;
    document.querySelector("#program-details-faculty").innerHTML = program.faculty;
    document.querySelector("#program-details-field").innerHTML = program.field;
    document.querySelector("#program-details-score").innerHTML = program.score;
    

    $('#program-details-modal').modal();
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
                    file: school.file,
                    programFile: school.programFile
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
                            schoolId: "school-" + schools[i].shortName.toId(),
                            name: course.name,
                            shortName: course.id,
                            years: course.year,
                            teachers: course.teacher,
                            url: course.url,
                            languages: course.language,
                            themes: course.themes,
                            themesIds: course.themes.map(a => "theme-" + a.toId()),
                        });
                    });
                }
            });

        sessionStorage.courses = JSON.stringify(courses);
    }

    return JSON.parse(sessionStorage.courses);
}

async function getPrograms() {

    if (!sessionStorage.programs) {

        var programs = [];

        const schools = await getSchools();

        for (var i = 0; i < schools.length; i++) {

            await fetch("data/" + schools[i].programFile)
                .then(response => { return response.json(); })
                .then(data => {

                    data.forEach(p => {

                        programs.push({

                            id: p.id,
                            name: p.name,
                            url: p.url,
                            faculty: p.faculty,
                            campus: p.campus,
                            schoolShortName: schools[i].shortName,
                            schoolId: "school-" + schools[i].shortName.toId(),
                            courses: p.courses,
                            themes: p.themes,
                            themesIds: p.themes.map(a => "theme-" + a.toId()),
                            field: p.field,
                            fieldId: "field-" + p.field.toId(),
                            score: p.themes_scores.reduce((a, b) => a + b, 0),
                            cycle: p.cycle
                        });
                    });
                });
        }

        sessionStorage.programs = JSON.stringify(programs);
    }

    return JSON.parse(sessionStorage.programs);
}

/* HELPERS */

String.prototype.toId = function () {
    return this.toLowerCase().replace(/[^a-zA-Z0-9]+/g, "-");
};

function getLanguageFromISOCode(code) {

    dictionary = { "fr": "Français", "nl": "Néerlandais", "en": "Anglais", "de": "Allemand", "ar": "Arabe" };

    return dictionary.hasOwnProperty(code) ? dictionary[code] : "Inconnu";
}

document.querySelectorAll('.smooth-scroll').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});