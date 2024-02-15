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
        this.programsLanguages = [];
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

            // Getting all the .json in parallel
            var data = await Promise.all(urls.map(url => fetch(url).then((response) => response.json())));

            data.forEach((p, i) => {

                p.forEach((program, j) => {

                    programs.push({

                        id: j,
                        code: String(program.id) ? String(program.id) : "",
                        name: program.name ? program.name : "",
                        url: program.url ? program.url : "",
                        faculties: program.faculties ? program.faculties : "",
                        campuses: program.campuses && program.campuses.length > 0 ? program.campuses : [],
                        schoolId: schools[i].id,
                        courses: program.matched_courses && program.matched_courses.length > 0 ? program.matched_courses : [],
                        totalCoursesCount: program.nb_total_courses ? program.nb_total_courses : 0,
                        matchedCoursesCount: program.nb_matched_courses ? program.nb_matched_courses : 0,
                        approachingCoursesCount: program.nb_matched_courses ? program.nb_matched_courses - program.nb_dedicated_courses : 0,
                        dedicatedCoursesCount: program.nb_dedicated_courses ? program.nb_dedicated_courses : 0,
                        themes: this._getThemes(program.themes && program.themes.length > 0 ? program.themes : ["other"], program.themes_scores),
                        fields: this._getFields(program.fields && program.fields.length > 0 ? program.fields : ["Other"]),
                        score: program.matched_courses ? program.matched_courses.length : 0,
                        cycleId: this._getCycleId(program.cycle ? program.cycle : "other"),
                        languages: this._getLanguages(program.languages && program.languages.length > 0 ? program.languages : ["other"]),
                    });

                    this._debugProgramsErrors(schools[i].shortName, program);
                });
            });

            sessionStorage.programsThemes = JSON.stringify(this.programsThemes);
            sessionStorage.programsFields = JSON.stringify(this.programsFields);
            sessionStorage.programsCycles = JSON.stringify(this.programsCycles);
            sessionStorage.programsLanguages = JSON.stringify(this.programsLanguages);
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

    async getProgramsLanguages() {

        if (!sessionStorage.programsLanguages) {

            await getProgram();
            sessionStorage.programsLanguages = JSON.stringify(this.programsLanguages);
        }

        return JSON.parse(sessionStorage.programsLanguages);
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
        if (!program.faculties || program.faculties.length === 0) console.log(school + " : " + program.id + " has no faculties");
        if (!program.campuses || program.campuses === 0) console.log(school + " : " + program.id + " has no campus");
        if (!program.fields || program.fields.length === 0) console.log(school + " : " + program.id + " has no fields");
        if (!program.cycle) console.log(school + " : " + program.id + " has no cycle");
        if (!program.matched_courses || program.matched_courses.length === 0) console.log(school + " : " + program.id + " has no matched courses");
        if (!program.themes || program.themes.length === 0) console.log(school + " : " + program.id + " has no themes");
        if (!program.themes_scores || program.themes_scores.length === 0) console.log(school + " : " + program.id + " has no themes_scores");
        if (program.themes && program.themes_scores && program.themes.length !== program.themes_scores.length) console.log(school + " : " + program.id + " has no score for all themes");
        if (!program.languages || program.languages.length === 0) console.log(school + " : " + program.id + " has no languages");
        if (program.languages && program.languages.length > 0 && !program.languages[0]) console.log(school + " : " + program.id + " has an empty language");
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

                for (var j = 0; j < this.programsLanguages.length; j++) {

                    if (this.programsLanguages[j].name == languages[i]) {

                        id = j;
                        break;
                    }
                }

                // If the language is not yet in the programsLanguages dictionnary, add it

                if (id == -1) {

                    id = this.programsLanguages.length;

                    this.programsLanguages.push({

                        id: id,
                        name: languages[i],
                        totalCount: 0
                    });
                }

                // If not yet present in the array that will be returned, add it and increment the language count

                if (!l.includes(id)) {
                    
                    this.programsLanguages[id].totalCount++;
                    l.push(id);
                }
            }
        }

        return l;
    }

    _getFields(fields) {

        var l = [];

        if (fields) {

            for (var i = 0; i < fields.length; i++) {

                // Take care of possible empty values

                if (fields[i].length === 0) continue;

                // Find the id of the field (if already in the programsFields dictionnary)

                var id = -1;

                for (var j = 0; j < this.programsFields.length; j++) {

                    if (this.programsFields[j].name == fields[i]) {

                        id = j;
                        break;
                    }
                }

                // If the field is not yet in the programsFields dictionnary, add it

                if (id == -1) {

                    id = this.programsFields.length;

                    this.programsFields.push({

                        id: id,
                        name: fields[i],
                        totalCount: 0
                    });
                }

                // If not yet present in the array that will be returned, add it and increment the field count

                if (!l.includes(id)) {
                    
                    this.programsFields[id].totalCount++;
                    l.push(id);
                }
            }
        }

        return l;
    }    
}

export default ProgramsManager;