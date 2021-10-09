/*jshint esversion: 8 */

/**
 * @file Manages the courses finder tool.
 * @author Quentin V.
 */

import baseApp from "./base-app.js";
import * as constants from './constants.js';
import SchoolsManager from './managers/schools-manager.js';
import CoursesManager from './managers/courses-manager.js';
import ProgramsManager from './managers/programs-manager.js';

var app = Vue.createApp({
    mixins: [baseApp],
    el: '#app',
    data() {
        return {
            schools: [],
            courses: [],
            displayedCourses: [],
            totalCoursesCounts: [],
            themes: [],
            languages: [],
            searchedName: "",
            currentPage: 0,
            showResponsiveFilters: false,
            currentMenuItem: "courses",
            searchedProgramCode: new URL(document.location).searchParams.get("programCode"),
            searchedProgram: {},
            searchedSchoolId: new URL(document.location).searchParams.get("schoolId"),
            programs: [],
            schoolsManager: new SchoolsManager(),
            programsManager: new ProgramsManager(),
            coursesManager: new CoursesManager()
        };
    },
    computed: {
        selectedAllSchools() {
            return this.selectedSchools && this.selectedSchools.length == this.schools.length;
        },
        selectedAllThemes() {
            return this.selectedThemes && this.selectedThemes.length == this.themes.length;
        },
        selectedAllLanguages() {
            return this.selectedLanguages && this.selectedLanguages.length == this.languages.length;
        },
        sortedSchools() { /* Sort the schools alphabetically for display */

            return this.schools.slice().sort((a, b) => { return a.shortName.localeCompare(b.shortName); });
        },
        sortedThemes() { /* Sort the themes DESC on the total count for display */

            return this.themes.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedLanguages() { /* Sort the languages DESC on the total count for display */

            return this.languages.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        filteredCourses() { /* Step 1 : filter the courses */

            if (this.dataLoaded) {

                this.currentPage = 0;
                let searchedName = this.searchedName.toLowerCase();
                this.searchedProgram = this.programs.find(program => program.code === this.searchedProgramCode);

                return this.courses.slice()
                    .filter(course => this.selectedSchools.includes(course.schoolId))
                    .filter(course => this.selectedThemes.some(selectedTheme => course.themes.map(theme => this.themes[theme].name).includes(selectedTheme)))
                    .filter(course => this.selectedLanguages.some(selectedLanguage => course.languages.map(language => this.languages[language].name).includes(selectedLanguage)))
                    .filter(course => course.name.toLowerCase().includes(searchedName))
                    .filter(course => this.searchedProgram ? this.searchedProgram.courses.includes(course.code) : true);
            }

            return true;
        },
        sortedCourses() { /* Step 2 : sort the filtered courses DESC on their score for display */

            return this.dataLoaded ? this.filteredCourses.slice().sort((a, b) => b.dedicated - a.dedicated || b.themes.length - a.themes.length) : true;
        },
        paginatedCourses() { /* Step 3 : paginate the sorted courses */

            if (this.currentPage == 0) {
                this.displayedCourses = [];
            }

            const start = this.currentPage * constants.PAGE_SIZE;
            const end = start + constants.PAGE_SIZE;
            let current = start;

            while (current < end && this.sortedCourses[end - (end - current)]) {
                this.displayedCourses.push(this.sortedCourses[end - (end - current)]);
                current++;
            }

            return this.displayedCourses;
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

            // if both parameters schoolId and programCode are passed in the url,
            // loads the programs and find the right school/program

            let searchedSchool = this.searchedSchoolId && this.searchedProgramCode ? this.schools.find(school => school.id == this.searchedSchoolId) : null;
            this.programs = await this.programsManager.getPrograms();
            this.searchedProgram = this.programs.find(program => program.code === this.searchedProgramCode);

            // loads courses data

            this.courses = await this.coursesManager.getCourses();
            this.totalCoursesCounts = await this.coursesManager.getTotalCoursesCounts();
            this.themes = await this.coursesManager.getCoursesThemes();
            this.languages = await this.coursesManager.getCoursesLanguages();

            // sets the filters default selected schools / themes / languages

            this.selectedSchools = searchedSchool ? [searchedSchool.id] : this.selectedSchools ? this.selectedSchools : this.schools.map(school => { return school.id; });
            this.selectedThemes = this.selectedThemes ? this.selectedThemes : this.themes.map(theme => { return theme.name; });
            this.selectedLanguages = this.selectedLanguages ? this.selectedLanguages : this.languages.map(language => { return language.name; });

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

            this.currentPage = this.dataLoaded && this.displayedCourses.length < this.sortedCourses.length ? this.currentPage + 1 : this.currentPage;
        },
        toggleCheckAllSchools() {

            this.selectedSchools = this.selectedAllSchools ? [] : this.schools.map(school => { return school.id; });
        },
        toggleCheckAllThemes() {

            this.selectedThemes = this.selectedAllThemes ? [] : this.themes.map(theme => { return theme.name; });
        },
        toggleCheckAllLanguages() {

            this.selectedLanguages = this.selectedAllLanguages ? [] : this.languages.map(language => { return language.name; });
        },
        exportCSV() {

            const separator = ",";

            let csv = ["Name", "Code", "Year", "School", "Dedicated", "Themes", "Languages", "Teachers", "Url"].join(separator) + "\n";

            this.sortedCourses.forEach((course) => {
                csv += "\"" + course.name + "\"" + separator;
                csv += "\"" + course.code + "\"" + separator;
                csv += course.year + separator;
                csv += this.schools[course.schoolId].shortName + separator;
                csv += course.dedicated + separator;
                csv += course.themes.map(theme => this.themes[theme].name).join("|") + separator;
                csv += course.languages.map(language => this.languages[language].name).join("|") + separator;
                csv += course.teachers.join("|") + separator;
                csv += course.url;
                csv += "\n";
            });

            const anchor = document.createElement('a');
            anchor.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
            anchor.target = '_blank';
            anchor.download = 'education4climate-courses.csv';
            anchor.click();
        }
    }
});

app.mount("#app");