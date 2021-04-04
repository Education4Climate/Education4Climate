/*jshint esversion: 8 */

/**
 * @file Manages the teachers logic.
 * @author Quentin V.
 */

import * as coursesManager from './courses-manager.js';

class TeachersManager {

    async getTeachers() {

        if (!sessionStorage.teachers) {

            let teachers = [];

            const courses = await coursesManager.getCourses();

            courses.forEach(course => {

                if (course.teachers && course.teachers.length > 0) {

                    course.teachers.forEach(teacher => {

                        let id = -1;

                        for (var i = 0; i < teachers.length; i++) {

                            if (teachers[i].schoolId == course.schoolId && teachers[i].name == teacher) {

                                id = i;
                                break;
                            }
                        }

                        if (id === -1) {

                            id = teachers.length;

                            teachers.push({

                                id: id,
                                schoolId: course.schoolId,
                                name: teacher,
                                coursesIds: [],
                                themesIds: []
                            });
                        }

                        teachers[id].coursesIds.push(course.id);

                        course.themes.forEach(theme => {

                            if (!teachers[id].themesIds.includes(theme)) {

                                teachers[id].themesIds.push(theme);
                            }
                        });
                    });
                }
            });

            sessionStorage.teachers = JSON.stringify(teachers);
        }

        return JSON.parse(sessionStorage.teachers);
    }
}

export default TeachersManager;