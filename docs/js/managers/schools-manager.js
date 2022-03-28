/*jshint esversion: 8 */

/**
 * @file Manages the schools data.
 * @author Quentin V.
 */

import * as constants from '../constants.js';

class SchoolsManager {

    /**
     * Gets the schools from the schools JSON file.
     * 
     * @returns a cached array of all the schools where every index
     * is also the school ID.
     */
    async getSchools() {

        if (!sessionStorage.schools) {

            var schools = [];

            await fetch(constants.SCHOOLS_FILE)
                .then(response => response.json())
                .then(data => {

                    data.schools.forEach((school, i) => {

                        schools.push({
                            id: i,
                            name: school.name,
                            shortName: school.shortName,
                            coursesFile: school.coursesFile,
                            programsFile: school.programsFile,
                            teachersDirectoryUrl: school.teachersDirectoryUrl,
                            type: school.type
                        });
                    });
                });

            sessionStorage.schools = JSON.stringify(schools);
        }

        return JSON.parse(sessionStorage.schools);
    }
}

export default SchoolsManager;