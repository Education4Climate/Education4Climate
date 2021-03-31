/*jshint esversion: 8 */

/**
 * @file Manages the teachers directory tool.
 * @author Quentin V.
 */

import * as constants from './constants.js';
import * as schoolsManager from './managers/schools-manager.js';
import * as translationManager from "./managers/translation-manager.js";
import * as teachersManager from "./managers/teachers-manager.js";
import * as coursesManager from './managers/courses-manager.js';

var app = Vue.createApp({
    el: '#app',
    data() {
        return {
            schools: [],
            courses: [],
            teachers: [],
            displayedTeachers: [],
            themes: [],
            dataLoaded: false,
            selectedSchools: [],
            currentPage: 0,
            showResponsiveFilters: false,
            currentLanguage: "fr",
            translations: [],
            availableLanguages: constants.AVAILABLE_LANGUAGES,
            menuItems: constants.MENU_ITEMS,
            currentMenuItem: "teachers",
            teachersCountsBySchool: [],
            teachersCountsByTheme: [],
            alphabet: ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
            firstLetterSearched: "",
            searchedName: "",
            selectedThemes: []
        };
    },
    computed: {
        sortedSchools() { /* Sort the schools alphabetically for display */

            return this.schools.slice().sort((a, b) => { return a.shortName.localeCompare(b.shortName); });
        },
        sortedThemes() { /* Sort the themes DESC on the total count for display */

            return this.themes.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        filteredTeachers() { /* Filter the sorted teachers  according to the schools/themes selected and teacher name searched */

            if (this.dataLoaded) {

                this.currentPage = 0;
                let searchedName = this.searchedName.toLowerCase();

                return this.teachers.slice()
                    .filter(teacher => this.selectedSchools.includes(teacher.schoolId))
                    .filter(teacher => this.selectedThemes.some(theme => teacher.themesIds.includes(theme)))
                    .filter(teacher => teacher.name.toLowerCase().includes(searchedName))
                    .filter(teacher => !this.firstLetterSearched || !teacher.name[0] ? true : teacher.name[0].toUpperCase() === this.firstLetterSearched);
            }

            return true;
        },
        sortedTeachers() { /* Step 2 : sort the filtered teachers alphabetically for display */

            return this.dataLoaded ? this.filteredTeachers.slice().sort((a, b) => { return a.name.localeCompare(b.name); }) : true;
        },
        paginatedTeachers() { /* Step 3 : paginate the sorted teachers */

            if (this.currentPage == 0) {
                this.displayedTeachers = [];
            }

            const start = this.currentPage * constants.PAGE_SIZE;
            const end = start + constants.PAGE_SIZE;
            let current = start;

            while (current < end && this.sortedTeachers[end - (end - current)]) {
                this.displayedTeachers.push(this.sortedTeachers[end - (end - current)]);
                current++;
            }

            return this.displayedTeachers;
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

        await translationManager.loadTranslations().then(translations => { this.translations = translations; });

        await schoolsManager.getSchools().then(schools => {

            this.schools = schools;
            this.selectedSchools = this.schools.map(school => { return school.id; }); // sets the default selected fields
        });

        await coursesManager.getCourses().then(courses => this.courses = courses);

        await coursesManager.getCoursesThemes().then(themes => {
            this.themes = themes;
            this.selectedThemes = this.themes.map(theme => { return theme.id; }); // sets the default selected themes
        });

        await teachersManager.getTeachers().then(teachers => {

            this.teachers = teachers;

            this.schools.forEach(school => {
                this.teachersCountsBySchool[school.id] = teachers.filter(teacher => school.id == teacher.schoolId).length;
            });

            this.themes.forEach(theme => {
                this.teachersCountsByTheme[theme.id] = teachers.filter(teacher => teacher.themesIds.includes(theme.id)).length;
            });
        });

        this.dataLoaded = true;
    },
    methods: {
        loadMore() {

            this.currentPage = this.dataLoaded && this.displayedTeachers.length < this.sortedTeachers.length ? this.currentPage + 1 : this.currentPage;
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