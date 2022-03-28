/*jshint esversion: 8 */

/**
 * @file Manages the cookie bar/manager
 * - Displays the cookie bar if the user has never been shown to the user.
 * - Displays the cookie manager if asked to.
 * - Writes the consent to the 'cookieManager' Local Storage value.
 * - Sends the consent to the parent.
 * @author Quentin V.
 */

import TranslationManager from "../managers/translation-manager.js";

var CookieManager = {
    data() {
        return {
            translationManager: new TranslationManager(),
            displayCookieBar: !localStorage.getItem("cookieManager"),
            consentGoogleAnalytics: false,
            consentLocalStorage: false,
        };
    },
    props: ['translations', 'currentLanguage'],
    template: `<div class="container shadow p-3 mb-4 rounded fixed-bottom" id="cookieBar" v-if="displayCookieBar" v-cloak>
        <div class="row">
            <div class="col-md-6">{{translate("cookies.use-cookies")}}</div>
            <div class="col-md-6 mt-2 buttons">
                <button type="button" class="btn btn-light me-2 btn-sm" data-bs-toggle="modal"
                    data-bs-target="#modalCookies" :aria-label="translate('cookies.customize')">{{translate("cookies.customize")}}</button>
                <button type="button" class="btn btn-danger me-2 btn-sm"
                    @click="changeCookiesConsent(false, false)" :aria-label="translate('cookies.reject-all')">{{translate("cookies.reject-all")}}</button>
                <button type="button" class="btn btn-primary btn-sm"
                    @click="changeCookiesConsent(true, true)" :aria-label="translate('cookies.accept-all')">{{translate("cookies.accept-all")}}</button>
            </div>
        </div>
    </div>

    <div class="modal fade" tabindex="-1" id="modalCookies">
        <div class="modal-dialog modal-dialog-centered">

            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{{translate("cookies.modal-title")}}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <small>{{translate("cookies.modal-intro")}}</small>
                    <hr>
                    <div class="form-check form-switch ps-0">
                        <label class="form-check-label" for="toggleAnalyticsCookies">Google Analytics (gtag.js)<br /><small
                                class="text-muted">{{translate("cookies.analytics-intro")}}<br />{{translate("cookies.analytics-cookies")}}<br /><a
                                    href="https://support.google.com/analytics/answer/6004245">{{translate("shared.learn-more")}}</a></small></label>
                        <input class="form-check-input" type="checkbox" id="toggleAnalyticsCookies" v-model="consentGoogleAnalytics">
                    </div>
                    <hr>
                    <div class="form-check form-switch ps-0">
                        <label class="form-check-label" for="toggleLocalStorageCookies">Local Storage<br /><small
                                class="text-muted">{{translate("cookies.local-storage-intro")}}<br />{{translate("cookies.local-storage-cookies")}}</small></label>
                        <input class="form-check-input" type="checkbox" id="toggleLocalStorageCookies" v-model="consentLocalStorage">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-light"
                        data-bs-dismiss="modal">{{translate("shared.cancel")}}</button>&nbsp;
                    <button type="button" class="btn btn-primary" @click="changeCookiesConsent()" data-bs-dismiss="modal">{{translate("shared.validate")}}</button>
                </div>
            </div>
        </div>
    </div>`,
    created() {

        var cookieManager = localStorage.getItem("cookieManager");

        if (cookieManager) {

            var consent = JSON.parse(cookieManager);
            this.consentGoogleAnalytics = consent.consentGoogleAnalytics;
            this.consentLocalStorage = consent.consentLocalStorage;
        }

        this.$emit("change-cookies-consent", this.consentGoogleAnalytics, this.consentLocalStorage);
    },
    methods: {
        translate(key, returnKeyIfNotFound) {

            return this.translations.length > 0 ? this.translationManager.translate(this.translations, key, this.currentLanguage, returnKeyIfNotFound) : "";
        },
        changeCookiesConsent(consentGoogleAnalytics, consentLocalStorage) {

            // Set the local values

            this.consentGoogleAnalytics = consentGoogleAnalytics !== undefined ? consentGoogleAnalytics : this.consentGoogleAnalytics;
            this.consentLocalStorage = consentLocalStorage !== undefined ? consentLocalStorage : this.consentLocalStorage;

            // Set the booleans in the 'cookieManager' Local Storage value

            localStorage.setItem("cookieManager", JSON.stringify({ consentGoogleAnalytics: this.consentGoogleAnalytics, consentLocalStorage: this.consentLocalStorage }));

            // Hide the cookie bar

            this.displayCookieBar = false;

            // Send the information to the parent

            this.$emit("change-cookies-consent", this.consentGoogleAnalytics, this.consentLocalStorage);
        }
    }
};

export default CookieManager;