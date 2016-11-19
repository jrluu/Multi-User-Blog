module.exports = function(grunt) {

    // 1. All configuration goes here
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        //Compress html
        htmlmin: {
            dist: {                                      // Target
              options: {                                 // Target options
                removeComments: true,
                collapseWhitespace: true
              },
              files: [{
                expand: true,
                cwd: 'templates/assets/',
                src: ['**/*.html'],
                dest: 'templates/',

              }]
            },
        },

        //Compress CSS
        cssmin: {
          target: {
            files: [{
              'FrontEnd/build/css/production.min.css':['FrontEnd/assets/css/*.css']
            }]
          }
        },

        //Concat JS  files
        concat: {
            js: {
                src: [
                    'FrontEnd/assets/js/bootstrap.js', // Ordering matters
                    'FrontEnd/assets/js/*.js'
                ],
                dest: 'FrontEnd/build/js/production.js',
            },
        },

        //Compress JS
        uglify: {
            build: {
                src: 'FrontEnd/build/js/production.js',
                dest: 'FrontEnd/build/js/production.min.js'
            }
        },

        //Compress images
        imagemin: {
            dynamic: {
                files: [{
                    expand: true,
                    cwd: 'FrontEnd/assets/img/used/',
                    src: ['**/*.{png,jpg,gif}'],
                    dest: 'build/img/'
                }]
            }
        },

        //Turn SASS files to CSS
        sass: {
          dist: {
            files: [{
              expand: true,
              cwd: 'FrontEnd/assets/sass/',
              src: ['*.scss'],
              dest:'FrontEnd/assets/css/',
              ext: '.css'
            }]
          }
        },


        //Runs task based on file changes
        watch: {
          js_change: {
            files: ['FrontEnd/assets/js/*'],
            tasks: ['concat', 'uglify'],
          },
          image_change:{
            files:['FrontEnd/assets/img/used/*'],
            tasks:['imagemin'],
          },
          html_change:{
            files:['templates/assets/*'],
            tasks:['htmlmin'],
          },
          css_change:{
            files:['FrontEnd/assets/sass/*.scss'],
            tasks:['sass', 'cssmin'],

          }


        },

    });

    // 3. Where we tell Grunt we plan to use this plug-in.
    grunt.loadNpmTasks('grunt-contrib-htmlmin');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-imagemin');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');



    // 4. Where we tell Grunt what to do when we type "grunt" into the terminal.
    grunt.registerTask('default', ['sass','htmlmin','cssmin','concat', 'uglify','imagemin']);

};
