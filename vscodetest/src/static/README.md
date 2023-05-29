Do not version files in this directory. This directory is for the output of our
gulp build process.

Generating the Static Files
===========================
To generate static files in `~/cloudbolt/src/static` based on the source files
in `~/cloudbolt/src/static_src`:

    cd ~/cloudbolt/src/static_src/
    npm run gulp

If you are using `dev_tools/startdev.sh`, your static files will be
automatically re-built when making changes to the source files in `static_src`.

Setup
=====
Perform this one-time setup to install the dependencies required by our gulp
build process:

    cd ~/cloudbolt/src/static_src/
    npm install
