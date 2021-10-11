/*jshint esversion: 8 */

/**
 * @file Base Vue.js app.
 * @author Quentin V.
 */

import * as constants from './constants.js';
import TranslationManager from "./managers/translation-manager.js";
import CookieManager from "./components/cookie-manager.js";

export default {
    components: {
        CookieManager
    },
    data() {
        return {
            availableLanguages: constants.AVAILABLE_LANGUAGES,
            menuItems: constants.MENU_ITEMS,
            currentLanguage: "fr",
            translations: [],
            translationManager: new TranslationManager(),
            dataLoaded: false,
            errors: "",
            consentGoogleAnalytics: false,
            consentLocalStorage: false,
            selectedSchools: null,
            selectedThemes: null,
            selectedLanguages: null
        };
    },
    async created() {

        try {

            this.currentLanguage = this.translationManager.getLanguage();
            this.translations = await this.translationManager.loadTranslations();

            var currentTheme = document.documentElement.getAttribute("data-theme");
            currentTheme = currentTheme ? currentTheme : constants.DEFAULT_THEME;
            document.documentElement.setAttribute("data-theme", currentTheme);
            const themeToggler = document.querySelector("#theme-toggler");
            
            if (themeToggler) themeToggler.addEventListener("click", toggleTheme, false);
        }
        catch (error) {
            console.log(error);
            this.errors += error;
        }
    },
    mounted() {

        // Initialize the filters values from the sessionStorage so the
        // selected values stay the same across pages

        if (sessionStorage.selectedSchools) this.selectedSchools = JSON.parse(sessionStorage.selectedSchools);
        if (sessionStorage.selectedThemes) this.selectedThemes = JSON.parse(sessionStorage.selectedThemes);
        if (sessionStorage.selectedLanguages) this.selectedLanguages = JSON.parse(sessionStorage.selectedLanguages);
    },
    watch: {

        // Watch for the sessionStorage to update the filters values which
        // stay the same across pages (hence the use of sessionStorage)

        selectedSchools(value) {
            sessionStorage.selectedSchools = JSON.stringify(value);
        },
        selectedThemes(value) {
            sessionStorage.selectedThemes = JSON.stringify(value);
        },
        selectedLanguages(value) {
            sessionStorage.selectedLanguages = JSON.stringify(value);
        }
    },
    methods: {
        translate(key, returnKeyIfNotFound) {

            return this.translations.length > 0 ? this.translationManager.translate(this.translations, key, this.currentLanguage, returnKeyIfNotFound) : "";
        },
        setLanguage(language) {

            this.currentLanguage = language;
            this.translationManager.setLanguage(language, this.consentLocalStorage);
        },
        changeCookiesConsent(consentGoogleAnalytics, consentLocalStorage) {

            // Update the local values

            this.consentGoogleAnalytics = consentGoogleAnalytics;
            this.consentLocalStorage = consentLocalStorage;

            if (consentGoogleAnalytics) {

                // Add Google Analytics script if it's not already present

                if (!document.getElementById('googleAnalytics')) this.addGoogleAnalyticsScript();
            }
            else {

                // Otherwise remove the Google Analytics if it's present

                if (document.getElementById('googleAnalytics')) {

                    document.head.removeChild(document.getElementById('googleAnalytics'));
                    console.log("Google Analytics script removed");
                }

                // Remove all cokies (as Google Analytics cookies are the only ones)

                this.clearAllCookies();
            }

            if (consentLocalStorage) {

                // Set the language in the Local Storage

                this.translationManager.setLanguage(this.currentLanguage, true);
            }
            else {

                // Otherwise remove the language from the Local Storage if it's present

                if (localStorage.getItem("language")) {

                    localStorage.removeItem("language");
                    console.log("Language removed from Local Storage");
                }
            }
        },
        addGoogleAnalyticsScript() {

            const script = document.createElement("script");
            script.setAttribute("src", "https://www.googletagmanager.com/gtag/js?id=" + constants.GOOGLE_ANALYTICS_ID);
            script.setAttribute("id", "googleAnalytics");

            script.onload = function () {

                window.dataLayer = window.dataLayer || [];
                function gtag() { dataLayer.push(arguments); }
                gtag('js', new Date());
                gtag('config', constants.GOOGLE_ANALYTICS_ID);
            };

            document.head.appendChild(script);

            console.log("Google Analytics script added");
        },
        clearAllCookies() {

            var cookies = document.cookie.split(";");

            for (var i = 0; i < cookies.length; i++) {

                // Set every cookie as expired

                var cookie = cookies[i];
                var eqPos = cookie.indexOf("=");
                var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
                document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
            }

            if (cookies.length > 1) console.log("Google Analytics cookies removed");
        },
        toggleTheme(e) {

            console.log("toggleTheme()");

            var currentTheme = document.documentElement.getAttribute("data-theme");

            console.log(currentTheme);

            if (currentTheme == constants.DEFAULT_THEME) {
                document.documentElement.setAttribute("data-theme", constants.ALTERNATE_THEME);
            }
            else {
                document.documentElement.setAttribute("data-theme", constants.DEFAULT_THEME);
            }
        }
    }
};