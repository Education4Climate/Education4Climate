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
            availableLanguages: constants.AVAILABLE_LANGUAGES,
            menuItems: constants.MENU_ITEMS,
            currentMenuItem: "",
            dataLoaded: false,
            errors: ""
        };
    },
    async created() {

        try {

            // detect current language and loads translations

            this.currentLanguage = translationManager.getLanguage();
            this.translations = await translationManager.loadTranslations();

            // hides the loader

            this.dataLoaded = true;
        }
        catch (error) {
            console.log(error);
            this.errors += error;
        }
    },
    methods: {
        translate(key) {

            return this.translations.length > 0 ? translationManager.translate(this.translations, key, this.currentLanguage) : "";
        },
        setLanguage(language) {
            this.currentLanguage = language;
            translationManager.setLanguage(language);
        }
    }
});

app.mount("#app");