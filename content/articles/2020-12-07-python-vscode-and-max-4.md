---
title: Set up VSCode to Debug Python in 3ds Max - IV
date: 2020-12-07T21:08:47.02
category: dev setup
tags: Python,3ds Max,VSCode
slug: python-vscode-max-4
authors: db
summary: Part IV&#58; VSCode's compound launch configuration
header_cover: /images/article-bg.png
---

In the previous article, we successful created a debugging session from connecting the various pieces of our infrastructure.  We created a Python virtual environment via `virtualenv`, built a `bootstrap.py` to graft it into the application and to execute `ptvsd` at startup, and successfully make the whole contraption work, via VSCode's `Attach to Process` remote debugging configuration. In this article, we'll look up at couple of tweaks to make that manual process into one that's automated.

## Attach vs Launch

VSCode has two main workflows for debugging: `launch` and `attach`.  The `launch` configuration could work, but it requires a very specific set up that executes something equivalent to a `python.exe`.  That won't work in our case because the Python interpreter is buried inside a Windows application, so we're left with `attach` workflow where we manually launch the application, switch to VSCode and execute the `attach` configuration.

While the launch-and-attach workflow does its job, it can become tedious after a while -- especially if unhandled exceptions or crash destabilizes the application so much that the only recourse is to restart the session.  There is, however, some automation tricks that we can incorporate to our current set-up that could remove that friction.

## Companion Launch Configuration

The first trick is to create a `launch` configuration, but not for Python.
Instead we're going to create a *companion* launch configuration for our application, which should use a debugger native to the application.

We configure the new configuration with the [cppvsdg] debugger (from VSCode's [C/C++ debugging] documentation) and include all the settings from our `launch.cmd` script.  Thankfully, this is pretty straight forward:

```json
{
    "name": "3ds Max 2018",
    "type": "cppvsdbg",
    "request": "launch",
    "program": "C:\\Program Files\\Autodesk\\3ds Max 2018\\3dsmax.exe",
    "args": [
        "-U",
        "PythonHost",
        "${workspaceFolder}\\scripts\\bootstrap.py"
    ],
    "stopAtEntry": false,
    "environment": [
        // Ensure that 3ds Max is ahead of any other Qt based application.
        {
            "name": "PATH",
            "value": "C:\\Program Files\\Autodesk\\3ds Max 2018;${env:PATH}"
        },
        // PROJECT_LOG_LEVEL is the logging levele we need for development
        {
            "name": "PROJECT_LOG_LEVEL",
            "value": "DEBUG"
        }
        // PROJECT_DEBUG_PORT / PROJECT_DEBUG_HOST should match 'Remote Attach'.
        {
            "name": "PROJECT_DEBUG_PORT",
            "value": "5678"
        },
        {
            "name": "PROJECT_DEBUG_HOST",
            "value": "localhost"
        },
        // PROJECT_SCRIPTS contains a ';' delimeter list of Python script to run at startup.
        {
            "name": "PROJECT_SCRIPTS",
            "value": "${workspaceRoot}\\.env27\\Scripts\\activate_this.py"
        },
    ],
},
```

This configuration replaces our `launch.cmd` script.  It incorporate the same command line to load the `bootstrap.py` as a start-up script while also specifying the needed environment variables for our workflow.

As a bonus, we're also addressing [another problem] by updating the `PATH` environment to ensure that 3ds Max's executable and libraries are given the top most priority.

## Compound Configuration

We now have an `attach` and `launch` configuration and we can execute them at the same time using a [compound configuration].  The compound configuration is the mechanism to execute multi-target sessions, like what we have now, and it's also pretty straight forward:

```json
{
    "compounds": [
        {
            "name": "Python 3ds Max 2018",
            "configurations": [
                "3ds Max 2018",
                "Python: Remote Attach"
            ]
        }
    ]
}
```

Now hitting <kbd>F5</kbd> will launch both the `3ds Max 2018` and `Python: Remote Attach`.  We would be done here, except for one last thing:  3ds Max takes a good 10-20 seconds before it initializes `ptvsd` and calls the `ptvsd.wait_for_attach()`.  The compound configuration launches all configurations at the same time, so the loading delay cascades into the `attach` call timing out before 3ds Max is ready.

The compound configuration does not support a delay so the only solution is to take advantage of the `launch.json`'s [preLaunchTask] attribute and add an artificial delay to the `attach` configuration.

## 'Delayed' Attach Configuration

The `preLaunchTask` is a generic enough to take in any [Task], so we create one:  `sleep`.

```json
{
    "label": "sleep",
    "type": "process",
    "command": "${env:COMSPEC}",
    "args": [
        "/c",
        "timeout",
        "/t",
        "30",
        "/nobreak"
    ],
    "group": "none",
    "presentation": {
        "reveal": "never",
        "showReuseMessage": false,
    },
},
```

The `sleep` task is a custom VSCode Task in our project's `tasks.json` file that wraps around the `cmd.exe` command [timeout].  We try to avoid any conflicts with shell settings by making this a `process` task instead of a `shell` task.  We explicitly name the [cmd.exe] executable, which is usually available `COMSPEC` environment variable.

For our 3ds Max example we anecdotally select use a hardcoded a time of 30 seconds.  That time will vary on how 3ds max is configured, what's the current system specs, and even if you've launched the application for the first time.  Multiple iterations will keep the application available in memory so subsequent launches will appear shorter.

The implementation of sleep is a personal choice and it could be re-written to use any command.  Our only requirement is that the command delays the original Remote Attach task by desired amount.  After the command is written, it is then plugged into the `preLaunchTask` attribute:

```json
{
    "name": "Python: Remote Attach",
    "type": "python",
    "request": "attach",
    "justMyCode": false,
    "processName": "3dsmax.exe",
    "host": "localhost",
    "port": 5678,
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}",
            "remoteRoot": "."
        }
    ],
    "preLaunchTask": "sleep",
},
```

## Next Step

We now have a collection of components assembled into something that delivers a seamless debugging workflow.  In fact the workflow is good enough that we could start using it right now.  However, in the [Part V], we'll look at an alternative to the sleep command that adds a little more precision to our delay, effectively making our `sleep-attach` workflow into an `auto-attach` workflow.

[activate_this.py]: https://github.com/pypa/virtualenv/blob/main/src/virtualenv/activation/python/activate_this.py
[addsitedir]: https://docs.python.org/3/library/site.html#site.addsitedir
[site]: https://docs.python.org/3/library/site.html
[sys.path]: https://docs.python.org/3/library/sys.html#sys.path
[install_requires vs requirements files]: https://packaging.python.org/discussions/install-requires-vs-requirements/
[__main__]: https://docs.python.org/3/library/__main__.html
[debugger mode]: https://code.visualstudio.com/Docs/editor/debugging
[C/C++ debugging]: https://code.visualstudio.com/docs/cpp/launch-json-reference
[compound configuration]: https://code.visualstudio.com/Docs/editor/debugging#_compound-launch-configurations
[another problem]: {filename}2020-10-29-qt-dll-mismatch.md
[prelaunchtask]: https://code.visualstudio.com/Docs/editor/debugging#_launchjson-attributes
[task]: https://code.visualstudio.com/docs/editor/tasks
[timeout]: https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-R2-and-2012/cc754891(v=ws.11)
[cmd]: https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/cmd
