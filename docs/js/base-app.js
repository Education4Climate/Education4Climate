/*jshint esversion: 8 */

/**
 * @file Base Vue.js app.
 * @author Quentin V.
 */

import * as constants from './constants.js';
import TranslationManager from "./managers/translation-manager.js";

export default {
    data() {
        return {
            availableLanguages: constants.AVAILABLE_LANGUAGES,
            menuItems: constants.MENU_ITEMS,
            currentLanguage: "fr",
            translations: [],
            translationManager: new TranslationManager(),
            dataLoaded: false,
            errors: "",
        };
    },
    async created() {

        try {

            this.currentLanguage = this.translationManager.getLanguage();
            this.translations = await this.translationManager.loadTranslations();
        }
        catch (error) {
            console.log(error);
            this.errors += error;
        }
    },
    methods: {
        translate(key, returnKeyIfNotFound) {

            return this.translations.length > 0 ? this.translationManager.translate(this.translations, key, this.currentLanguage, returnKeyIfNotFound) : "";
        },
        setLanguage(language) {

            this.currentLanguage = language;
            this.translationManager.setLanguage(language);
        }
    }
};