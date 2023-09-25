/*jshint esversion: 8 */

/**
 * @file Manages the programs finder tool.
 * @author Quentin V.
 */

import baseApp from "./base-app.js";
import SchoolsManager from './managers/schools-manager.js';
import ProgramsManager from './managers/programs-manager.js';
//import { Chart } from './chart.js';
//import ChartDataLabels from './chartjs-plugin-datalabels.min.js';

var app = Vue.createApp({
    mixins: [baseApp],
    el: '#app',
    data() {
        return {
            schools: [],
            programs: [],
            displayedPrograms: [],
            themes: [],
            fields: [],
            languages: [],
            selectedFields: [],
            selectedCycles: [],
            searchedName: "",
            currentPage: 0,
            showResponsiveFilters: false,
            currentMenuItem: "programs",
            cycles: [],
            schoolsManager: new SchoolsManager(),
            programsManager: new ProgramsManager()
        };
    },
    computed: {

        programsCountsBySchool() { // Computes the total counts of programs by school

            const programsCountsBySchool = [];

            this.schools.forEach(school => {
                programsCountsBySchool[school.id] = this.programs.filter(program => school.id == program.schoolId).length;
            });

            return programsCountsBySchool;
        }
    },
    async created() {

        try {

            // loads schools data

            this.schools = await this.schoolsManager.getSchools();

            // loads programs data

            this.programs = await this.programsManager.getPrograms();
            this.themes = await this.programsManager.getProgramsThemes();
            this.fields = await this.programsManager.getProgramsFields();
            this.cycles = await this.programsManager.getProgramsCycles();
            this.languages = await this.programsManager.getProgramsLanguages();

            // sets the filters default selected schools / themes / fields

            this.selectedUniversities = this.selectedUniversities ? this.selectedUniversities : this.schools.filter(school => school.type == "university").map(school => { return school.id; });
            this.selectedHighSchools = this.selectedHighSchools ? this.selectedHighSchools : this.schools.filter(school => school.type == "highschool").map(school => { return school.id; });
            this.selectedThemes = this.selectedThemes ? this.selectedThemes : this.themes.map(theme => { return theme.name; });
            this.selectedFields = this.fields.map(field => { return field.id; });
            this.selectedLanguages = this.selectedLanguages ? this.selectedLanguages : this.languages.map(language => { return language.name; });
            this.selectedCycles = this.cycles.map(cycle => { return cycle.id; });

            // hides the loader

            this.dataLoaded = true;



            this.showChart();
        }
        catch (error) {
            console.log(error);
            this.errors += error;
        }
    },
    methods: {

        toggleHighschoolSwitch() {
            this.highschoolIsSelected = !this.highschoolIsSelected;
        },
        toggleUniversitySwitch() {
            this.universitieIsSelected = !this.universitieIsSelected;
        },
        toggleBacSwitch() {
            this.bacIsSelected = !this.bacIsSelected;
        },
        toggleMasterSwitch() {
            this.masterIsSelected = !this.masterIsSelected;
        },
        showChart() {

            var programsbyUniversityData = [62.79, 24.67, 7.41, 5.13];
            var programsbyHighSchoolData = [71.32, 23.00, 4.19, 1.50];

            const doughnutConfig = {
                type: 'doughnut',
                data: {
                    datasets: [{
                        backgroundColor: ["#C0C0C0", "#4bd2af", "#00788c", "#00004b"],
                        borderWidth: 1,
                        borderColor: '#000000',
                        datalabels: {
                            align: 'start',
                            anchor: 'start'
                        }
                    }],
                    labels: ['aucun cours', 'moins de 10%', 'entre 10 et 20%', 'plus de 20%']
                },
                options: {
                    responsive: false,
                    events: null,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'right',
                            labels: {
                                generateLabels: (chart) => {
                                    const datasets = chart.data.datasets;
                                    return datasets[0].data.map((data, i) => ({
                                        text: `${chart.data.labels[i]} : ${data}%`,
                                        fillStyle: datasets[0].backgroundColor[i],
                                        index: i
                                    }));
                                }
                            }
                        },
                        title: {
                            display: true
                        },
                    }
                }
            };

            var programsbyUniversityConfig = doughnutConfig;
            programsbyUniversityConfig.data.datasets[0].data = programsbyUniversityData;
            new Chart(this.$refs.programsbyUniversityChart, programsbyUniversityConfig);

            var programsbyHighSchoolConfig = doughnutConfig;
            programsbyHighSchoolConfig.data.datasets[0].data = programsbyHighSchoolData;
            new Chart(this.$refs.programsbyHighSchoolChart, programsbyHighSchoolConfig);

            new Chart(this.$refs.chart3, {
                type: 'bar',
                data: {
                    labels: ['Théologie', 'Médecine et santé', 'Arts', 'Lettres', 'Philosophie', 'Pédagogie', 'Communication'],
                    datasets: [{
                        label: 'Pas de cours',
                        data: [-100, -100, -95, -50, -40, -30, -10],
                        backgroundColor: '#C0C0C0',
                    },
                    {
                        label: '> 1 cours sur 10',
                        data: [0, 0, 5, 50, 60, 70, 90],
                        backgroundColor: '#4bd2af'
                    }]
                },
                options: {
                    responsive: false,
                    events: null,
                    indexAxis: 'y',
                    scales: {
                        x: {
                            ticks: {
                                callback: (val) => {
                                    return val.toString().replace('-', '');
                                }
                            }
                        },
                        y: {
                            stacked: true
                        }
                    }
                }
            });

            var treeMapData = [
                {
                    what: 'Agronomie et biotechnologie',
                    value: 100
                },
                {
                    what: 'Sciences',
                    value: 80
                },
                {
                    what: 'Ingénierie',
                    value: 50
                },
                {
                    what: 'Architecture',
                    value: 30
                },
                {
                    what: 'Gestion',
                    value: 10
                },
                {
                    what: 'Communication',
                    value: 10
                },
                {
                    what: 'Théologie',
                    value: 5

                },
                {
                    what: 'Psychologie',
                    value: 1
                }
            ];

            const config = {
                type: 'treemap',
                data: {
                    datasets: [
                        {
                            label: 'My treemap dataset',
                            tree: treeMapData,
                            key: 'value',
                            borderColor: 'transparent',
                            borderWidth: 2,
                            spacing: 0,
                            labels: {
                                display: true,
                                formatter(ctx) {
                                    return ctx.raw._data.what;
                                },
                                color: 'white'
                            },
                            backgroundColor: (ctx) => {

                                if (ctx.type !== 'data') { return; }
                                return ctx.raw._data.value > 50 ? '#00004b': ctx.raw._data.value > 25 ? '#00788c' : '#4bd2af';
                            }
                        }
                    ],
                },
                options: {
                    events: null,
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            };

            new Chart(this.$refs.chart4, config);

        }
    }
});

app.mount("#app");