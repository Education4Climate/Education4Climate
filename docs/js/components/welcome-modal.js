/*jshint esversion: 8 */

/**
 * @file Manages the welcome modal
 * - Displays the welcome modal if user has not yet seen it in the current session (using sessionStorage).
 * - Hides and remembers that the modal has been seen in the current session.
 * @author Quentin V.
 */

import TranslationManager from "../managers/translation-manager.js";

var WelcomeModal = {
    data() {
        return {
            translationManager: new TranslationManager(),
            displayWelcomeModal: !sessionStorage.welcomeModalDismissed
        };
    },
    props: ['translations', 'currentLanguage', 'methodologyDocument'],
    template: `<div id="welcome-modal" class="welcome-modal" v-if="displayWelcomeModal">
                   <div class="welcome-modal-content">
                       <div v-html="translate('shared.welcome-modal')
                           .replace('{0}', methodologyDocument)
                           .replace('{1}','<a href=&quot;https://www.theshifters.org/gl/belgique/&quot; target=&quot;_blank&quot;><img style=&quot;max-width: 50px;&quot; src=&quot;./img/logo_shifters_belgium.svg&quot;></a>')"></div>
                           <p style="text-align: right;"><a class="btn btn-primary btn-lg" @click="dismissWelcomeModal" v-html="translate('shared.welcome-modal-dismiss-button')"></a></p>
                       </div>
               </div>`,
    methods: {
        translate(key, returnKeyIfNotFound) {
            return this.translations.length > 0 ? this.translationManager.translate(this.translations, key, this.currentLanguage, returnKeyIfNotFound) : "";
        },
        dismissWelcomeModal() {
            sessionStorage.welcomeModalDismissed = true; // Update the sessionStorage flag           
            this.displayWelcomeModal = false;            // Update the property to hide the modal
        }
    }
};

export default WelcomeModal;

