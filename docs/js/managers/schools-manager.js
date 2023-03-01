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
    async getSchools(languages) {

        if (!sessionStorage.schools) {

            var schools = [];

            await fetch(constants.SCHOOLS_FILE)
                .then(response => response.json())
                .then(data => {

                    data.schools.forEach((school) => {

                        if (!languages || school.languages.filter(item => languages.includes(item)).length > 0) {

                            schools.push({
                                id: schools.length,
                                name: school.name,
                                shortName: school.shortName,
                                coursesFile: school.coursesFile,
                                programsFile: school.programsFile,
                                teachersDirectoryUrl: school.teachersDirectoryUrl,
                                type: school.type,
                                regions: school.regions
                            });
                        }
                    });
                });

            sessionStorage.schools = JSON.stringify(schools);
        }

        return JSON.parse(sessionStorage.schools);
    }
}

export default SchoolsManager;