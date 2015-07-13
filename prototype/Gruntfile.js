module.exports = function(grunt) {

  grunt.initConfig({
    uglify: {
      build: {
        src: 'bundles/oira.cms.js',
        dest: 'bundles/oira.cms.min.js'
      }
    },
    cssmin: {
      target: {
        files: {
            'redactor/redactor.min.css': ['redactor/redactor.css']
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.registerTask('default', ['uglify']);
};
