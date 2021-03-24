/*jshint esversion: 8 */

window.addEventListener('load', function () {

    showPage(new URLSearchParams(window.location.search).get('page'));
});

function showPage(page) {

    page = !page ? "home" : page; // la page d'accueil est la valeur par défaut si on ne passe pas d'argument page

    ["home"].forEach(value => { document.getElementById(value).style.display = page == value ? "block" : "none"; });
}

/* HELPERS */

String.prototype.toId = function () {
    return this.toLowerCase().replace(/[^a-zA-Z0-9]+/g, "-");
};

function getLanguageFromISOCode(code) {

    dictionary = { "fr": "Français", "nl": "Néerlandais", "en": "Anglais", "de": "Allemand", "ar": "Arabe" };

    return dictionary.hasOwnProperty(code) ? dictionary[code] : "Inconnu";
}

document.querySelectorAll('.smooth-scroll').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});