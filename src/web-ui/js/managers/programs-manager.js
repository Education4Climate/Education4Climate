/*jshint esversion: 8 */

/**
 * @file Manages the programs data.
 * @author Quentin V.
 */

import * as constants from '../constants.js';
import * as schoolsManager from './schools-manager.js';

var totalProgramsCountBySchool = [];
var programsThemes = [];
var programsFields = [];

/**
 * Gets the programs from the 'programFile' properties in the school.json.
 * In the meantime, build 2 dictionnaries of all the themes and fields with
 * their respective total occurences. All the data are cached in the
 * sessionStorage so original data are only accessed once per browser tab.
 * 
 * @export
 * @returns a cached array of all the programs.
 */
export async function getPrograms() {

    if (!sessionStorage.programs) {

        var programs = [];

        const schools = await schoolsManager.getSchools();

        for (var i = 0; i < schools.length; i++) {

            await fetch(constants.DATA_FOLDER + "/" + schools[i].programsFile)
                .then(response => { return response.json(); })
                .then(data => {

                    data.forEach((program, j) => {

                        programs.push({

                            id: j,
                            code: program.id,
                            name: program.name,
                            url: program.url,
                            faculty: program.faculty,
                            campus: program.campus,
                            schoolId: schools[i].id,
                            courses: program.courses,
                            themes: getThemes(program.themes, program.themes_scores),
                            fieldId: getFieldId(program.field),
                            score: program.themes_scores.reduce((a, b) => a + b, 0),
                            cycle: program.cycle
                        });
                    });

                    totalProgramsCountBySchool[schools[i].id] = data.length;
                });
        }

        sessionStorage.totalProgramsCountBySchool = JSON.stringify(totalProgramsCountBySchool);
        sessionStorage.programsThemes = JSON.stringify(programsThemes);
        sessionStorage.programs = JSON.stringify(programs);
    }

    return JSON.parse(sessionStorage.programs);
}

/**
 * Get the total number of programs for each school.
 *
 * @export
 * @returns a cached array of the total programs count for each school, every index of the array
 * being the index of the schools array returned by schoolsManager.getSChools().
 */
export async function getTotalProgramsCountBySchool() {

    if (!sessionStorage.totalProgramsCountBySchool) {

        await getPrograms();
        sessionStorage.totalProgramsCountBySchool = JSON.stringify(totalProgramsCountBySchool);
    }

    return JSON.parse(sessionStorage.totalProgramsCountBySchool);
}

export async function getProgramsThemes() {

    if (!sessionStorage.programsThemes) {

        await getPrograms();
        sessionStorage.programsThemes = JSON.stringify(programsThemes);
    }

    return JSON.parse(sessionStorage.programsThemes);
}

export async function getProgramsFields() {

    if (!sessionStorage.programsFields) {

        await getPrograms();
        sessionStorage.programsFields = JSON.stringify(programsFields);
    }

    return JSON.parse(sessionStorage.programsFields);
}

function getFieldId(field) {

    var id = -1;

    for (var i = 0; i < programsFields.length; i++) {

        if (programsFields[i].name == field) {

            id = i;
            break;
        }
    }

    if (id == -1) {

        id = programsFields.length;

        programsFields.push({
            id: id,
            name: field,
            totalCount: 0
        });
    }

    programsFields[i].totalCount++;

    return id;
}

function getThemes(themes, scores) {

    var t = [];

    for (var i = 0; i < themes.length; i++) {

        var id = -1;

        for (var j = 0; j < programsThemes.length; j++) {

            if (programsThemes[j].name == themes[i]) {

                id = j;
                break;
            }
        }

        if (id == -1) {

            id = programsThemes.length;

            programsThemes.push({

                id: id,
                name: themes[i],
                totalCount: 0
            });
        }

        programsThemes[id].totalCount++;

        t.push({
            id: id,
            score: scores[i]
        });
    }

    t.sort((a, b) => { return b.score - a.score; });

    return t;
}