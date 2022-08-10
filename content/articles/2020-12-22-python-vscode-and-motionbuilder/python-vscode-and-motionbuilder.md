---
title: Set up VSCode to Debug Python in MotionBuilder
date: 2020-12-22 11:45
tags: python, motionbuilder, vscode
slug: python-vscode-motionbuilder
authors: db
summary: A small tweak to adapt the VSCode auto-attach to work with MotionBuilder
header_cover: /images/article-bg.png
status: published
categories: developer set-up
category: developer set-up
type: article
---
<!--
spell-checker:ignore
-->
In the [previous series of articles], we built a quasi auto-attach workflow to debug 3ds Max's Python scripts with VSCode.  We recently tweaked it for Maya and we can easily tweak it again for MotionBuilder.

## Updated Launcher

Unlike Maya, MotionBuilder provides a native way to launch Python scripts on startup and this makes the workflow easier to migrate from 3ds Max than Maya.  The easiest startup script command is taken directly from the [command line] help:

```cmd
motionbuilder.exe -console -verbosePython script.py
```

With that command line, we can update the `launcher.json` file in VSCode accordingly:

```json
{
    "name": "MotionBuilder 2018",
    "type": "cppvsdbg",
    "request": "launch",
    "program": "${env:ProgramW6432}\\Autodesk\\MotionBuilder 2018\\bin\\x64\\motionbuilder.exe",
    "args": [
        "-console",
        "-verbosePython",
        "${workspaceFolder}\\scripts\\bootstrap.py"
    ],
    "stopAtEntry": false,
    "cwd": "",
    "logToFile": true,
    "environment": [
        // PROJECT_SCRIPTS contains a `;` separated list of filenames to run at startup in `bootstrap.py`
        {
            "name": "PROJECT_SCRIPTS",
            "value": "${workspaceRoot}\\.env27\\Scripts\\activate_this.py"
        },
        // PROJECT_DEBUG_PORT / PROJECT_DEBUG_HOST should match 'Remote Attach' below.
        {
            "name": "PROJECT_DEBUG_PORT",
            "value": "5678"
        },
        {
            "name": "PROJECT_DEBUG_HOST",
            "value": "localhost"
        },
        // PROJECT_LOG_LEVEL for the level of `logging` statements
        {
            "name": "PROJECT_LOG_LEVEL",
            "value": "DEBUG"
        },
    ],
}
```

And we still need to add the compound job that launches this new companion launch configuration with the generic `Python: Remote Attach` auto-attach configuration from the previous article:

```json
{
    "name": "Python MotionBuilder 2018",
    "configurations": [
        "MotionBuilder 2018",
        "Python: Remote Attach"
    ]
}
```

## Updated `bootstrap.py`

MotionBuilder executes Python scripts [slightly differently] than what is expected.  Instead of executing the file in the scope of [main scope] module, the script is executed under the `__builtin__` (or [builtins] in Python 3) module.

We can easily fix this by updating the `bootstrap.py` script to accept a collection of scopes using a simple tuple:

```python

....

if __name__ in ("__main__", "__builtin__", "builtins")
    main()
```

Like Maya and 3ds Max, we're still following the same model of grafting a side-car environment via the `bootstrap.py`.  The only difference is a slight tweak needed to handle the peculiarities of MotionBuilder's embedded Python environment.

[main scope]: https://docs.python.org/3/library/__main__.html
[builtins]: https://docs.python.org/3/library/builtins.html#module-builtins
[slightly differently]: https://forums.autodesk.com/t5/motionbuilder-forum/whats-wrong-with-main/td-p/4254363
[previous series of articles]: {filename}../2020-11-30-python-vscode-and-max/note.md
