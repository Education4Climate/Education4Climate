/*jshint esversion: 8 */

/**
 * @file Manages the programs finder tool.
 * @author Quentin V.
 */

import baseApp from "./base-app.js";
import * as constants from './constants.js';
import SchoolsManager from './managers/schools-manager.js';
import ProgramsManager from './managers/programs-manager.js';

var app = Vue.createApp({
    mixins: [baseApp],
    el: '#app',
    data() {
        return {

            currentStep: 0,
            totalSteps: 5,
            selectedFields: [],
            highschoolIsSelected: true,
            universitieIsSelected: true,
            bacIsSelected: true,
            masterIsSelected: true,
            selectedProgram: { // Mock Data, to replace by {}
                name: "Master en biologie des organismes et écologie à finalité",
                totalCoursesCount: 40,
                matchedCoursesCount: 20,
                approachingCoursesCount: 10,
                dedicatedCoursesCount: 10,
                url: "https://www.google.com",
                schoolId: 10
            },
            chart: null,
            selectedRegions: ['antwerpen', 'brabant-wallon', 'brussels', 'hainaut', 'liege', 'limburg', 'luxembourg', 'namur', 'oost-vlaanderen', 'vlaams-brabant', 'west-vlaanderen'],
            availableRegions: [],
            programsCountByRegion: {},
            sendingEmail: false,
            errorSendingEmail: false,
            mailSuccessfullySent: false,

            schools: [],
            programs: [],
            displayedPrograms: [],
            themes: [],
            fields: [],
            languages: [],
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
        selectedAllUniversities() {
            return this.selectedUniversities && this.selectedUniversities.length >= this.schools.filter(school => school.type == "university").length;
        },
        selectedAllHighSchools() {
            return this.selectedHighSchools && this.selectedHighSchools.length >= this.schools.filter(school => school.type == "highschool").length;
        },
        selectedAllThemes() {
            return this.selectedThemes && this.selectedThemes.length == this.themes.length;
        },
        selectedAllFields() {
            return this.selectedFields && this.selectedFields.length == this.fields.length;
        },
        selectedAllLanguages() {
            return this.selectedLanguages && this.selectedLanguages.length == this.languages.length;
        },
        selectedAllCycles() {
            return this.selectedCycles && this.selectedCycles.length == this.cycles.length;
        },
        sortedSchools() { /* Sort the schools alphabetically for display */

            return this.schools.slice().sort((a, b) => { return a.shortName.localeCompare(b.shortName); });
        },
        sortedThemes() { /* Sort the themes DESC on the total count for display */

            return this.themes.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedFields() { /* Sort the fields DESC on the total count for display */

            return this.fields.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedLanguages() { /* Sort the languages DESC on the total count for display */

            return this.languages.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        sortedCycles() { /* Sort the cycles DESC on the total count for display */

            return this.cycles.slice().sort((a, b) => { return b.totalCount - a.totalCount; });
        },
        filteredPrograms() { /* Filter the sorted programs according to the schools/themes/fields selected and program name searched */

            if (this.dataLoaded) {

                var results = this.programs.slice()
                    .filter(program => (this.highschoolIsSelected && this.schools[program.schoolId].type == "highschool") || (this.universitieIsSelected && this.schools[program.schoolId].type == "university"))
                    .filter(program => (this.masterIsSelected && this.cycles[program.cycleId].name == "master") || (this.bacIsSelected && this.cycles[program.cycleId].name == "bac"))
                    .filter(program => this.selectedFields.some(field => program.fields.includes(field)))
                    .filter(program => this.selectedCycles.includes(program.cycleId));

                this.availableRegions = [];
                this.programsCountByRegion = {};

                results.forEach(program => {

                    this.schools[program.schoolId].regions.forEach(region => {

                        if (!this.availableRegions.includes(region)) {
                            this.availableRegions.push(region);
                            this.programsCountByRegion[region] = 0;
                        }

                        this.programsCountByRegion[region]++;
                    });
                });

                this.availableRegions = this.availableRegions.sort();

                return results.filter(program => this.selectedRegions.filter(item => this.schools[program.schoolId].regions.includes(item)).length > 0);
            }

            return true;
        },
        sortedPrograms() { /* Step 2 : sort the filtered programs DESC on their score for display */

            return this.dataLoaded ? this.filteredPrograms.slice().sort((a, b) => { return b.score - a.score; }) : true;
        },
        programsCountsBySchool() { // Computes the total counts of programs by school

            const programsCountsBySchool = [];

            this.schools.forEach(school => {
                programsCountsBySchool[school.id] = this.programs.filter(program => school.id == program.schoolId).length;
            });

            return programsCountsBySchool;
        },
        programsCountLabel() {

            if (!this.sortedPrograms) {

                return "";
            }

            var tag = "<strong class='super-accent-color'>";

            if (this.sortedPrograms.length == 0) {

                return tag + "Aucune formation</strong> ne correspond à ta sélection";
            }

            tag = "<strong class='accent-color'>";

            if (this.sortedPrograms.length == 1) {

                return tag + this.sortedPrograms.length + " formation</strong> correspond à ta sélection";
            }

            return tag + this.sortedPrograms.length + " formations</strong> correspondent à ta sélection";
        }
    },

    async created() {

        try {

            if (!document.getElementById('googleAnalytics')) this.addGoogleAnalyticsScript();

            this.setTheme("dark");

            // loads schools data

            this.schools = await this.schoolsManager.getSchools();

            // loads programs data

            this.programs = await this.programsManager.getPrograms(this.schools);
            // Pour le SIEP on ne garde que les programmes des cours des écoles francophones, on filtre maintenant pour alléger les filtres
            this.programs = this.programs.filter(program => this.schools.filter(school => school.languages.includes("fr") && school.id == program.schoolId).length == 1);

            this.fields = (await this.programsManager.getProgramsFields()).filter(field => field.name != "Other");
            this.cycles = await this.programsManager.getProgramsCycles();
            this.languages = await this.programsManager.getProgramsLanguages();

            // sets the filters default selected schools / themes / fields

            this.selectedUniversities = this.selectedUniversities ? this.selectedUniversities : this.schools.filter(school => school.type == "university").map(school => { return school.id; });
            this.selectedHighSchools = this.selectedHighSchools ? this.selectedHighSchools : this.schools.filter(school => school.type == "highschool").map(school => { return school.id; });
            this.selectedLanguages = this.selectedLanguages ? this.selectedLanguages : this.languages.map(language => { return language.name; });
            this.selectedCycles = this.cycles.map(cycle => { return cycle.id; });

            // hides the loader

            this.dataLoaded = true;
        }
        catch (error) {
            console.log(error);
            this.errors += error;
        }
    },
    mounted() {

        document.addEventListener('swiped-right', this.previousStep);
        document.addEventListener('swiped-left', this.nextStep);
    },
    watch: {
        currentStep(value) {

            window.scrollTo(0, 0);

            if (value == 5) {

                this.showChart();
            }
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

            if (this.selectedProgram) {

                var chartData = [this.selectedProgram.totalCoursesCount - this.selectedProgram.matchedCoursesCount, // Le nombre total de cours - le nombre de cours matchés
                this.selectedProgram.approachingCoursesCount, // Le nombre de cours abordants (sans les cours dédicacés)
                this.selectedProgram.dedicatedCoursesCount]; // Uniquement les cours dédicacés

                if (this.chart) {

                    this.chart.destroy();
                    this.chart = null;
                }

                var canvas = this.$refs.chart;

                setTimeout(() => { // Va savoir pourquoi, en direct le graphe ne s'affiche pas

                    this.chart = new Chart(canvas, {
                        type: 'doughnut',
                        data: {
                            datasets: [{
                                data: chartData,
                                backgroundColor: ["#00004b", "#4bd2af", "#dc4b78"],
                                borderWidth: 4
                            }]
                        },
                        options: {
                            responsive: true,
                            events: null
                        }
                    });
                });
            }
        },
        toggleSelectedRegion(region) {

            if (this.selectedRegions.includes(region)) {

                // Si la région est déjà sélectionnée, on la retire du tableau
                this.selectedRegions.splice(this.selectedRegions.indexOf(region), 1);
            }
            else {
                // Sinon on l'y ajoute
                this.selectedRegions.push(region);
            }
        },
        nextStep(event) {

            switch (this.currentStep) {

                // Sur la page d'accueil par de contrôle
                case 0: this.currentStep++; break;
                // Sur les autres pages on vérifie qu'il y aura au moins un résultat
                case 1: this.currentStep = this.selectedFields.length > 0 ? this.currentStep + 1 : this.currentStep; break;
                case 2: this.currentStep = (this.highschoolIsSelected || this.universitieIsSelected) && (this.bacIsSelected || this.masterIsSelected) ? this.currentStep + 1 : this.currentStep; break;
                case 3: this.currentStep = this.selectedRegions.filter(item => this.availableRegions.includes(item)).length > 0 ? this.currentStep + 1 : this.currentStep; break;
            }
        },
        previousStep(event) {

            switch (this.currentStep) {

                // Sur la page d'accueil
                case 0: this.currentStep = 0; break;
                // Sur la page email on redirige vers la liste
                case 6: this.currentStep = 4; break;
                // Ailleurs on redirige vers la page précédente
                default: this.currentStep = this.currentStep - 1; break;
            }
        },
        programsCountShortLabel(count) { // Sous-titres pour la page "Dans quelle région?"

            return !count ? "Aucune information" : count == 1 ? "1 formation" : count + " formations";
        },
        coursesCountShortLabel(count) { // Compteur de cours sur la page de détails d'une formation

            return !count ? "aucun cours" : count + " cours";
        },
        async submitEmail(e) {

            // On remet à zéro l'écran
            this.sendingEmail = false;
            this.mailSuccessfullySent = false;

            if (!this.$refs.emailForm.email.value) {

                return;
            }

            this.sendingEmail = true; // On dit à l'écran qu'on est en train d'envoyer les données

            var requestOptions = {
                method: 'POST',
                body: new FormData(this.$refs.emailForm),
                redirect: 'follow'
            };

            fetch("https://script.google.com/macros/s/AKfycbxWF4IAssBIE5p_wayVj9Zr110YJao4mAENWy-sHuzYRiZJWM2tWjrdvrm7BHV7VK1GNQ/exec", requestOptions)
                .then(response => response.text())
                .then(result => {

                    this.$refs.emailForm.email.value = ""; // Si c'est OK on vide la textbox
                    this.mailSuccessfullySent = true; // On dit à l'écran que c'est OK
                })
                .catch(error => {

                    this.errorSendingEmail = true; // On dit à l'écran qu'il y a eu un soucis
                    console.log('error', error);
                })
                .finally(() => {

                    this.sendingEmail = false; // On dit à l'écran qu'on est plus occupé
                });
        },
        share() {

            const options = {
                title: "Education 4 Climate",
                text: "Tu es un des futurs acteurs de demain, les études que tu choisiras peuvent avoir un impact significatif sur le changement climatique et la transition vers une société neutre en CO2",
                url: document.location.href
            };

            if (dataLayer) {
                dataLayer.push("event", "share", {});
            }

            navigator.share(options);
        },
        async sendAnalytics() {

            if (dataLayer) {

                var wizardCycles = [];
                var wizardSchoolTypes = [];

                if (this.bacIsSelected) wizardCycles.push("bac");
                if (this.masterIsSelected) wizardCycles.push("master");
                if (this.highschoolIsSelected) wizardSchoolTypes.push("highschool");
                if (this.universitieIsSelected) wizardSchoolTypes.push("university");

                dataLayer.push({
                    'event': 'wizardSearch',
                    'wizardFields': this.selectedFields.map(field => this.fields[field].name),
                    'wizardRegions':this.selectedRegions.filter(region => this.availableRegions.includes(region)),
                    'wizardCycles': wizardCycles,
                    'wizardSchoolTypes':wizardSchoolTypes
                });
            }
        }
    }
});

app.mount("#app");