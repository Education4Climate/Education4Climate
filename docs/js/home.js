/*jshint esversion: 8 */

/**
 * @file Manages the home page.
 * @author Quentin V.
 */

import baseApp from "./base-app.js";

var app = Vue.createApp({
    mixins: [baseApp],
    el: '#app',
    data() {
        return {
            currentMenuItem: ""
        };
    },
    async created() {

        this.dataLoaded = true;
    }
});

app.mount("#app");