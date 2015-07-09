({
    "baseUrl": ".",
    "out": "bundles/oira.cms.js",
    "include": ["patterns-cms"],
    "insertRequire": ["patterns-cms"],
    "name": "almond",
    "mainConfigFile": 'main.js',
    "optimize": "none",
    "paths": {
        "redactor":             "redactor/redactor",
        "pat-redactor":         "bower_components/pat-redactor/src/pat-redactor",
        "pat-pluggable":        "bower_components/patternslib/src/core/pluggable",
        "jquery.ui":            "nuplone_components/jquery-ui",
        "nuplone-behaviour":    "nuplone_components/behaviour",
        "nuplone-editlink":     "nuplone_components/editlink",
        "nuplone-ordering":     "nuplone_components/ordering",
        "nuplone-z3cform":      "nuplone_components/z3cform",
        "nuplone-css-browser-selector": "nuplone_components/css_browser_selector"
    },
    "shim": {
        "jquery.browser":               { deps: ["jquery"] },
        "jquery.ui":                    { deps: ["jquery"] }
    }
})
