({
    baseUrl: ".",
    out: "bundles/ploneintranet.js",
    include: ["patterns"],
    name: "almond",
    mainConfigFile: 'main.js',
    wrap: {
        endFile: "bower_components/patternslib/src/wrap-end.js"
    },
    optimize: "none",
    paths: {
        "almond": "bower_components/almond/almond"
    }
})
