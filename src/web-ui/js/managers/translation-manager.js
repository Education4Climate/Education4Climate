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

export function translate(key, language) {

    let translations = JSON.parse(sessionStorage.translations);
    let corpus = translations.find(translation => translation.language === language);

    return key.split('.').reduce((obj, i) => obj[i], corpus.translations);
}

export async function loadTranslations() {

    if (!sessionStorage.translations) {

        var translations = [];

        for (let language of constants.AVAILABLE_LANGUAGES) {

            await fetch(constants.DATA_FOLDER + "/translations/" + language + ".json")
                .then(response => { return response.json(); })
                .then(data => {
                    translations.push({
                        language: language,
                        translations: data
                    });
                });
        }

        sessionStorage.translations = JSON.stringify(translations);
    }

    return JSON.parse(sessionStorage.translations);
}