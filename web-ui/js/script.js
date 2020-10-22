var schools = [uantwerp, ucl, ulb, umons, unamur];
var courses = [];
var table;
var themes = [];
var languages = [];

window.addEventListener('load', function () {

    schools.forEach(school => {

        schools[school] = 0;

        school.courses.forEach(course => {

            // On agrège les données de toutes les écoles dans un même tableau

            courses.push({

                schoolShortName: school.shortName,
                name: course.name,
                shortName: course.shortName,
                years: course.years,
                teachers: course.teachers,
                credits: course.credits,
                languages: course.languages,
                themes: course.themes,
                abstract: course.abstract,
                campus: course.campus,
                shiftScore: course.shiftScore,
                climateScore: course.climateScore,
                url: course.url
            });

            // On parcourt les thématiques du cours pour pouvoir peupler les filtres

            course.themes.forEach(theme => {

                if (!themes.includes(theme)) {

                    themes.push(theme);
                    themes[theme] = 1;
                }

                themes[theme]++;
            });

            course.languages.forEach(language => {

                if (!languages.includes(language)) {

                    languages.push(language);
                    languages[language] = 1;
                }

                languages[language]++;
            });

            schools[school]++;
        });

        // On crée chaque filtre qui permet de choisir l'université

        var line = "<label class='school-selector'><input type='checkbox' value='" + school.shortName + "' onclick='setFilters()' checked><span class='label-body'>" + school.shortName + "&nbsp;<h6>(" + schools[school] + ")<h6></span></label>";
        document.querySelector("#schools-selector").innerHTML += line;
    });

    // On trie les thématiques et les langues alphabétiquement avant de créer les filtres

    themes.sort((a, b) => { return a.localeCompare(b); }); // a.localCompare(b) permet de trier sans prendre en compte les accents (e/é/è)
    languages.sort((a, b) => { return a.localeCompare(b); });

    themes.forEach(theme => {

        var line = "<label class='theme-selector'><input type='checkbox' value='" + theme + "' onclick='setFilters()' checked><span class='label-body'>" + theme + "&nbsp;<h6>(" + themes[theme] + ")</h6></span></label>";
        document.querySelector("#themes-selector").innerHTML += line;
    });

    languages.forEach(language => {

        var line = "<label class='language-selector'><input type='checkbox' value='" + language + "' onclick='setFilters()' checked><span class='label-body'>" + getLanguageFromISOCode(language) + "&nbsp;<h6>(" + languages[language] + ")</h6></span></label>";
        document.querySelector("#languages-selector").innerHTML += line;
    });

    // On instancie la table

    table = new Tabulator("#courses-table-container", {

        data: courses,
        columns: [
            { title: "Score", field: "climateScore", formatter: "star", sorter: "number", tooltip: true },
            { title: "Université", field: "schoolShortName", sorter: "string" },
            { title: "Intitulé", field: "name", sorter: "string" },
            { title: "Code", field: "shortName", formatter: "link", formatterParams: { labelField: "shortName", urlField: "url", target: "_blank" } },
            {
                title: "Thématiques", field: "themes", headerSort: false, formatter: function (cell, formatterParams, onRendered) {

                    var cellValue = "";
                    cell.getValue().forEach(value => { cellValue += "<span class='theme'>" + value + "</span>&nbsp;"; });
                    
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
        ],
        pagination: "local",
        paginationSize: 10,
        initialSort: [
            { column: "climateScore", dir: "desc" }
        ],
        rowClick: function (e, row) { openModal(e, row); },
        locale: true
    });

    displayResultsCount();

    document.getElementById("course-details-modal").addEventListener('click', e => {

        if (event.target.id !== "youtube-logo" && event.target.id !== "spotify-logo" && event.target.id !== "bandcamp-logo") {
            closeModal();
        }
    });
});

function displayResultsCount() {

    document.getElementById("results-count").innerHTML = "<strong>" + table.getDataCount("active") + " cours sur un total de " + table.getDataCount() + " correspondent à vos critères</strong>";
}

function getLanguageFromISOCode(code) {

    dictionary = { "fr": "Français", "nl": "Néerlandais", "en": "Anglais", "de": "Allemand" };

    return dictionary.hasOwnProperty(code) ? dictionary[code] : "Inconnu";
}

/* Filtres */

function setFilters() {

    // On chaîne les différents filtres

    table.setFilter([getSelectedSchoolsFilter(), getSelectedThemesFilter(), getSelectedLanguagesFilter(), getSearchedCourseFilter()]);

    // On recalcule le compteur de résultats

    displayResultsCount();
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

/* Modal */

function openModal(e, row) {

    course = row.getData();

    document.getElementById("course-name").innerHTML = course.name;
    document.getElementById("course-short-name").innerHTML = "[" + course.shortName + "]"
    document.getElementById("course-years").innerHTML = course.years;
    document.getElementById("course-abstract").innerHTML = course.abstract;
    document.getElementById("course-teachers").innerHTML = course.teachers;
    document.getElementById("course-themes").innerHTML = course.themes;
    document.getElementById("course-credits").innerHTML = course.credits;
    document.getElementById("course-languages").innerHTML = course.languages;
    document.getElementById("course-campus").innerHTML = course.campus;
    document.getElementById("course-climate-score").innerHTML = course.climateScore;
    document.getElementById("course-shift-score").innerHTML = course.shiftScore;
    document.getElementById("course-url").innerHTML = "<a href='" + course.url + "' target='_blank'>Plus de détails</a>";

    document.getElementById("course-details-modal").style.display = "block";
}

function closeModal() {
    document.getElementById("course-details-modal").style.display = "none";
}