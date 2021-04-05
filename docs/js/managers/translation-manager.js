/*jshint esversion: 8 */

/**
 * @file Manages the translations.
 * @author Quentin V.
 */

import * as constants from '../constants.js';

class TranslationManager {

    getLanguage() {

        // Step 1 : if the language is passed in the url

        const urlLanguage = new URL(document.location).searchParams.get("lang");

        if (urlLanguage && constants.AVAILABLE_LANGUAGES.includes(urlLanguage)) {

            this.setLanguage(urlLanguage);
            return urlLanguage;
        }

        // Step 2 : if the language is stored in the local storage

        let storedLanguage = localStorage.getItem("language");

        if (storedLanguage && constants.AVAILABLE_LANGUAGES.includes(storedLanguage)) {

            this.setLanguage(storedLanguage);
            return storedLanguage;
        }

        // Step 3 : the language of the browser

        let navigatorLanguage = navigator && navigator.languages && navigator.languages[0].substr(0, 2);

        if (navigatorLanguage && constants.AVAILABLE_LANGUAGES.includes(navigatorLanguage)) {

            this.setLanguage(navigatorLanguage);
            return navigatorLanguage;
        }

        // Step 4 : default language

        this.setLanguage(constants.DEFAULT_LANGUAGE);
        return constants.DEFAULT_LANGUAGE;
    }

    setLanguage(language, consentLocalStorage = false) {

        if (constants.AVAILABLE_LANGUAGES.includes(language)) {

            if (consentLocalStorage) {

                localStorage.setItem("language", language);
                console.log("Language set in the Local Storage");
            }

            // sets the 'lang' attribute inside the <html> tag

            document.documentElement.setAttribute('lang', language);

            // add the 'lang" parameter in the url

            if (document.location.search) {

                const urlLanguage = new URL(document.location).searchParams.get("lang");

                if (urlLanguage) {

                    window.history.replaceState({}, "", document.location.pathname + document.location.search.replace("lang=" + urlLanguage, "lang=" + language));
                }
                else {
                    window.history.replaceState({}, "", document.location.pathname + document.location.search + "&lang=" + language);
                }
            }
            else {
                window.history.replaceState({}, "", document.location.pathname + "?lang=" + language);
            }
        }
    }

    translate(translations, key, language, returnKeyIfNotFound = false) {

        if (!translations || translations.length == 0) {

            console.log("translate() : parameter 'translations' is empty");
            return "";
        }

        let corpus = translations.find(translation => translation.language === language);

        if (!corpus) {

            console.log("translate() : no corpus found for language '" + language + "'");
            return "";
        }

        let value = key.split('.').reduce((obj, i) => obj[i], corpus.translations);

        if (!value) {

            console.log("translate() : no translation found in language '" + language + "' for key '" + key + "'");
            return returnKeyIfNotFound ? key : "";
        }

        return value;
    }

    async loadTranslations() {

        if (!sessionStorage.translations) {

            var translations = [];

            var urls = constants.AVAILABLE_LANGUAGES.map(language => constants.DATA_FOLDER + "/translations/" + language + ".json");

            // Getting all the .json in parralel
            var data = await Promise.all(urls.map(url => fetch(url).then((response) => response.json())));

            data.forEach((language, i) => { translations.push({ language: constants.AVAILABLE_LANGUAGES[i], translations: language }); });

            sessionStorage.translations = JSON.stringify(translations);
        }

        return JSON.parse(sessionStorage.translations);
    }

}

export default TranslationManager;