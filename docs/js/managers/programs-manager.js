/*jshint esversion: 8 */

/**
 * @file Manages the programs data.
 * @author Quentin V.
 */

import * as constants from '../constants.js';
import SchoolsManager from './schools-manager.js';

class ProgramsManager {

    constructor() {

        this.programsThemes = [];
        this.programsFields = [];
        this.programsCycles = [];
        this.schoolsManager = new SchoolsManager();
    }

    /**
     * Gets the programs from the 'programFile' properties in the school.json.
     * In the meantime, build 2 dictionnaries of all the themes and fields with
     * their respective total occurences. All the data are cached in the
     * sessionStorage so original data are only accessed once per browser tab.
     * 
     * @export
     * @returns a cached array of all the programs.
     */
    async getPrograms() {

        if (!sessionStorage.programs) {

            var programs = [];

            const schools = await this.schoolsManager.getSchools();

            var urls = schools.map(school => constants.DATA_FOLDER + "/" + school.programsFile);

            // Getting all the .json in parralel
            var data = await Promise.all(urls.map(url => fetch(url).then((response) => response.json())));

            data.forEach((p, i) => {

                p.forEach((program, j) => {

                    programs.push({

                        id: j,
                        code: program.id ? program.id : "",
                        name: program.name ? program.name : "",
                        url: program.url ? program.url : "",
                        faculty: program.faculty ? program.faculty : "",
                        campus: program.campus ? program.campus : "",
                        schoolId: schools[i].id,
                        courses: program.courses && program.courses.length > 0 ? program.courses : [],
                        themes: this._getThemes(program.themes && program.themes.length > 0 ? program.themes : ["other"], program.themes_scores),
                        fieldId: this._getFieldId(program.field ? program.field : "other"),
                        score: program.courses ? program.courses.length : 0,
                        cycleId: this._getCycleId(program.cycle ? program.cycle : "other")
                    });

                    this._debugProgramsErrors(schools[i].shortName, program);
                });
            });

            sessionStorage.programsThemes = JSON.stringify(this.programsThemes);
            sessionStorage.programsFields = JSON.stringify(this.programsFields);
            sessionStorage.programsCycles = JSON.stringify(this.programsCycles);
            sessionStorage.programs = JSON.stringify(programs);
        }

        return JSON.parse(sessionStorage.programs);
    }

    async getProgramsThemes() {

        if (!sessionStorage.programsThemes) {

            await this.getPrograms();
            sessionStorage.programsThemes = JSON.stringify(this.programsThemes);
        }

        return JSON.parse(sessionStorage.programsThemes);
    }

    async getProgramsFields() {

        if (!sessionStorage.programsFields) {

            await this.getPrograms();
            sessionStorage.programsFields = JSON.stringify(this.programsFields);
        }

        return JSON.parse(sessionStorage.programsFields);
    }

    async getProgramsCycles() {

        if (!sessionStorage.programsCycles) {

            await this.getPrograms();
            sessionStorage.programsCycles = JSON.stringify(this.programsCycles);
        }

        return JSON.parse(sessionStorage.programsCycles);
    }

    _getFieldId(field) {

        var id = -1;

        for (var i = 0; i < this.programsFields.length; i++) {

            if (this.programsFields[i].name == field) {

                id = i;
                break;
            }
        }

        if (id == -1) {

            id = this.programsFields.length;

            this.programsFields.push({
                id: id,
                name: field,
                totalCount: 0
            });
        }

        this.programsFields[i].totalCount++;

        return id;
    }

    _getThemes(themes, scores) {

        var t = [];

        if (themes && scores && themes.length == scores.length) {

            for (var i = 0; i < themes.length; i++) {

                var id = -1;

                for (var j = 0; j < this.programsThemes.length; j++) {

                    if (this.programsThemes[j].name == themes[i]) {

                        id = j;
                        break;
                    }
                }

                if (id == -1) {

                    id = this.programsThemes.length;

                    this.programsThemes.push({

                        id: id,
                        name: themes[i],
                        totalCount: 0
                    });
                }

                this.programsThemes[id].totalCount++;

                t.push({
                    id: id,
                    score: scores[i]
                });
            }

            t.sort((a, b) => { return b.score - a.score; });
        }

        return t;
    }

    _getCycleId(cycle) {

        var id = -1;

        var master = ["master", "master"];
        var bac = ["bac", "bachelier", "bachelor"];

        cycle = master.includes(cycle.toLowerCase()) ? "master" : bac.includes(cycle.toLowerCase()) ? "bac" : "other";

        for (var i = 0; i < this.programsCycles.length; i++) {

            if (this.programsCycles[i].name == cycle) {

                id = i;
                break;
            }
        }

        if (id == -1) {

            id = this.programsCycles.length;

            this.programsCycles.push({
                id: id,
                name: cycle,
                totalCount: 0
            });
        }

        this.programsCycles[i].totalCount++;

        return id;
    }

    _debugProgramsErrors(school, program) {

        if (!program.id) console.log(school + " : " + program.id + " has no id");
        if (!program.name) console.log(school + " : " + program.id + " has no name");
        if (!program.url) console.log(school + " : " + program.id + " has no url");
        if (!program.faculty) console.log(school + " : " + program.id + " has no faculty");
        if (!program.campus) console.log(school + " : " + program.id + " has no campus");
        if (!program.field) console.log(school + " : " + program.id + " has no field");
        if (!program.cycle) console.log(school + " : " + program.id + " has no cycle");
        if (!program.courses || program.courses.length === 0) console.log(school + " : " + program.id + " has no courses");
        if (!program.themes || program.themes.length === 0) console.log(school + " : " + program.id + " has no themes");
        if (!program.themes_scores || program.themes_scores.length === 0) console.log(school + " : " + program.id + " has no themes_scores");
        if (program.themes && program.themes_scores && program.themes.length !== program.themes_scores.length) console.log(school + " : " + program.id + " has no score for all themes");
    }
}

export default ProgramsManager;