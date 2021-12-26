---
title: Set up VSCode to Debug Python in 3ds Max - III
date: 2020-12-05 19:10
tags: python, 3ds max, vscode
slug: python-vscode-max-3
authors: db
summary: Part III&#58; VSCode's attach to process workflow'
header_cover: /images/article-bg.png
status: published
categories: developer set-up
category: developer set-up
type: article
---

In the [previous article], we had created a Python virtual environment via `virtualenv`'s and built a `bootstrap.py` to graft it into the application.  In this article, we'll take a first pass at incorporating VSCode into our workflow.

## Attach to Process

Developing Python packages for use in external application is a very special edge case.  The [Python debug configurations in Visual Studio Code](https://code.visualstudio.com/docs/python/debugging) only covers the most common Python debugging scenarios and we'll be incorporating the *Attach To Process* one, where we attach the debugger to the already-running application.

That workflow is represented as a `attach` configuration request in the `launch.json`, which is different than the more workflow-friendly `launch` configuration, which launches the process and immediately attaches to it.  The VSCode Python plugin provides an auto-generated `attach` configuration under the `Python: Remote Attach` template:

```python
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
},
```

This `attach` configuration is the same configuration used for *Remote Debugging*.  The only real difference here is that instead of making a connection to another machine, we'll be making a network connection to the same machine that we're running on.  That means a few different things:

1. The loopback connection is denoted by using the `localhost` host name.

2. The loopback connection will communicate to another VSCode-compatible debugger on the local `5678` port.

   This is the value VSCode chose as its default port.  A port is a single use communication channel, so if you're planning on doing anything more complex, like maybe debugging multiple applications side by side, you'll need to select a different port to avoid port-in-use conflicts.

3. We've toggled `justMyCode` to `true` so we're not debugging the standard lib.

4. We've configured `pathMapping` to make `localRoot` and `remoteRoot` point to the same path.  Other remote workflows will have different values in that mapping, but because we're on the same machine and debugging the same project, we simply use use project's root path, stored in the `${workspaceFolder}` variable.

## The `ptvsd` package

The `attach` configuration expects to connect with VSCode-compatible debugger running inside the application.  That means for the attach process to work, we need to activate that software component and have that component start a connection to VSCode after the application has start.

Unfortunately, there's nothing in 3ds Max (and most applications) that will do this out of the box.  To work around this, we'll need to install a 3rd party library, like the `ptvsd` Python package, and activate it at start-up.

The activation is straight forward.  Sometime after the application has loaded, the user needs to execute the following commands:

```python
import ptvsd
ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
ptvsd.wait_for_attach()
```

The `enable_attach` function will enable the port at the same `localhost:5678` address our `attach` configuration is using.  And the `wait_for_attach` function will wait forever, freezing the application in a busy loop, until VSCode completes the connection.  After the connection is made, VSCode is now attached and the application continues on its way.

## Install `ptvsd` into the side-car environment

There are different ways to handle installing the `ptvsd` package.  But because it is available as a standalone Python package on PyPI, we can leverage our existing workflow that we put into place in [Part I].  There, we created a virtual environment to be grafted into the application, which we set-up by using `pip`:

```shell
$ D:\project\.env27\script\activate.bat
(.env27) $ python -m pip install -r D:\project\requirements.txt
(.env27) $ python -m pip install -e D:\project
```

This means that the simplest way to instal ptvsd is to add it to the `requirements.txt` file

```text
ptvsd==4.3.2
```

Note:  Do not add it as a package dependency to your project, be it in setup.py's `install_requires` or some other mechanism.  It is not a dependency to be installed on the user's machine when the user installs your project; it is a development tool that only has value to the development team.  There's more information about the difference in the PyPA's [install_requires vs requirements files] guidelines.

## Call `ptvsd` from the `bootstrap.py` script

We can also leverage the components we created in [Part II] and add the `ptvsd` connection call to our `bootstrap.py`. This will make the connection at startup, but we have to be careful to add it *after* the grafting of the side-car environment, as that's where the Python package lives.

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

.. note::

    This script does not install ptvsd and expects the module to be already installed,
    or installed during the site injection or exec execution step.

"""
import logging
import os


def main():
    """Main entry point for the bootstrap script"""

    debug_port = os.getenv("PROJECT_DEBUG_PORT", "")
    debug_host = os.getenv("PROJECT_DEBUG_HOST", "")
    scripts = os.getenv("PROJECT_SCRIPTS", "").split(";")
    log_level = os.getenv("PROJECT_LOG_LEVEL", logging.DEBUG)

    logging.basicConfig(level=log_level, format="%(message)s")
    logger = logging.getLogger(__name__)
    logger.info("Python Bootstrap script - start -")
    logger.info('Initialized logging to "%s"', log_level)

    if scripts:
        script_paths = [sf for sf in filenames if os.path.exists(sf)]
        if not script_paths:
            logger.warning("No scripts to execute.  Skipping script execution.")

        for script_path in script_paths:
            logger.info("Executing Script: %s", script_path)
            with open(script_path) as f:
                contents = f.read()
            try:
                exec(contents, {"__file__": script_path})
            except Exception as e:
                logger.exception("   ! %s failed to execute", script_path)
    else:
        logger.warning("Could not find variable PROJECT_SCRIPTS does not exist or is empty.  Skipping Python script execution.")

    if debug_host and debug_port:
        try:
            import ptvsd
            logger.info("Waiting for PTVSD debug client to connect on %s:%s", debug_host, debug_port)
            ptvsd.enable_attach(address=(debug_host, int(debug_port)), redirect_output=True)
            ptvsd.wait_for_attach()
        except ImportError:
            logger.exception("Could not import module `ptvsd`.  Is installed?")
    else:
        logger.warning("Environment variable PROJECT_DEBUG_HOST/PROJECT_DEBUG_PORT do not exist or are empty.  Skipping Python remote debugging.")

    logger.info("Python Bootstrap script - stop -")

if __name__ == "__main__":
    main()

```

In this iteration we've made a few changes things:

1. We've added `PROJECT_DEBUG_PORT` and `PROJECT_DEBUG_HOST` environment variables to contain the respective parameters for `ptvsd`.

2. We've add a little of extra error handling in case the `ptvsd` module is not importable.

## Code Complexity

Unfortunately, we've triggered a code complexity warning in the single `main` function.  We'll do that by splitting up the function into `main` and two internal function `_exec` and `_attach`:

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

.. note::

    This script does not install ptvsd and expects the module to be already installed,
    or installed during the site injection or exec execution step.

"""
import logging
import os

def _exec(filenames):
    """Execute a collection of Python files in the current environment

    Args:
        scripts (list): A list of filename.
    """
    logger = logging.getLogger(__name__)

    script_paths = [sf for sf in filenames if os.path.exists(sf)]
    if not script_paths:
        logger.warning("No scripts to execute.  Skipping script execution.")

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

    logger.info("Waiting for PTVSD debug client to connect on %s:%s", host, port)
    ptvsd.enable_attach(address=(host, port), redirect_output=True)
    ptvsd.wait_for_attach()

def main():
    """Main entry point for the bootstrap script"""

    debug_port = os.getenv("PROJECT_DEBUG_PORT", "")
    debug_host = os.getenv("PROJECT_DEBUG_HOST", "")
    scripts = os.getenv("PROJECT_SCRIPTS", "").split(";")
    log_level = os.getenv("PROJECT_LOG_LEVEL", logging.DEBUG)

    logging.basicConfig(level=log_level, format="%(message)s")
    logger = logging.getLogger(__name__)
    logger.info("Python Bootstrap script - start -")
    logger.info('Initialized logging to "%s"', log_level)

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

## Attach to Process (Manually)

With the `ptvsd` installed in the side-car environment and configured to run on startup via `bootstrap.py`, we now have the minimum amount of pieces in place to start a debugging session.

First we update our launch script to include to host and the port:

```batch
@echo off
setlocal
cd %~dp0
set "PROJECT_LOG_LEVEL=DEBUG"
set "PROJECT_SCRIPTS=%CD%\.env27\Scripts\activate_this.py"
set "PROJECT_HOST=locahost"
set "PROJECT_PORT=5678"
3dsmax.exe -u PythonHost bootstrap.py
```

And second, we execute the VSCode's [remote debugging manual steps] to connect the `ptvsd` instance running in the application:

1. Launch the application with `launch.cmd`.

2. Wait for the application to display `Waiting for debug client to connect on localhost:5678`

3. Switch to VSCode.

4. Execute the `Python: Attach` launch configuration from above.

You should see the application resume its start sequence and VSCode should be in [debugger mode].

## Next Step

The updated `bootstrap.py` and `launcher.cmd` scripts completes the third part of the tutorial and we now have a complete workflow (even if it is somewhat clunky) to debug our Python package while it's running inside an embedded Python environment.  In the [Part IV], we'll start the refinement phase and start looking at different way to make this manual process an automatic one.

[install_requires vs requirements files]: https://packaging.python.org/discussions/install-requires-vs-requirements/
[debugger mode]: https://code.visualstudio.com/Docs/editor/debugging
[part iv]: {filename}../2020-12-07-python-vscode-and-max-4/note.md
[remote debugging steps]: https://code.visualstudio.com/docs/python/debugging#_remote-script-debugging-with-ssh
[previous article]: {filename}../2020-12-03-python-vscode-and-max-2/note.md
[part i]: {filename}../2020-12-01-python-vscode-and-max-1/note.md
[part ii]: {filename}../2020-12-03-python-vscode-and-max-2/note.md
