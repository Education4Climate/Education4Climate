/*jshint esversion: 8 */

/**
 * @file Manages the home page.
 * @author Quentin V.
 */

import * as constants from './constants.js';
import * as translationManager from "./managers/translation-manager.js";

var app = Vue.createApp({
    el: '#app',
    data() {
        return {
            currentLanguage: "fr",
            translations: [],
            availableLanguages: constants.AVAILABLE_LANGUAGES
        };
    },
    async created() {

        this.currentLanguage = translationManager.getLanguage();

        await translationManager.loadTranslations().then(translations => {
            this.translations = translations;
        });

        this.dataLoaded = true;
    },
    methods: {
        translate(key) {

            let corpus = this.translations.find(translation => translation.language === this.currentLanguage);
            return key.split('.').reduce((obj, i) => obj[i], corpus.translations);
        },
        setLanguage(language) {
            this.currentLanguage = language;
            translationManager.setLanguage(language);
        }
    }
});

app.mount("#app");