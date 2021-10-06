/*jshint esversion: 8 */

/**
 * @file Manages the courses data.
 * @author Quentin V.
 */

import * as constants from '../constants.js';
import SchoolsManager from './schools-manager.js';

class CoursesManager {

    constructor() {

        this.totalCoursesCounts = [];
        this.coursesThemes = [];
        this.coursesLanguages = [];
        this.schoolsManager = new SchoolsManager();
    }

    async getCourses() {

        if (!sessionStorage.courses) {

            var courses = [];

            const schools = await this.schoolsManager.getSchools();

            var urls = schools.map(school => constants.DATA_FOLDER + "/" + school.coursesFile);

            // Getting all the .json in parallel
            var data = await Promise.all(urls.map(url => fetch(url).then((response) => response.json())));

            data.forEach((c, i) => {

                c.forEach((course, j) => {

                    courses.push({

                        id: courses.length,
                        teachers: this._getCleanedTeachers(course.teachers),
                        year: course.year ? course.year : "",
                        code: course.id ? course.id : "",
                        name: course.name ? course.name : "",
                        schoolId: schools[i].id,
                        url: course.url ? course.url : "",
                        languages: this._getLanguages(course.languages && course.languages.length > 0 ? course.languages : ["other"]),
                        themes: this._getThemes(course.themes && course.themes.length > 0 ? course.themes : ["other"]),
                        dedicated: course.dedicated === 1
                    });

                    this._debugCoursesErrors(schools[i].shortName, course);
                });

                this.totalCoursesCounts[schools[i].id] = c.length;
            });

            sessionStorage.totalCoursesCounts = JSON.stringify(this.totalCoursesCounts);
            sessionStorage.coursesThemes = JSON.stringify(this.coursesThemes);
            sessionStorage.coursesLanguages = JSON.stringify(this.coursesLanguages);
            sessionStorage.courses = JSON.stringify(courses);
        }

        return JSON.parse(sessionStorage.courses);
    }

    _getCleanedTeachers(teachers) {

        let t = [];

        if (teachers && Array.isArray(teachers) && teachers.length > 0) {

            teachers.forEach(teacher => {

                teacher = teacher.trim();

                if (teacher.length > 0) {
                    t.push(teacher);
                }
            });
        }

        return t;
    }

    async getTotalCoursesCounts() {

        if (!sessionStorage.totalCoursesCounts) {

            await getCourses();
            sessionStorage.totalCoursesCounts = JSON.stringify(this.totalCoursesCounts);
        }

        return JSON.parse(sessionStorage.totalCoursesCounts);
    }

    async getCoursesThemes() {

        if (!sessionStorage.coursesThemes) {

            await getCourses();
            sessionStorage.coursesThemes = JSON.stringify(this.coursesThemes);
        }

        return JSON.parse(sessionStorage.coursesThemes);
    }

    async getCoursesLanguages() {

        if (!sessionStorage.coursesLanguages) {

            await getCourses();
            sessionStorage.coursesLanguages = JSON.stringify(this.coursesLanguages);
        }

        return JSON.parse(sessionStorage.coursesLanguages);
    }

    _getThemes(themes) {

        var t = [];

        if (themes) {

            for (var i = 0; i < themes.length; i++) {

                var id = -1;

                for (var j = 0; j < this.coursesThemes.length; j++) {

                    if (this.coursesThemes[j].name == themes[i]) {

                        id = j;
                        break;
                    }
                }

                if (id == -1) {

                    id = this.coursesThemes.length;

                    this.coursesThemes.push({

                        id: id,
                        name: themes[i],
                        totalCount: 0
                    });
                }

                this.coursesThemes[id].totalCount++;

                t.push(id);
            }
        }

        return t;
    }

    _getLanguages(languages) {

        var l = [];

        if (languages) {

            for (var i = 0; i < languages.length; i++) {

                // Take care of possible empty values

                if (languages[i].length === 0) continue;

                // Aggregate all languages other than fr/nl/en under "other"

                if (languages[i] != "en" && languages[i] != "fr" && languages[i] != "nl") languages[i] = "other";

                // Find the id of the language (if already in the programsLanguages dictionnary)

                var id = -1;

                for (var j = 0; j < this.coursesLanguages.length; j++) {

                    if (this.coursesLanguages[j].name == languages[i]) {

                        id = j;
                        break;
                    }
                }

                // If the language is not yet in the coursesLanguages dictionnary, add it

                if (id == -1) {

                    id = this.coursesLanguages.length;

                    this.coursesLanguages.push({

                        id: id,
                        name: languages[i],
                        totalCount: 0
                    });
                }

                // If not yet present in the array that will be returned, add it and increment the language count

                if (!l.includes(id)) {
                    
                    this.coursesLanguages[id].totalCount++;
                    l.push(id);
                }
            }
        }

        return l;
    }

    _debugCoursesErrors(school, course) {

        if (!course.year) console.log(school + " : " + course.id + " has no year");
        if (!course.id) console.log(school + " : " + course.id + " has no id");
        if (!course.name) console.log(school + " : " + course.id + " has no name");
        if (!course.url) console.log(school + " : " + course.id + " has no url");
        if (!course.languages || course.languages.length === 0) console.log(school + " : " + course.id + " has no languages");
        if (!course.themes || course.themes.length === 0) console.log(school + " : " + course.id + " has no themes");
        if (!course.teachers || !Array.isArray(course.teachers) || course.teachers.length === 0) console.log(school + " : " + course.id + " has no teachers");
        if (course.teachers && course.teachers.length > 0 && !course.teachers[0]) console.log(school + " : " + course.id + " has an empty teacher");
    }
}

export default CoursesManager;