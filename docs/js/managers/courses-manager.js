/*jshint esversion: 8 */

/**
 * @file Manages the courses data.
 * @author Quentin V.
 */

import * as constants from '../constants.js';
import * as schoolsManager from './schools-manager.js';

var totalCoursesCounts = [];
var coursesThemes = [];
var coursesLanguages = [];

export async function getCourses() {

    if (!sessionStorage.courses) {

        var courses = [];

        const schools = await schoolsManager.getSchools();

        var urls = schools.map(school => constants.DATA_FOLDER + "/" + school.coursesFile);

        // Getting all the .json in parralel
        var data = await Promise.all(urls.map(url => fetch(url).then((response) => response.json())));

        data.forEach((c, i) => {

            c.forEach((course, j) => {

                courses.push({

                    id: courses.length,
                    teachers: getCleanedTeachers(course.teachers),
                    year: course.year ? course.year : "",
                    code: course.id ? course.id : "",
                    name: course.name ? course.name : "",
                    schoolId: schools[i].id,
                    url: course.url ? course.url : "",
                    languages: getLanguages(course.languages && course.languages.length > 0 ? course.languages : ["other"]),
                    themes: getThemes(course.themes && course.themes.length > 0 ? course.themes : ["other"])
                });

                debugCoursesErrors(schools[i].shortName, course);
            });

            totalCoursesCounts[schools[i].id] = c.length;
        });

        sessionStorage.totalCoursesCounts = JSON.stringify(totalCoursesCounts);
        sessionStorage.coursesThemes = JSON.stringify(coursesThemes);
        sessionStorage.coursesLanguages = JSON.stringify(coursesLanguages);
        sessionStorage.courses = JSON.stringify(courses);
    }

    return JSON.parse(sessionStorage.courses);
}

function getCleanedTeachers(teachers) {

    let t = [];

    if (teachers && Array.isArray(teachers) && teachers.length > 0) {

        teachers.forEach(teacher => {

            // teacher = teacher.replace("\u00a0", " ").trim();
            // const toDelete = ["Prof. dr. ir. arch.", "dr. ir. ing.", "Prof. dr. ir.", "Prof. dr. dr.", "Prof. dr.", "Prof. Dr.", "Prof. ir.", "- NNB", "arch.", "Dr.", "dr.", "Mevrouw ", "De heer "];
            // toDelete.forEach(str => { teacher = teacher.replace(str, ""); });

            teacher = teacher.trim();

            if (teacher.length > 0) {
                t.push(teacher);
            }
        });
    }

    return t;
}

export async function getTotalCoursesCounts() {

    if (!sessionStorage.totalCoursesCounts) {

        await getCourses();
        sessionStorage.totalCoursesCounts = JSON.stringify(totalCoursesCounts);
    }

    return JSON.parse(sessionStorage.totalCoursesCounts);
}

export async function getCoursesThemes() {

    if (!sessionStorage.coursesThemes) {

        await getCourses();
        sessionStorage.coursesThemes = JSON.stringify(coursesThemes);
    }

    return JSON.parse(sessionStorage.coursesThemes);
}

export async function getCoursesLanguages() {

    if (!sessionStorage.coursesLanguages) {

        await getCourses();
        sessionStorage.coursesLanguages = JSON.stringify(coursesLanguages);
    }

    return JSON.parse(sessionStorage.coursesLanguages);
}

function getThemes(themes) {

    var t = [];

    if (themes) {

        for (var i = 0; i < themes.length; i++) {

            var id = -1;

            for (var j = 0; j < coursesThemes.length; j++) {

                if (coursesThemes[j].name == themes[i]) {

                    id = j;
                    break;
                }
            }

            if (id == -1) {

                id = coursesThemes.length;

                coursesThemes.push({

                    id: id,
                    name: themes[i],
                    totalCount: 0
                });
            }

            coursesThemes[id].totalCount++;

            t.push(id);
        }
    }

    return t;
}

function getLanguages(languages) {

    var l = [];

    if (languages) {

        for (var i = 0; i < languages.length; i++) {

            var id = -1;

            for (var j = 0; j < coursesLanguages.length; j++) {

                if (coursesLanguages[j].name == languages[i]) {

                    id = j;
                    break;
                }
            }

            if (id == -1) {

                id = coursesLanguages.length;

                coursesLanguages.push({

                    id: id,
                    name: languages[i],
                    totalCount: 0
                });
            }

            coursesLanguages[id].totalCount++;

            l.push(id);
        }
    }

    return l;
}

function debugCoursesErrors(school, course) {

    if (!course.year) console.log(school + " : " + course.id + " has no year");
    if (!course.id) console.log(school + " : " + course.id + " has no id");
    if (!course.name) console.log(school + " : " + course.id + " has no name");
    if (!course.url) console.log(school + " : " + course.id + " has no url");
    if (!course.languages || course.languages.length === 0) console.log(school + " : " + course.id + " has no languages");
    if (!course.themes || course.themes.length === 0) console.log(school + " : " + course.id + " has no themes");
    if (!course.teachers || !Array.isArray(course.teachers) || course.teachers.length === 0) console.log(school + " : " + course.id + " has no teachers");
    if (course.teachers && course.teachers.length > 0 && !course.teachers[0]) console.log(school + " : " + course.id + " has an empty teacher");
}