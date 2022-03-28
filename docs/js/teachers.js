/*jshint esversion: 8 */

/**
 * @file Manages the teachers directory tool.
 * @author Quentin V.
 */

import baseApp from "./base-app.js";
import * as constants from './constants.js';
import SchoolsManager from './managers/schools-manager.js';
import TeachersManager from "./managers/teachers-manager.js";
import CoursesManager from './managers/courses-manager.js';

var app = Vue.createApp({
    mixins: [baseApp],
    el: '#app',
    data() {
        return {
            schools: [],
            courses: [],
            teachers: [],
            displayedTeachers: [],
            themes: [],
            currentPage: 0,
            showResponsiveFilters: false,
            currentMenuItem: "teachers",
            alphabet: ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"],
            firstLetterSearched: "",
            searchedName: "",
            teachersManager: new TeachersManager(),
            schoolsManager: new SchoolsManager(),
            coursesManager: new CoursesManager()
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
                    .filter(teacher => this.selectedUniversities.includes(teacher.schoolId) || this.selectedHighSchools.includes(teacher.schoolId))
                    .filter(teacher => this.selectedThemes.some(selectedTheme => teacher.themesIds.map(theme => this.themes[theme].name).includes(selectedTheme)))                    
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
        },
        teachersCountsBySchool() { // Computes the total counts of teachers by school

            const teachersCountsBySchool = [];

            this.schools.forEach(school => {
                teachersCountsBySchool[school.id] = this.teachers.filter(teacher => school.id == teacher.schoolId).length;
            });

            return teachersCountsBySchool;
        },
        teachersCountsByTheme() { // Computes the total counts of teachers by theme

            const teachersCountsByTheme = [];

            this.themes.forEach(theme => {
                teachersCountsByTheme[theme.id] = this.teachers.filter(teacher => teacher.themesIds.includes(theme.id)).length;
            });

            return teachersCountsByTheme;
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

            // loads schools, courses and teachers data

            this.schools = await this.schoolsManager.getSchools();
            this.courses = await this.coursesManager.getCourses();
            this.themes = await this.coursesManager.getCoursesThemes();
            this.teachers = await this.teachersManager.getTeachers();

            // sets the filters default selected schools / themes

            this.selectedUniversities = this.selectedUniversities ? this.selectedUniversities : this.schools.filter(school => school.type == "university").map(school => { return school.id; });
            this.selectedHighSchools = this.selectedHighSchools ? this.selectedHighSchools : this.schools.filter(school => school.type == "highschool").map(school => { return school.id; });            
            this.selectedThemes = this.selectedThemes ? this.selectedThemes : this.themes.map(theme => { return theme.name; });

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

            this.currentPage = this.dataLoaded && this.displayedTeachers.length < this.sortedTeachers.length ? this.currentPage + 1 : this.currentPage;
        },
        toggleCheckAllUniversities() {

            this.selectedUniversities = this.selectedAllUniversities ? [] : this.schools.filter(school => school.type == "university").map(school => { return school.id; });
        },
        toggleCheckAllHighSchools() {

            this.selectedHighSchools = this.selectedAllHighSchools ? [] : this.schools.filter(school => school.type == "highschool").map(school => { return school.id; });
        },
        toggleCheckAllThemes() {

            this.selectedThemes = this.selectedAllThemes ? [] : this.themes.map(theme => { return theme.name; });
        }        
    }
});

app.mount("#app");