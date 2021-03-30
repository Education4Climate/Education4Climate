/*jshint esversion: 8 */

/**
 * @file Manages the translations.
 * @author Quentin V.
 */

import * as constants from '../constants.js';

export function getLanguage() {

    let storedLanguage = localStorage.getItem("language");

    if (storedLanguage) {

        if (!constants.AVAILABLE_LANGUAGES.includes(storedLanguage)) {

            localStorage.removeItem("language");
        }
        else {
            return storedLanguage;
        }
    }

    if (navigator && navigator.languages) {

        let navigatorLanguage = navigator.languages[0].substr(0, 2);

        return constants.AVAILABLE_LANGUAGES.includes(navigatorLanguage) ? navigatorLanguage : constants.DEFAULT_LANGUAGE;
    }

    return constants.DEFAULT_LANGUAGE;
}

export function setLanguage(language) {

    if (constants.AVAILABLE_LANGUAGES.includes(language)) {

        localStorage.setItem("language", language);
    }
}

export function translate(translations, key, language, returnKeyIfNotFound = false) {

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

export async function loadTranslations() {

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