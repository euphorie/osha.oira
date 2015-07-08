({
    "baseUrl": ".",
    "out": "bundles/oira.cms.js",
    "include": ["patterns-cms"],
    "insertRequire": ["patterns"],
    "name": "almond",
    "mainConfigFile": 'main.js',
    "optimize": "none",
    "paths": {
        "redactor": "redactor/redactor",
        "pat-redactor": "bower_components/pat-redactor/src/pat-redactor",
        "pat-pluggable": "bower_components/patternslib/src/core/pluggable"
    }
})
