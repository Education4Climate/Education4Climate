/*jshint esversion: 8 */

/**
 * @file Manages the programs finder tool.
 * @author Quentin V.
 */

import baseApp from "./base-app.js";
import * as constants from './constants.js';
import SchoolsManager from './managers/schools-manager.js';
import ProgramsManager from './managers/programs-manager.js';

var app = Vue.createApp({
    mixins: [baseApp],
    el: '#app',
    data() {
        return {
            schools: [],
            programs: [],
            displayedPrograms: [],
            themes: [],
            fields: [],
            languages: [],
            selectedFields: [],
            selectedCycles: [],
            searchedName: "",
            currentPage: 0,
            showResponsiveFilters: false,
            currentMenuItem: "programs",
            cycles: [],
            schoolsManager: new SchoolsManager(),
            programsManager: new ProgramsManager()
        };
    },
    computed: {
        selectedAllUniversities() {
            return this.selectedUniversities && this.selectedUniversities.length >= this.schools.filter(school => school.type == "university").length;
        },
        selectedAllHighSchools() {
            return this.selectedHighSchools && this.selectedHighSchools.length >= this.schools.filter(school => school.type == "highschool").length;
        },
        selectedAllThemes() {
            return this.selectedThemes && this.selectedThemes.length == this.themes.length;
        },
        selectedAllFields() {
            return this.selectedFields && this.selectedFields.length == this.fields.length;
        },
        selectedAllLanguages() {
            return this.selectedLanguages && this.selectedLanguages.length == this.languages.length;
        },
        selectedAllCycles() {
            return this.selectedCycles && this.selectedCycles.length == this.cycles.length;
        },
        sortedSchools() { /* Sort the schools alphabetically for display */

            return this.schools.slice().sort((a, b) => { return a.shortName.localeCompare(b.shortName); });
        },
        sortedThemes() { /* Sort the themes DESC on the total count for display */

            return this.themes.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedFields() { /* Sort the fields DESC on the total count for display */

            return this.fields.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedLanguages() { /* Sort the languages DESC on the total count for display */

            return this.languages.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedCycles() { /* Sort the cycles DESC on the total count for display */

            return this.cycles.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        filteredPrograms() { /* Filter the sorted programs according to the schools/themes/fields selected and program name searched */

            if (this.dataLoaded) {

                this.currentPage = 0;
                let searchedName = this.searchedName.toLowerCase();

                return this.programs.slice()
                    .filter(program => this.selectedUniversities.includes(program.schoolId) || this.selectedHighSchools.includes(program.schoolId))
                    .filter(program => this.selectedThemes.some(selectedTheme => program.themes.map(theme => this.themes[theme.id].name).includes(selectedTheme)))
                    .filter(program => this.selectedFields.some(field => program.fields.includes(field)))
                    .filter(program => this.selectedLanguages.some(selectedLanguage => program.languages.map(language => this.languages[language].name).includes(selectedLanguage)))
                    .filter(program => this.selectedCycles.includes(program.cycleId))
                    .filter(program => program.name.toLowerCase().includes(searchedName));
            }

            return true;
        },
        sortedPrograms() { /* Step 2 : sort the filtered programs DESC on their score for display */

            return this.dataLoaded ? this.filteredPrograms.slice().sort((a, b) => { return b.score - a.score; }) : true;
        },
        paginatedPrograms() { /* Step 3 : paginate the sorted programs */

            if (this.currentPage == 0) {
                this.displayedPrograms = [];
            }

            const start = this.currentPage * constants.PAGE_SIZE;
            const end = start + constants.PAGE_SIZE;
            let current = start;

            while (current < end && this.sortedPrograms[end - (end - current)]) {
                this.displayedPrograms.push(this.sortedPrograms[end - (end - current)]);
                current++;
            }

            return this.displayedPrograms;
        },
        programsCountsBySchool() { // Computes the total counts of programs by school

            const programsCountsBySchool = [];

            this.schools.forEach(school => {
                programsCountsBySchool[school.id] = this.programs.filter(program => school.id == program.schoolId).length;
            });

            return programsCountsBySchool;
        }
    },
    mounted() {

        var intersectionObserver = new IntersectionObserver(entries => {

            if (entries[0].intersectionRatio <= 0) return;

            this.loadMore();
        }, { rootMargin: "200px" });

        intersectionObserver.observe(this.$refs.loadMore);
    },
    async created() {

        try {

            // loads schools data

            this.schools = await this.schoolsManager.getSchools();

            // loads programs data

            this.programs = await this.programsManager.getPrograms();
            this.themes = await this.programsManager.getProgramsThemes();
            this.fields = await this.programsManager.getProgramsFields();
            this.cycles = await this.programsManager.getProgramsCycles();
            this.languages = await this.programsManager.getProgramsLanguages();

            // sets the filters default selected schools / themes / fields

            this.selectedUniversities = this.selectedUniversities ? this.selectedUniversities : this.schools.filter(school => school.type == "university").map(school => { return school.id; });
            this.selectedHighSchools = this.selectedHighSchools ? this.selectedHighSchools : this.schools.filter(school => school.type == "highschool").map(school => { return school.id; });
            this.selectedThemes = this.selectedThemes ? this.selectedThemes : this.themes.map(theme => { return theme.name; });
            this.selectedFields = this.fields.map(field => { return field.id; });
            this.selectedLanguages = this.selectedLanguages ? this.selectedLanguages : this.languages.map(language => { return language.name; });
            this.selectedCycles = this.cycles.map(cycle => { return cycle.id; });

            // hides the loader

            this.dataLoaded = true;
        }
        catch (error) {
            console.log(error);
            this.errors += error;
        }
    },
    methods: {
        loadMore() {

            this.currentPage = this.dataLoaded && this.displayedPrograms.length < this.sortedPrograms.length ? this.currentPage + 1 : this.currentPage;
        },
        toggleCheckAllUniversities() {

            this.selectedUniversities = this.selectedAllUniversities ? [] : this.schools.filter(school => school.type == "university").map(school => { return school.id; });
        },
        toggleCheckAllHighSchools() {

            this.selectedHighSchools = this.selectedAllHighSchools ? [] : this.schools.filter(school => school.type == "highschool").map(school => { return school.id; });
        },
        toggleCheckAllThemes() {

            this.selectedThemes = this.selectedAllThemes ? [] : this.themes.map(theme => { return theme.name; });
        },
        toggleCheckAllFields() {

            this.selectedFields = this.selectedAllFields ? [] : this.fields.map(field => { return field.id; });
        },
        toggleCheckAllLanguages() {

            this.selectedLanguages = this.selectedAllLanguages ? [] : this.languages.map(language => { return language.name; });
        },
        toggleCheckAllCycles() {

            this.selectedCycles = this.selectedAllCycles ? [] : this.cycles.map(cycle => { return cycle.id; });
        },
        exportCSV() {

            const separator = ",";

            let csv = "\uFEFF"; // BOM : force UTF8 encoding
            csv += "Name" + separator + "Code" + separator + "Faculties" + separator + "School" + separator + "Campuses" + separator;

            this.themes.forEach((theme) => { csv += "Theme:" + theme.name + separator; });
            this.languages.forEach((language) => { csv += "Language:" + language.name + separator; });
            this.fields.forEach((field) => { csv += "Field:" + field.name + separator; });

            csv += "Score" + separator + "Cycle" + separator + "Url\n";

            this.sortedPrograms.forEach((program) => {

                csv += "\"" + program.name.replaceAll("\"", "\"\"") + "\"" + separator;
                csv += "\"" + program.code + "\"" + separator;
                csv += "\"" + program.faculties.join("|") + "\"" + separator;
                csv += this.schools[program.schoolId].shortName + separator;
                csv += "\"" + program.campuses.join("|") + "\"" + separator;

                this.themes.forEach((theme) => {

                    var i = program.themes.findIndex((t) => this.themes[t.id].name == theme.name);
                    csv += i > -1 ? program.themes[i].score + separator : 0 + separator;
                });

                this.languages.forEach((language) => { csv += program.languages.map(l => this.languages[l].name).includes(language.name) ? "true" + separator : "false" + separator; })
                this.fields.forEach((field) => { csv += program.fields.map(f => this.fields[f].name).includes(field.name) ? "true" + separator : "false" + separator; })

                csv += program.score + separator;
                csv += this.cycles[program.cycleId].name + separator;
                csv += program.url + "\n";
            });

            const anchor = document.createElement('a');
            anchor.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
            anchor.target = '_blank';
            anchor.download = 'education4climate-programmes.csv';
            anchor.click();
        }
    }
});

app.mount("#app");