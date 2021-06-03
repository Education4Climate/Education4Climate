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
            selectedSchools: [],
            selectedThemes: [],
            selectedFields: [],
            selectedLanguages: [],
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
        filteredPrograms() { /* Filter the sorted programs according to the schools/themes/fields selected and program name searched */

            if (this.dataLoaded) {

                this.currentPage = 0;
                let searchedName = this.searchedName.toLowerCase();

                return this.programs.slice()
                    .filter(program => this.selectedSchools.includes(program.schoolId))
                    .filter(program => this.selectedThemes.some(theme => program.themes.map(theme => theme.id).includes(theme)))
                    .filter(program => this.selectedFields.includes(program.fieldId))
                    .filter(program => this.selectedLanguages.some(language => program.languages.includes(language)))
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

            this.selectedSchools = this.schools.map(school => { return school.id; });
            this.selectedThemes = this.themes.map(theme => { return theme.id; });
            this.selectedFields = this.fields.map(field => { return field.id; });
            this.selectedLanguages = this.languages.map(language => { return language.id; });
            
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
        }
    }
});

app.mount("#app");