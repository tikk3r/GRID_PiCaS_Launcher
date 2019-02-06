[![Build Status](https://travis-ci.org/apmechev/GRID_PiCaS_Launcher.svg?branch=restructure)](https://travis-ci.org/apmechev/GRID_PiCaS_Launcher)
[![codecov](https://codecov.io/gh/apmechev/GRID_PiCaS_Launcher/branch/restructure/graph/badge.svg)](https://codecov.io/gh/apmechev/GRID_PiCaS_Launcher)
[![alt text](http://apmechev.com/img/git_repos/GRID_picastools_clones.svg "github clones since 2017-01-25")](https://github.com/apmechev/github_clones_badge)

GRID_picastools
=============

List of tools that are used by PiCaS jobs to interface the User scripts with the job tokens. The scripts are responsible for locking job tokens, downloading the user sandbox, and executing the user scripts. The scripts automatically import Token Fields into the BASH environment before running the scripts. Finally, logs and exit status are uploaded to the Job token. 

