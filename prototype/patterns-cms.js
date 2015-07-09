/* Patterns bundle configuration.
 *
 * This file is used to tell r.js which Patterns to load when it generates a
 * bundle. This is only used when generating a full Patterns bundle, or when
 * you want a simple way to include all patterns in your own project. If you
 * only want to use selected patterns you will need to pull in the patterns
 * directly in your RequireJS configuration.
 */
define([
    "pat-registry", // Keep separate as first argument to callback
    "jquery.browser",
    "jquery.ui",
    "nuplone-behaviour",
    "nuplone-css-browser-selector",
    "nuplone-editlink",
    "nuplone-ordering",
    "nuplone-z3cform",
    "pat-redactor"
], function(registry) {
    registry.init();
    return registry;
});
