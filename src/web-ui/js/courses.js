/*jshint esversion: 8 */

/**
 * @file Manages the courses finder tool.
 * @author Quentin V.
 */

import * as constants from './constants.js';
import * as schoolsManager from './managers/schools-manager.js';
import * as coursesManager from './managers/courses-manager.js';
import * as translationManager from "./managers/translation-manager.js";

var app = Vue.createApp({
    el: '#app',
    data() {
        return {
            schools: [],
            courses: [],
            displayedCourses: [],
            totalCoursesCounts: [],
            themes: [],
            languages: [],
            dataLoaded: false,
            selectedSchools: [],
            selectedThemes: [],
            selectedLanguages: [],
            searchedName: "",
            currentPage: 0,
            showResponsiveFilters: false,
            currentLanguage: "fr",
            translations: [],
            availableLanguages: constants.AVAILABLE_LANGUAGES,
            menuItems: constants.MENU_ITEMS,
            currentMenuItem: "courses"
        };
    },
    computed: {
        sortedSchools() { /* Sort the schools alphabetically for display */

            return this.schools.slice().sort((a, b) => { return a.shortName.localeCompare(b.shortName); });
        },
        sortedThemes() { /* Sort the themes DESC on the total count for display */

            return this.themes.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedLanguages() { /* Sort the languages DESC on the total count for display */

            return this.languages.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedCourses() { /* Sort the courses DESC on their score for display */

            return this.courses.slice().sort((a, b) => { return b.themes.length - a.themes.length; });
        },
        filteredCourses() { /* Filter the sorted courses according to the schools/themes/languages selected and course name searched */

            this.currentPage = 0;

            return this.sortedCourses.slice()
                .filter(course => this.selectedSchools.includes(course.schoolId))
                .filter(course => this.selectedThemes.some(theme => course.themes.includes(theme)))
                .filter(course => this.selectedLanguages.some(language => course.languages.includes(language)))
                .filter(course => course.name.toLowerCase().includes(this.searchedName.toLowerCase()));
        },
        paginatedCourses() { /* Paginate the filtered courses */

            if (this.currentPage == 0) {
                this.displayedCourses = [];
            }

            const start = this.currentPage * constants.PAGE_SIZE;
            const end = start + constants.PAGE_SIZE;
            let current = start;

            while (current < end && this.filteredCourses[end - (end - current)]) {
                this.displayedCourses.push(this.filteredCourses[end - (end - current)]);
                current++;
            }

            return this.displayedCourses;
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

        await coursesManager.getCourses().then(courses => this.courses = courses);
        await coursesManager.getTotalCoursesCounts().then(totalCoursesCounts => this.totalCoursesCounts = totalCoursesCounts);

        await coursesManager.getCoursesThemes().then(themes => {
            this.themes = themes;
            this.selectedThemes = this.themes.map(theme => { return theme.id; }); // sets the default selected themes
        });

        await coursesManager.getCoursesLanguages().then(languages => {
            this.languages = languages;
            this.selectedLanguages = this.languages.map(language => { return language.id; }); // sets the default selected languages
        });

        this.dataLoaded = true;
    },
    methods: {
        loadMore() {

            this.currentPage = this.displayedCourses.length < this.filteredCourses.length ? this.currentPage + 1 : this.currentPage;
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