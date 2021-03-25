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

        for (var i = 0; i < schools.length; i++) {

            await fetch(constants.DATA_FOLDER + "/" + schools[i].coursesFile)
                .then(response => { return response.json(); })
                .then(data => {

                    data.forEach((course, j) => {

                        courses.push({

                            id: j,
                            teachers: course.teacher,
                            years: course.year,
                            code: course.id,
                            name: course.name,
                            schoolId: schools[i].id,
                            url: course.url,
                            languages: getLanguages(course.language),
                            themes: getThemes(course.themes)
                        });

                        // DEBUG
                        if (!course.language) console.log(schools[i].name + " : " + course.id + " has no language");
                        if (!course.themes) console.log(schools[i].name + " : " + course.id + " has no theme");
                        if (!course.url || course.url === "") console.log(schools[i].name + " : " + course.id + " has no url");
                    });

                    totalCoursesCounts[schools[i].id] = data.length;
                });
        }

        sessionStorage.totalCoursesCounts = JSON.stringify(totalCoursesCounts);
        sessionStorage.coursesThemes = JSON.stringify(coursesThemes);
        sessionStorage.coursesLanguages = JSON.stringify(coursesLanguages);
        sessionStorage.courses = JSON.stringify(courses);
    }

    return JSON.parse(sessionStorage.courses);
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