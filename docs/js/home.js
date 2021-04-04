/*jshint esversion: 8 */

/**
 * @file Manages the home page.
 * @author Quentin V.
 */

import * as constants from './constants.js';
import TranslationManager from "./managers/translation-manager.js";

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
            errors: "",
            translationManager: new TranslationManager()
        };
    },
    async created() {

        try {

            // detect current language and loads translations

            this.currentLanguage = this.translationManager.getLanguage();
            this.translations = await this.translationManager.loadTranslations();

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

            return this.translations.length > 0 ? this.translationManager.translate(this.translations, key, this.currentLanguage) : "";
        },
        setLanguage(language) {
            this.currentLanguage = language;
            this.translationManager.setLanguage(language);
        }
    }
});

app.mount("#app");