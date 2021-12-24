---
title: Set up VSCode to Debug Python in 3ds Max - V
date: 2020-12-09 21:02
tags: 3ds max, python, vscode
slug: python-vscode-max-5
authors: db
summary: Part V&#58; A slight tweak to get us an VSCode auto-attach configuration
header_cover: /images/article-bg.png
status: published
categories: developer set-up
category: developer set-up
type: article
---

In the [previous article], we established an auto-attach workflow with VSCode that was based on a passive sleep delay.  Now we'll refine that process by using the same network strategy used by the remote debugger.

## Preliminary Connection

The current solution synchronizes VSCode and `ptvsd` by making VSCode sleep before it attempts the connection.  VSCode doesn't provide a native delay so we take advantage of the `preLaunchTask` attribute to sleep using a local command.  Otherwise the `attach` configuration will timeout because of a misalignment of VSCode's and `ptvsd` connection requests.  The sleep works around the misalignment, but it's an adhoc synchronization that needs to be tuned to for each environment.

Instead, we can replace that passive sleep with a more active, on-demand, pre-connect network handshake.  The remote debugging workflow already synchronizes VSCode and `ptvsd` with a network connection in the original `wait_and_attach` call.  Our plan duplicates that same approach and uses another connection request as a waiting mechanism.

This *preliminary* connection is a very simple [socket] connection.  The server socket waits for a connection and the client socket repeatedly makes connection requests until it succeeds.  After the connection has been established, we can assumed some level of synchronization between the server and client and simply close the connection.  The execution continues and, shortly afterwards, VSCode makes the *real* connection to `ptvsd` the same as before.

## The 'Listen' Socket

We wrap the server socket logic into a `_listen` function with host and port parameters.

```python
import logging
import socket
import time

def _listen(host, port):
    """Launches a very simple server socket on `host`, `port` to wait for a socket connection

    Args:
        host (str): The host name.
        port (int): The host port.
    """
    logger = logging.getLogger(__name__)
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ss.settimeout(60)
    ss.bind((host, port))
    ss.listen(1)

    logger.debug("Listening on %s:%s", host, port)
    cs, _ = ss.accept()
    logger.debug("Connected to %s:%s", host, port)

    cs.close()
    ss.close()
    time.sleep(1)
```

There are a few things to note:

1. The main part of this function is the `socket.accept` function, which will wait for the incoming connection from our client socket.  Everything else is just setting up socket to manage the connection as cleaning as possible.

2. We're using the same host and port in both the preliminary and real connections so we also enable the `socket.SO_REUSEADDR` option.

3. After we close the connection, we `time.sleep` for an additional 1 second.  This is a basic safety measure taken so that the system can close the socket.  Otherwise the socket may remains in a `TIME_WAIT` state that prevents its re-use by the same host, which is what we want to do later on.

## The 'Connect' Socket

We wrap the request logic into a `_connect` function with a pair of host and port parameters:

```python
import logging
import socket
import time

def _connect(host, port):
    """Launches a very simple client socket on `host`, `port` to repeatedly try a connection.

    Args:
        host (str): The host name.
        port (int): The host port.
    """
    logger = logging.getLogger(__name__)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR , 1)
    s.settimeout(60)
    connected = False
    while not connected:
        logger.debug("Polling %s:%s for connection.", host, port)
        try:
            s.connect((host, port))
            connected = True
        except Exception:
            time.sleep(1)
    s.close()
    time.sleep(1)
    logger.debug("Connected to %s:%s", host, port)

```

Unlike the listen function, the client socket has no blocking `accept` function.  Instead we enter into a perpetual loop where we repeatedly connect to the host and port.  If the connection fails, it will raise an exception which we handle by sleeping a little bit and then trying again.  However, if the connection is successful then it sets the connected flag to `True` and exits the loop.

After we've exited the loop, we close the socket and sleep for one more time to allow the socket to move from `TIME_WAIT` to the proper closed state.

## Connect then Wait For Attach

The `_connect` function is added to the same `bootstrap.py` file that we've been using and specifically to the `_attach` function. Inside that function, the `_connect` is called before we run `ptvsd.wait_for_attach()`.  We use the same host and port for both the preliminary and real connections, which we can do because we're careful with closing the socket connection after using it for the first time.

```python
def _attach(host, port):
    """Attaches to a remote debugger on a host and port

    Args:
        host (str): The host name.
        port (int): The host port.
    """
    logger = logging.getLogger(__name__)
    try:
        import ptvsd
    except ImportError:
        logger.exception("Could not import module `ptvsd`.  Is installed?")
        return

    logger.info("Notifying IDE for auto-attach on %s:%s", host, port)
    _connect(host, port)

    logger.info("Waiting for debug client to connect on %s:%s", host, port)
    ptvsd.enable_attach(address=(host, port), redirect_output=True)
    ptvsd.wait_for_attach()
```

Because the call to `ptvsd` is part of the application's start-up sequence we don't know exactly when it will be called.  The new `_connect` function loops until it makes connection to the respective `_listen` function called by the `preTaskFunction` attribute.  Since this function is part of the application's startup sequence, chances are the `listen` will be already waiting and the initial `connect` function will be the only connection attempted.

## Listen Script

Because we've added `_connect` to the bootstrap script, we keep things self contained and also add the `_listen` function to the script.  However, that means that we need to update the main entry point to have two modes:  One for the new Python `attach` configuration and one for the current C++ `launch` configuration.

```python
import logging
import os
import socket
import time

def main():
    """Main entry point for the bootstrap script"""

    debug_port = os.getenv("PROJECT_DEBUG_PORT", "")
    debug_host = os.getenv("PROJECT_DEBUG_HOST", "")
    debug_attach = os.getenv("PROJECT_AUTOATTACH", "")
    scripts = os.getenv("PROJECT_SCRIPTS", "").split(";")
    log_level = os.getenv("PROJECT_LOG_LEVEL", logging.DEBUG)

    logging.basicConfig(level=log_level, format="%(message)s")
    logger = logging.getLogger(__name__)
    logger.info("Python Bootstrap script - start -")
    logger.info('Initialized logging to "%s"', log_level)

    if debug_attach:
        _listen(debug_host, int(debug_port))
    else:
        if scripts:
            _exec(scripts)
        else:
            logger.warning("Could not find variable PROJECT_SCRIPTS does not exist or is empty.  Skipping script execution.")

        if debug_port and debug_host:
            _attach(debug_host, int(debug_port))
        else:
            logger.warning("Environment variable PROJECT_DEBUG_HOST/PROJECT_DEBUG_PORT do not exist or are empty.  Python debugging disabled.")

    logger.info("Python Bootstrap script - stop -")

if __name__ == "__main__":
    main()
```

We've updated the bootstrap script with a new parameter: `PROJECT_AUTOATTACH`.  If that value exists, the logic goes straight into the `_listen` function, where it will call the `socket.accept()` and wait for the first connection request.  However, if that variable doesn't exist, then the logic goes through the same logic as before.

We could have created a second script to handle this new mode implementation instead of putting it into our existing `bootstrap.py` script.  That's perfectly valid and would be strictly adhering to the [Single Responsibility Principle], but because we're putting the mode toggle on the module instead of the module's functions, it's less egregious and somewhat acceptable -- especially give how small our `bootstrap.py` still is.

## The Auto-Attach Task

With our `bootstrap.py` modified, we can now create a new VSCode task to replace the `sleep` task.  Because we've engineered this auto-attach with Python, we swap out the `COMSPEC` process with the local `python.exe` from our virtual environment and use that to call our `bootstrap.py` file.  We toggle the mode with by defining a `PROJECT_AUTOATTACH` and specify the `PROJECT_DEBUG_PORT` and `PROJECT_DEBUG_HOST` which will be passed onto the `_listen` function.

```json
{
    "label": "auto-attach",
    "type": "process",
    "command": "${workspaceFolder}\\.env27\\Scripts\\python.exe",
    "args": [
        "${workspaceFolder}\\scripts\\bootstrap.py",
    ],
    "options": {
        "env": {
            "PROJECT_DEBUG_PORT": "5678",
            "PROJECT_DEBUG_HOST": "localhost",
            "PROJECT_AUTOATTACH": "1"
        }
    },
    "group": "none",
    "presentation": {
        "reveal": "never",
        "showReuseMessage": false
    }
},
```

And change the `attach` configuration's `preLaunchTask` value from `sleep` to `auto-attach`.

```json
{
    "name": "Python: Remote Attach",
    "type": "python",
    "request": "attach",
    "justMyCode": true,
    "processName": "3dsmax.exe",
    "host": "localhost",
    "port": 5678,
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}",
            "remoteRoot": "${workspaceFolder}"
        }
    ],
    "preLaunchTask": "auto-attach",
},
```

## Auto-Attach vs Sleep

This socket auto-attach task is a refinement that makes the overall workflow more flexible in exchange for a more complicated workflow.

The choice to use it will matter on the complexity of the project.  For example, if the project is accessed by multiple people, across different environments, then the sleep value is a developer specific personal choice, one that will most likely be tuned and re-tuned. Values that are personal choices should not be checked into source control.  Otherwise, the project will have a (hopefully, cordial) fight between developers that will result in a series of meaningless back-and-forth commits or a weird ignore rule.

The socket auto-attach adds a little bit of engineering for an adaptable sleep that's great for that kind of situation.  However, if the project is less complex, like a script written by one person, then the sleep attach is probably good enough.

## The Final Hodge Podge Solution

Finally, we now have a collection of components, assembled into something resembling a seamless debugging workflow:

1. Create a fresh virtual environment.

2. Install the project as an editable package into that virtual environment.

3. Create a startup script for the application that:

    1. Grafts the virtual environment onto the application's Python installation with the `activate_this.py`.

    2. Configures the Python logging as needed.

    3. Invokes `ptvsd`'s attach functions.

4. Configure a VSCode C++ `launch` configuration that runs the application with the start-up script without changing any global application state (e.g. use the application's command line).

5. Configure a VSCode Python `attach` configuration that attaches to the application.

6. Create a `sleep` / `auto-attach` task for the `attach`'s `preLaunchTask` attribute.

7. Create a compound configuration that launches both the `launch` and the `auto-attach` configuration at the same time.

This infrastructure yields a quasi `auto-attach` workflow that delivers a equivalent `launch` experience with the ++F5++ key.

### The final `bootstrap.py` file

```python
"""
Standalone script to attach to a remote debugging.

The script will inject various sites and execute startup files in
order to set-up the Python environment for development.

In addition the script will also use `ptvsd` to remotely attach to
a remote debugger to the current process.  In some applications this
is the only way to debug Python code.

This script expects the following environment variables:

- `PROJECT_SCRIPTS` A semi-colon separated list of files to execute with
  `exec`.

- `PROJECT_DEBUG_HOST` The host name of the remote debugger to attach to.

- `PROJECT_DEBUG_PORT` The port number of the remote debugger to attach to.

- `PROJECT_LOG_LEVEL` The initial logging level this script will use.

- `PROJECT_AUTOATTACH` Flag to toggle auto-attach mode.  Enable when used pre-launch task.

.. note::

    This script does not install ptvsd and expects the module to be already installed,
    or installed during the site injection or exec execution step.

"""
import logging
import os
import socket
import time
import sys


def _connect(host, port):
    """Launches a very simple client socket on `host`, `port` to repeatedly try a connection.

    Args:
        host (str): The host name.
        port (int): The host port.
    """
    logger = logging.getLogger(__name__)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR , 1)
    s.settimeout(60)
    connected = False
    while not connected:
        logger.debug("Polling %s:%s for connection.", host, port)
        try:
            s.connect((host, port))
            connected = True
        except Exception:
            time.sleep(1)
    s.close()
    time.sleep(1)
    logger.debug("Connected to %s:%s", host, port)


def _listen(host, port):
    """Launches a very simple server socket on `host`, `port` to wait for a socket connection

    Args:
        host (str): The host name.
        port (int): The host port.
    """
    logger = logging.getLogger(__name__)
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ss.settimeout(60)
    ss.bind((host, port))
    ss.listen(1)

    logger.debug("Listening on %s:%s", host, port)
    cs, _ = ss.accept()
    logger.debug("Connected to %s:%s", host, port)

    cs.close()
    ss.close()
    time.sleep(1)


def _exec(filenames):
    """Execute a collection of Python files in the current environment

    Args:
        scripts (list): A list of filename.
    """
    logger = logging.getLogger(__name__)

    script_paths = [sf for sf in filenames if os.path.exists(sf)]
    if not script_paths:
        logger.warning("User provided not scripts to execute.  Skipping script execution.")

    for script_path in script_paths:
        logger.info("Executing Script: %s", script_path)
        with open(script_path) as f:
            contents = f.read()
        try:
            exec(contents, {"__file__": script_path})
        except Exception as e:
            logger.exception("   ! %s failed to execute", script_path)


def _attach(host, port):
    """Attaches to a remote debugger on a host and port

    Args:
        host (str): The host name.
        port (int): The host port.
    """
    logger = logging.getLogger(__name__)
    try:
        import ptvsd
    except ImportError:
        logger.exception("Could not import module `ptvsd`.  Is installed?")
        return

    logger.info("Notifying IDE for auto-attach on %s:%s", host, port)
    _connect(host, port)

    logger.info("Waiting for debug client to connect on %s:%s", host, port)
    ptvsd.enable_attach(address=(host, port), redirect_output=True)
    ptvsd.wait_for_attach()


def main():
    """Main entry point for the bootstrap script"""

    debug_port = os.getenv("PROJECT_DEBUG_PORT", "")
    debug_host = os.getenv("PROJECT_DEBUG_HOST", "")
    debug_attach = os.getenv("PROJECT_AUTOATTACH", "")
    scripts = os.getenv("PROJECT_SCRIPTS", "").split(";")
    log_level = os.getenv("PROJECT_LOG_LEVEL", logging.DEBUG)

    logging.basicConfig(level=log_level, format="%(message)s")
    logger = logging.getLogger(__name__)
    logger.info("Python Bootstrap script - start -")
    logger.info('Initialized logging to "%s"', log_level)

    if debug_attach:
        _listen(debug_host, int(debug_port))
    else:
        if scripts:
            _exec(scripts)
        else:
            logger.warning("Could not find variable PROJECT_SCRIPTS does not exist or is empty.  Skipping script execution.")

        if debug_port and debug_host:
            _attach(debug_host, int(debug_port))
        else:
            logger.warning("Environment variable PROJECT_DEBUG_HOST/PROJECT_DEBUG_PORT do not exist or are empty.  Python debugging disabled.")

    logger.info("Python Bootstrap script - stop -")

if __name__ == "__main__":
    main()
```

### The final `launch.json` file

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Max 2018",
            "type": "cppvsdbg",
            "request": "launch",
            "program": "${env:ProgramW6432}\\Autodesk\\3ds Max 2018\\3dsmax.exe",
            "args": [
                "-U",
                "PythonHost",
                "${workspaceFolder}\\scripts\\bootstrap.py"
            ],
            "stopAtEntry": false,
            "cwd": "",
            "environment": [
                // Ensure that 3ds Max is ahead of any other Qt based application.
                {
                    "name": "PATH",
                    "value": "C:\\Program Files\\Autodesk\\3ds Max 2018;${env:PATH}"
                },
                // PROJECT_SCRIPTS contains a `;` separated list of filenames to run at startup
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
                }
            ]
        },
        {
            "name": "Python: Remote Attach",
            "type": "python",
            "request": "attach",
            "justMyCode": true,
            "host": "localhost",
            "port": 5678,
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "${workspaceFolder}"
                }
            ],
            "preLaunchTask": "auto-attach"
        }
    ],
    "compounds": [
        {
            "name": "Python Max 2018",
            "configurations": [
                "Max 2018",
                "Python: Remote Attach"
            ]
        }
    ]
}
```

### The final `tasks.json` file

```json
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "2.0.0",
    "tasks": [{
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
                "showReuseMessage": false
            }
        },
        {
            "label": "auto-attach",
            "type": "process",
            "command": "${workspaceFolder}\\.env27\\Scripts\\python.exe",
            "args": [
                "${workspaceFolder}\\.vscode\\bootstrap.py"
            ],
            "options": {
                "env": {
                    "PROJECT_DEBUG_PORT": "5678",
                    "PROJECT_DEBUG_HOST": "localhost",
                    "PROJECT_AUTOATTACH": "1"
                }
            },
            "group": "none",
            "presentation": {
                "reveal": "never",
                "showReuseMessage": false
            }
        }
    ]
}
```

## Potential Next Steps

This has been a particularly exhaustive tour of a rather specific Python development workflow.  We could go on as there's always room for improvements or slight tweaks.

### PYTHONPATH

If you're working on a single Python script with no external package, you could skip the grafting and just configuration the `PYTHONPATH` environment variable to include your Python script.

### `pip` / `virtualenv` alternatives

We chose `pip` and `virtualenv` as they were the default Python development tools.  There's nothing preventing the project from taking advantage of the `PYTHONPATH` environment variable and use a `vendor` folder or some other manual process to create an equivalent `site-packages` folder.  Just be sure to include `ptvsd` in your solution.

### `ptvsd` vs `debugpy`

It has to be noted that `ptvsd` has been deprecated in favour of the newer [debugpy].  This tutorial did not make that switch because it's a swap-able component and, embarrassingly enough, it didn't work right out of the box.  Follow `debugpy`'s [#262] for more information.

### Scalability

This set-up seems like a tediously manual process.  That's not wrong, but it was done that way to learn about the process instead of providing a readily available solution.  There are definitely ways to streamline the process if you need this for multiple projects. For instance, it could be incorporated into a project template, like a [cookiecutter], or made into an VSCode extension.

### Other VSCode plugins

While our example used 3ds Max, it should be general enough to adapt to another application.  These are already extensions out there solving similar problems, most notably [Blender Development] for Blender, [MayaCode] for Maya, and the more general [Python C++ Debugger].  In fact, a quick survey suggests that Blender and Maya are the hot topics these days.  See [Blender-VSCode-Debugger], [Blender Debugger for VS Code (and Visual Studio)], [MayaPy], and [MayaPort] extensions and the vast collection [How To VSCode and Blender] and [How To VSCode and Maya] tutorials for more examples.

### PyCharm?

We do see you [PyCharm]. Maybe next time.

[socket]: https://docs.python.org/3/howto/sockets.html
[single responsibility principle]: https://en.wikipedia.org/wiki/Single-responsibility_principle
[Blender Development]: https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development
[MayaCode]: https://marketplace.visualstudio.com/items?itemName=saviof.mayacode
[Python C++ Debugger]: https://marketplace.visualstudio.com/items?itemName=benjamin-simmonds.pythoncpp-debug
[cookiecutter]: https://cookiecutter.readthedocs.io/
[Blender-VSCode-Debugger]: https://github.com/Barbarbarbarian/Blender-VScode-Debugger
[Blender Debugger for VS Code (and Visual Studio)]:  https://github.com/AlansCodeLog/blender-debugger-for-vscode
[debugpy]: https://pypi.org/project/debugpy/
[#262]: https://github.com/microsoft/debugpy/issues/262]
[MayaPy]: https://marketplace.visualstudio.com/items?itemName=FXTD-Odyssey.mayapy
[MayaPort]: https://marketplace.visualstudio.com/items?itemName=JonMacey.mayaport
[How To VSCode and Blender]: https://googlethatforyou.com?q=vscode%20blender%20tutorial
[How To VSCode and Maya]: https://googlethatforyou.com?q=vscode%20maya%20tutorial
[PyCharm]: https://knowledge.autodesk.com/support/3ds-max/troubleshooting/caas/screencast/Main/Details/34ab44e0-5702-473e-850c-a6b7a86b45f2.html
[previous article]: {filename}2020-12-07-python-vscode-and-max-4.md
