# Browser Screen

A tool to run a browser-based pseudo-screensaver in windows. 

# Motivation

There exist screen-savers that run a webpage, but are fairly inconsisent across Windows versions and configurations, group policies etc.
Automating a version with python and selenium for firefox allows:
1) using an existing browser profile (cookies etc, useful if there is something pw protected you want screen-savered)
2) No dependencies on windows Version and settings.
3) Serving from a static html file. 
4) Logging.
5) Supports multiple monitors, with screensaver starting on a delay (do not ask why, but as why not - RFK)

# Usage 

    # install
    install python 3.6
    install firefox

    git clone https://github.com/psavine42/webscreensaver
    cd webscreensaver
    setup.bat           # this installs some pip packages
    mv ./demo ./prod    # copy the demo config to prod to be read by 
    
    # test - this starts the screen saver 
    test.bat

    # run 
    run.bat 
    
    # or for custom arguments
    python winapiv.py --act run --delay 1 --timeout 27

Config file will have values for test and run configs. Test will basically start the screen saver immediately. 

    {
        "test": {
            "timeout": 0.01,
            "url": "https:///www.google.com",
            "delay": 7,
            "logdir":""
        },
        "run": {
            "timeout": 20,
            "url": "https://www.tocci.com",
            "delay": 7,
            "logdir":""
        }
    }

# Misc
Log files go to %Appdata%/local/webscreensaver/log

