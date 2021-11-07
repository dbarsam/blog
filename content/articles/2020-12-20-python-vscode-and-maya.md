---
title: Set up VSCode to Debug Python in Maya
date: 2020-12-20T10:04:07.02
category: dev setup
tags: Python,Maya,VSCode
slug: python-vscode-maya
authors: db
summary: A small tweak to adapt the VSCode auto-attach to work with Maya
header_cover: /images/article-bg.png
---

In the [previous series of articles], we built a quasi auto-attach workflow to debug 3ds Max's Python scripts with VSCode.  Fortunately, that workflow was general enough that trying to apply that to Maya only requires some slight tweaking.

## `bootstrap.mel`

The Maya [command line] interface does not expose any way to execute a Python script.  However, it does accept [Mel Scripts] and we can easily create a `bootstrap.mel` instead.  Since our goal is to keep the work centralized in the `bootstrap.py` script, the resulting MEL script simply executes that file:

```mel
// Execute the Python bootstrap script
string $python_env = getenv("PROJECT_MAYA_PYTHON_SCRIPT");
string $python_files[] = stringToStringArray($python_env, ";");
for( $python_file in $python_files )
{
    string $filename = fromNativePath($python_file);
    print("Executing " + $filename + " python file\n");
    python("exec(open('" + $filename + "').read())");
}
```

We follow the same model as before and use environment variables to pass parameters into the process.  We use the new `PROJECT_MAYA_PYTHON_SCRIPT` environment variable to contain a list of `;` separated python files that the MEL script will execute using MEL script's `python` command.

## Updated Launcher

We need to update the `launcher.json` file in VSCode to account for the new executable, command line, and our environment variable:

```json
{
    "name": "Maya 2018",
    "type": "cppvsdbg",
    "request": "launch",
    "program": "${env:ProgramW6432}\\Autodesk\\Maya2018\\bin\\maya.exe",
    "args": [
        "-script",
        "${workspaceFolder}\\scripts\\bootstrap.mel"
    ],
    "stopAtEntry": false,
    "cwd": "",
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
        // PROJECT_MAYA_PYTHON_SCRIPT contains a `;` separated list of filenames to run at startup in `bootstrap.mel`
        {
            "name": "PROJECT_MAYA_PYTHON_SCRIPT",
            "value": "${workspaceFolder}\\scripts\\bootstrap.py"
        }
    ]
}
```

And we still need to add the compound job that launches this new companion launch configuration with the generic `Python: Remote Attach` auto-attach configuration from the previous article:

```json
{
    "name": "Python Maya 2018",
    "configurations": [
        "Maya 2018",
        "Python: Remote Attach"
    ]
}
```

We're still following the same workflow from our previous 3ds Max example.  The only real difference with Maya is the addition of a `bootstrap.mel`, which is only needed as a workaround to Maya's command line interface.

[command line]: https://help.autodesk.com/view/MAYAUL/2018/ENU/?guid=GUID-2E5D1D43-DC3D-4CB2-9A35-757598220F22
[MEL scripts]: https://help.autodesk.com/view/MAYAUL/2018/ENU/?guid=GUID-60178D44-9990-45B4-8B43-9429D54DF70E
[previous series of articles]: {filename}2020-11-30-python-vscode-and-max.md
