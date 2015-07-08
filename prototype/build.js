({
    baseUrl: ".",
    out: "bundles/ploneintranet.js",
    include: ["patterns"],
    insertRequire: ["patterns"],
    name: "almond",
    mainConfigFile: 'main.js',
    optimize: "none"
})
