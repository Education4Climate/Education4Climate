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
            availableLanguages: constants.AVAILABLE_LANGUAGES,
            menuItems: constants.MENU_ITEMS,
            currentMenuItem: "programs",
            cycles: [],
            errors: ""
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
        filteredPrograms() { /* Filter the sorted programs according to the schools/themes/fields selected and program name searched */

            if (this.dataLoaded) {

                this.currentPage = 0;
                let searchedName = this.searchedName.toLowerCase();

                return this.programs.slice()
                    .filter(program => this.selectedSchools.includes(program.schoolId))
                    .filter(program => this.selectedThemes.some(theme => program.themes.map(theme => theme.id).includes(theme)))
                    .filter(program => this.selectedFields.includes(program.fieldId))
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

            // detect current language and loads translations

            this.currentLanguage = translationManager.getLanguage();
            this.translations = await translationManager.loadTranslations();

            // loads schools data

            this.schools = await schoolsManager.getSchools();

            // loads programs data

            this.programs = await programsManager.getPrograms();
            this.totalProgramsCounts = await programsManager.getTotalProgramsCountBySchool();
            this.themes = await programsManager.getProgramsThemes();
            this.fields = await programsManager.getProgramsFields();
            this.cycles = await programsManager.getProgramsCycles();

            // sets the filters default selected schools / themes / fields

            this.selectedSchools = this.schools.map(school => { return school.id; });
            this.selectedThemes = this.themes.map(theme => { return theme.id; });
            this.selectedFields = this.fields.map(field => { return field.id; });

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
        translate(key, returnKeyIfNotFound) {

            return this.translations.length > 0 ? translationManager.translate(this.translations, key, this.currentLanguage, returnKeyIfNotFound) : "";
        },
        setLanguage(language) {

            this.currentLanguage = language;
            translationManager.setLanguage(language);
        }
    }
});

app.mount("#app");