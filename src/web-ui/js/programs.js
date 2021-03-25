/*jshint esversion: 8 */

/**
 * @file Manages the programs finder tool.
 * @author Quentin V.
 */

import * as constants from './constants.js';
import * as schoolsManager from './managers/schools-manager.js';
import * as programsManager from './managers/programs-manager.js';
import * as translationManager from "./managers/translation-manager.js";

var app = Vue.createApp({
    el: '#app',
    data() {
        return {
            schools: [],
            programs: [],
            displayedPrograms: [],
            totalProgramsCounts: [],
            themes: [],
            fields: [],
            dataLoaded: false,
            selectedSchools: [],
            selectedThemes: [],
            selectedFields: [],
            searchedName: "",
            currentPage: 0,
            showResponsiveFilters: false,
            currentLanguage: "fr",
            translations: [],
            availableLanguages: constants.AVAILABLE_LANGUAGES
        };
    },
    computed: {
        sortedSchools() { /* Sort the schools alphabetically for display */

            return this.schools.slice().sort((a, b) => { return a.shortName.localeCompare(b.shortName); });
        },
        sortedThemes() { /* Sort the themes DESC on the total count for display */

            return this.themes.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedFields() { /* Sort the fields DESC on the total count for display */

            return this.fields.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedPrograms() { /* Sort the programs DESC on their score for display */

            return this.programs.slice().sort((a, b) => { return b.score - a.score; });
        },
        filteredPrograms() { /* Filter the sorted programs according to the schools/themes/fields selected and program name searched */

            this.currentPage = 0;

            return this.sortedPrograms.slice()
                .filter(program => this.selectedSchools.includes(program.schoolId))
                .filter(program => this.selectedThemes.some(theme => program.themes.map(theme => theme.id).includes(theme)))
                .filter(program => this.selectedFields.includes(program.fieldId))
                .filter(program => program.name.toLowerCase().includes(this.searchedName.toLowerCase()));
        },
        paginatedPrograms() { /* Paginate the filtered programs */

            if (this.currentPage == 0) {
                this.displayedPrograms = [];
            }

            const start = this.currentPage * constants.PAGE_SIZE;
            const end = start + constants.PAGE_SIZE;
            let current = start;

            while (current < end && this.filteredPrograms[end - (end - current)]) {
                this.displayedPrograms.push(this.filteredPrograms[end - (end - current)]);
                current++;
            }

            return this.displayedPrograms;
        }
    },
    mounted() {

        window.addEventListener("scroll", () => {

            let scrollTop = window.scrollY;
            let docHeight = document.body.offsetHeight;
            let winHeight = window.innerHeight;
            let scrollPercent = scrollTop / (docHeight - winHeight);
            let scrollPercentRounded = Math.round(scrollPercent * 100);

            if (scrollPercentRounded === 100) {
                this.loadMore();
            }
        });

        this.loadMore();
    },
    async created() {

        this.currentLanguage = translationManager.getLanguage();

        await translationManager.loadTranslations().then(translations => {
            this.translations = translations;
        });

        await schoolsManager.getSchools().then(schools => {
            this.schools = schools;
            this.selectedSchools = this.schools.map(school => { return school.id; }); // sets the default selected fields
        });

        await programsManager.getPrograms().then(programs => this.programs = programs);
        await programsManager.getTotalProgramsCountBySchool().then(totalProgramsCounts => this.totalProgramsCounts = totalProgramsCounts);

        await programsManager.getProgramsThemes().then(themes => {
            this.themes = themes;
            this.selectedThemes = this.themes.map(theme => { return theme.id; }); // sets the default selected themes
        });

        await programsManager.getProgramsFields().then(fields => {
            this.fields = fields;
            this.selectedFields = this.fields.map(field => { return field.id; }); // sets the default selected fields
        });

        this.dataLoaded = true;
    },
    methods: {
        loadMore() {

            this.currentPage = this.displayedPrograms.length < this.filteredPrograms.length ? this.currentPage + 1 : this.currentPage;
        },
        translate(key) {

            let corpus = this.translations.find(translation => translation.language === this.currentLanguage);
            return key.split('.').reduce((obj, i) => obj[i], corpus.translations);
        },
        setLanguage(language) {
            this.currentLanguage = language;
            translationManager.setLanguage(language);
        }
    }
});

app.mount("#app");