/*jshint esversion: 8 */

import { DATA_FOLDER } from '../constants.js';

export async function getCourses() {

    if (!sessionStorage.courses) {

        var courses = [];

        const schools = await getSchools();

        await Promise.all(schools.map(school => fetch(DATA_FOLDER + "/" + school.file)))
            .then(responses => Promise.all(responses.map(res => res.json())))
            .then(results => {

                for (var i = 0; i < results.length; i++) {

                    // On agrège les données de toutes les écoles dans un même tableau

                    results[i].forEach(course => {

                        courses.push({

                            schoolShortName: schools[i].shortName,
                            schoolId: "school-" + schools[i].shortName.toId(),
                            name: course.name,
                            shortName: course.id,
                            years: course.year,
                            teachers: course.teacher,
                            url: course.url,
                            languages: course.language,
                            themes: course.themes,
                            themesIds: course.themes.map(a => "theme-" + a.toId()),
                        });
                    });
                }
            });

        sessionStorage.courses = JSON.stringify(courses);
    }

    return JSON.parse(sessionStorage.courses);
}

/* HELPERS */

String.prototype.toId = function () {
    return this.toLowerCase().replace(/[^a-zA-Z0-9]+/g, "-");
};