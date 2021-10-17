---
title: Set up VSCode to Debug Python in 3ds Max - II
date: 2020-12-03T20:23:45.12
category: dev setup
tags: Python,3ds Max,VSCode
slug: python-vscode-max-2
authors: db
summary: Part II&#58; The bootstrap script
header_cover: /images/article-bg.png
---

In the previous article, we prepared the Python development environment by first creating a Python virtual environment and then installing our Python project as an editable package.  In this article, we'll explore how we're going to graft this onto the external application.

## Python Activator

The virtual environment that we've created is linked to the Python environment that created it.  In order to graft that environment to the application's Python installation, we're going to play around with that relationship by activating that virtual environment not in the original Python installation, but in the application's Python environment.

We can do that in a non-destructible way via a bootstrap script that is launched at application start-up.  We're really emphasizing the non-destructive nature of this because we don't want to make any permanent changes to the application and everything should be isolated to the current executing session.  The goal here is that the user should be able to launch the application without the start-up script and have the new instance co-exist without any side effects.

Fortunately, the `virtualenv`'s Python activator option has done most of the work for us.  The Python activator produced an [activate_this.py] Python script and the the only thing that's really missing is for a way to execute within the application.

You can see this script online at GitHub.  The snapshot used for this article is available below:

```python
# -*- coding: utf-8 -*-
"""Activate virtualenv for current interpreter:
Use exec(open(this_file).read(), {'__file__': this_file}).
This can be used when you must use an existing Python interpreter, not the virtualenv bin/python.
"""
import os
import site
import sys

try:
    abs_file = os.path.abspath(__file__)
except NameError:
    raise AssertionError("You must use exec(open(this_file).read(), {'__file__': this_file}))")

bin_dir = os.path.dirname(abs_file)
base = bin_dir[: -len("__BIN_NAME__") - 1]  # strip away the bin part from the __file__, plus the path separator

# prepend bin to PATH (this file is inside the bin directory)
os.environ["PATH"] = os.pathsep.join([bin_dir] + os.environ.get("PATH", "").split(os.pathsep))
os.environ["VIRTUAL_ENV"] = base  # virtual env is right above bin directory

# add the virtual environments libraries to the host python import mechanism
prev_length = len(sys.path)
for lib in "__LIB_FOLDERS__".split(os.pathsep):
    path = os.path.realpath(os.path.join(bin_dir, lib))
    site.addsitedir(path.decode("utf-8") if "__DECODE_PATH__" else path)
sys.path[:] = sys.path[prev_length:] + sys.path[0:prev_length]

sys.real_prefix = sys.prefix
sys.prefix = base
```

There are a few things that this script is doing that's important:

1. This is a template file so the the strings `__LIB_FOLDERS__`, `__BIN_NAME__`, etc. are placeholders and are replaced with resolved values during the creation process.

2. The script is updating the `PATH` environment variable.  This is important for binary components, usually DLL files on Windows.

3. The script is injecting additional site package locations with the [addsitedir].  This is important, as it not only adds the respective `site-packages` path to the [sys.path] but also processes the various `.pth` files that may be added by -- but not limited to -- editable package installation.  More information about this is available on the [site] module in the Python standard lib.

## The `bootstrap.py` Bootstrap script

The `virtualenv` module's `activate_this.py` provides the core functionality that we need to graft the environment onto our application's Python environment.  The script even gives us instruction on how to execute it:

```python
script_path = r"D:\project\.env27\Scripts\activate_this.py"
exec(open(script_path).read(), {"__file__": script_path})
```

The problem is that we need to need to make the script portable.  If we put that code into a startup file, named `bootstrap.py`, then we can use the `__file__` attribute to resolve the current path and resolve the location of the `activate_this.py`.

```python
import os
root_path = os.path.dirname(__file__)
script_path = os.path.join(root_path, ".env27", "Scripts", "activate_this.py")
exec(open(script_path).read(), {"__file__": script_path})
```

That's better, but how do we differentiate between potentially different Python environment?

## Bootstrap Environment Variables

The `bootstrap.py`'s `script_path` variable is problematic for two reasons:

1. The hardcoded path is not portable.
2. The hardcoded path is not Python agnostic.

We can punt that responsibility down the line to the user and have him pass it in as a parameter.  However, we're limited by the application in how we can communicate with the script.  One solution that seems to work around that limitation is environment variables:

```python
import os
script_path =  os.getenv("ACTIVATE_THIS_SCRIPT", "")
exec(open(script_path).read(), {"__file__": script_path})
```

Environment variables local to a process are a simple way to pass arguments down through multiple layers of code.  This is most evident when your application will give you a way to execute a script from the command line but not a way to pass in script arguments.

The alternative is to either automatically generate the script or a parameter file before launch, which is not necessarily wrong but won't work well for our particular task.  In our case it will be easier to set up the script to get it's data from environment variables.

## Bootstrap Safety Checks

We can decorate our `bootstrap.py` with a bit more flare.

1. We change the `ACTIVATE_THIS_SCRIPT` into a `PROJECT_SCRIPTS` environment variable that's a collection of individual scripts separated by semi-colon `;`.

2. We add a bit more error handling to make the script as user-friendly as possible.

3. Since we're executing a startup script via `exec`, we're also trapping all exceptions with the base  `Exception`.  This is usually frowned upon as that patten tends to hide exceptions, but it's applicable in our case as we're sharing the exception to the logging console.

4. We wrap the entire script in a [main scope] out of good habit.

```python
"""
Standalone set-up script

The script will inject various sites and execute startup files in
order to set-up the Python environment for development.

This script expects the following environment variables:

- `PROJECT_SCRIPTS` A semi-colon separated list of files to execute with
  `exec`.

"""
import glob
import os

def main():
    # Execute a list of startup scripts
    scripts = os.getenv("PROJECT_SCRIPTS", "").split(";")
    script_paths = [sf for sf in scripts if os.path.exists(sf)]
    if not script_paths:
        print("Environment variable PROJECT_SCRIPTS does not exist or is empty.  Skipping script execution.")
    for script_path in script_paths:
        print("Executing Script: %s" % script_path)
        with open(script_path) as f:
            contents = f.read()
        try:
            exec(contents, {"__file__": script_path})
        except Exception:
            print("   ! %s failed to execute" % script_path)


if __name__ == "__main__":
    main()
```

## `bootstrap.py` + Logging

We take our basic premise one step further and replace the `prints` with [logging] statements.  This step is optional, but recommended as your Python tool should already be set-up to use logging instead of `print` messages.

As a convenience we use the logging module's basic set-up function [logging.basicConfig] but if this is easily extended to something more advanced with the [logging.config.dictConfig] configuration function.  And again, any parameter should be passed in via environment variables:

```python
"""
Standalone set-up script

The script will inject various sites and execute startup files in
order to set-up the Python environment for development.

This script expects the following environment variables:

- `PROJECT_SCRIPTS` A semi-colon separated list of files to execute with
  `exec`.

- `PROJECT_LOG_LEVEL` A semi-colon separated list of files to execute with
  `exec`.

.. note::

    This script does not install ptvsd and expects the module to be already installed, or installed during the site injection or exec execution step.

"""
import glob
import logging
import os
import site

def main():
    # Configure the logging for the application
    log_level = os.getenv("PROJECT_LOG_LEVEL", logging.DEBUG)
    logging.basicConfig(level=log_level, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Python Bootstrap script - start -")
    logger.info('Initialized logging to "%s"', log_level)

    # Execute a list of startup scripts
    scripts = os.getenv("PROJECT_SCRIPTS", "").split(";")
    script_paths = [sf for sf in scripts if os.path.exists(sf)]
    if not script_paths:
        logger.warning("Environment variable PROJECT_SCRIPTS does not exist or is empty.  Skipping script execution.")
    for script_path in script_paths:
        logger.info("Executing Script: %s", script_path)
        with open(script_path) as f:
            contents = f.read()
        try:
            exec(contents, {"__file__": script_path})
        except Exception:
            logger.exception("   ! %s failed to execute", script_path)

    logger.info("Python Bootstrap script - stop -")

if __name__ == "__main__":
    main()

```

## Execute the Bootstrap

With a virtual environment created and a basic bootstrap script in place, we're now ready to connect another pieces and launch our application with the side-car environment.  To ensure that we do that the most portable way possible, we look to the application's start-up process and see what methods we have to execute a script an startup.

Hopefully there is a command line or environment variable option available, but this is application specific.  From the [3ds Max help], we can execute any Python file using the `-u PythonHost` command:

```batch
3dsmax.exe -u PythonHost file.py
```

With that information, we can create a very rudimentary `launcher.cmd` script to launch 3ds Max with our debug environment variables and the command line configured to launch with our bootstrap script:

```batch
@echo off
setlocal
cd %~dp0
set "PROJECT_LOG_LEVEL=DEBUG"
set "PROJECT_SCRIPTS=%CD%\.env27\Scripts\activate_this.py"
3dsmax.exe -u PythonHost bootstrap.py
```

Running this from the command line should launch 3ds Max and produce the following output in the 3ds Max Listener:

```text
Welcome to MAXScript.


Python Bootstrap script - start -
Initialized logging to "DEBUG"
Executing Script: D:\projects\.env27\Scripts\activate_this.py
Python Bootstrap script - stop -
```

## Next Step

The completed `bootstrap.py` completes the second part of the tutorial.  That file executes all of the necessary component needed to launch the application with a grafted side-car environment.  The next step, [Part III] will look into how exactly we use VSCode to launch the application with the `bootstrap.py` script.

[activate_this.py]: https://github.com/pypa/virtualenv/blob/main/src/virtualenv/activation/python/activate_this.py
[main scope]: https://docs.python.org/3/library/__main__.html
[addsitedir]: https://docs.python.org/3/library/site.html#site.addsitedir
[site]: https://docs.python.org/3/library/site.html
[sys.path]: https://docs.python.org/3/library/sys.html#sys.path
[logging.basicConfig]: https://docs.python.org/3/library/logging.html#logging.basicConfig
[logging]: https://docs.python.org/3/library/logging.html
[logging.config.dictConfig]: https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig
[install_requires vs requirements files]:https://packaging.python.org/discussions/install-requires-vs-requirements/
[3ds max help]: https://knowledge.autodesk.com/support/3ds-max/getting-started/caas/CloudHelp/cloudhelp/2021/ENU/3DSMax-Basics/files/GUID-BCB04DEC-7967-4091-B980-638CFDFE47EC-htm.html
