/*jshint esversion: 8 */

/**
 * @file Gathers all the app constants.
 * @author Quentin V.
 */

const DATA_FOLDER = "data";
const SCHOOLS_FILE = DATA_FOLDER + "/" + "schools.json";
const PAGE_SIZE = 20;
const AVAILABLE_LANGUAGES = ["fr", "nl", "en"];
const DEFAULT_LANGUAGE = "en";
const MENU_ITEMS = ["programs", "courses", "teachers", "report", "wizard", "dashboard"];
const GOOGLE_ANALYTICS_ID = "G-8JCFK91KH7";
const WIZARD_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbxWF4IAssBIE5p_wayVj9Zr110YJao4mAENWy-sHuzYRiZJWM2tWjrdvrm7BHV7VK1GNQ/exec";

const DEFAULT_THEME = "light";
const ALTERNATE_THEME = "dark";

export { DATA_FOLDER, SCHOOLS_FILE, PAGE_SIZE, AVAILABLE_LANGUAGES, DEFAULT_LANGUAGE, MENU_ITEMS, GOOGLE_ANALYTICS_ID, DEFAULT_THEME, ALTERNATE_THEME, WIZARD_APPS_SCRIPT };