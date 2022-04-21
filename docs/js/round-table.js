/*jshint esversion: 8 */

/**
 * @file Manages the round-table page.
 * @author Quentin V.
 */

import baseApp from "./base-app.js";

successMessage: "You registration has been received.";
errorMessage: "";

var app = Vue.createApp({
    mixins: [baseApp],
    el: '#app',
    data() {
        return {
            currentMenuItem: "",
            sendingRegistration: false,
            errorWhileRegistering: false,
            isSuccessfullyRegistered: false
        };
    },
    async created() {

        this.dataLoaded = true;
    },
    methods: {
        async registerToRoundTable(e) {

            this.sendingRegistration = true;
            this.successfullyRegistered = false;

            var requestOptions = {
                method: 'POST',
                body: new FormData(this.$refs.roundTableForm),
                redirect: 'follow'
            };
            
            fetch("https://script.google.com/macros/s/AKfycbxF5o-7sSVt7ficTEV6O3IVQu4g1tr1PyxQaFpoHO1szoeQEIeNw7i8oW2zoOWBsY8czQ/exec", requestOptions)
                .then(response => response.text())
                .then(result => {
                    console.log(result);
                    this.isSuccessfullyRegistered = true;
                })
                .catch(error => {
                    this.errorWhileRegistering = true;

                    console.log('error', error);
                })
                .finally(() => {
                    this.sendingRegistration = false;
                });
        }
    }
});

app.mount("#app");