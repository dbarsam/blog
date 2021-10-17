---
title: Set up VSCode to Debug Python in 3ds Max - I
date: 2020-12-01T19:14:45.12
category: dev setup
tags: Python,3ds Max,VSCode
slug: python-vscode-max-1
authors: db
summary: Part I&#58; Python Side Car Environments
header_cover: /images/article-bg.png
---

In the previous article, we layed out the overall structure of the workflow.  In this article, we'll take a deep dive into the conventional Python part of that infrastructure and examine how to create a *side-car* environment for the external application.

## 'Side Car' Environments

While Python-enabled applications usually have some sort of Python scripting support, Python developers looking to deploy their scripts as Python packages -- or create Python scripts that use 3rd party Python packages -- should consider setting up an external Python environment as a package host.

This external Python environment will be completely separate from the application but later on we'll connect them together by by grafting one Python environment on top of the other.

It's important to note that this separation is crucial.  Our goal here is to ensure that the local development environment (packages, scripts, settings, etc.) are kept isolated from the application's global environment.  So, while we want to use Python's native packaging features, we need to do so in a way that will not modify the global installation of the application.

## Keep'em separated

There are some benefits to enforcing this barrier.  This separation ensures that the developer has the freedom to reset or even switch projects without having to selectively rollback global changes made to the application.  We can treat the side car environment as a personal sandbox and mess it up how ever we want; if we make a mistake, we can we can always reset by decoupling the environment from the application and destroying it. The alterative -- especially for those applications that don't have the most modular Python installation -- is to completely reinstall the application.

Python developers should already recognize this pattern as the concept of a *virtual environment*.  The slight difference here for this article is that our side-car environment is created by external Python installation and grafted onto another that does not natively support virtual environments.

## The `virtualenv` module

There are many tools that implement Python virtual environments, but the usual, and somewhat mature choice is `virtualenv` module.  Python's `virtualenv` module is a tool popular enough to warrant its own tutorials so it won't be covered here.  A good resource to keep around is the [official help], but the the important thing to note is that the `virtualenv` module works by spawning a new environment based on its host Python installation.   This brings up a few points:

1. Because the `virtualenv` module create virtual environments from a hosting Python environment, you must first install a _system_ Python environment to host `virtualenv`.  This installation is a permanent Python solutions and we only need it to create the temporary side car environments provided by `virtualenv`.

2. Because the `virtualenv` module can only create virtual environments that matches its hosting Python environment, that _system_ Python should be the same version as the the application's Python installation -- or at least match it as close as possible.  This may be challenging if your application still uses Python 2 environments as that line has been discontinued.

3. The _system_ Python installation is usually pre-installed on Linux systems but not on Windows.  On Windows, this achieved simply by installing a Python environment from <https://www.python.org> and then installing the `virtualenv` module.  It's possible to use alternative installations methods (like [Chocolatey]) or even alternative distribution (like [Conda]), but that won't be covered here.

Some vendors have listened to feedback (and learning from their past handling of Python 2) so there is a chance of that the application could already provide all of the necessary support to create user virtual environments.  If that's the case for your specific application, then that makes this section joyfully obsolete.

However, if the application does not provide `virtualenv` support directly out of the box, then we should continue to use the _system_ Python approach.  Even if the application's Python install is accessible, installing `virtualenv` into the application's Python environment would still violate the separation policy to not touching the global installation.

## `venv` vs. `virtualenv`

As a side note, it's probably best to explain the difference between `venv` and `virtualenv`.  The `virtualenv` module was not always (and maybe still isn't to some people) the tool of choice for virtual environments. Historically, Python 2 did not contain any virtual environment tool and it wasn't until Python 3.3 that a [venv] module became part of the standard library.

During that time, the existing `virtualenv` was a third party module that competed with other 3rd party modules to provide the virtual environment functionality.  However, `virtualenv` went through a re-write in 2019 and released a second iteration in 2020 that was built upon the same base as `venv`.  From the [official help]:

> `virtualenv` is a tool to create isolated Python environments. Since Python `3.3`, a subset of it has been integrated into the standard library under the venv module. The [venv module] does not offer all features of this library, to name just a few more prominent:
>
> - is slower (by not having the app-data seed method),
> - is not as extendable,
> - cannot create virtual environments for arbitrarily installed python versions (and automatically discover these),
> - is not upgrade-able via pip,
> - does not have as rich programmatic API (describe virtual environments without creating them).

But even then it wasn't clear which tool to use, as the `venv` help notes:

> _Deprecated since version 3.6_: `pyvenv` was the recommended tool for creating virtual environments for Python 3.3 and 3.4, and is [deprecated in Python 3.6].
>
> _Changed in version 3.5_: The use of `venv` is now recommended for creating virtual environments.

So this article is using the shared features of both the `venv`/`virtualenv` modules but we've selected `virtualenv` for its finer grain of control over the virtual environment process.

## Creating Virtual Environments

For this tutorial, we're assuming that you are able to execute `virtualenv` from a vanilla Python environment that matches the Python environment in your applications.  Creating an environment from the command line should be as simple as:

```batch
python.exe -m virtualenv env27
```

But because we're on creating this as a side car environment on Windows, we can fine-tune the installation to install it within our project folder:

```batch
python.exe -m virtualenv D:\project\.env27 --no-download --activators batch,python
```

We're doing a few things here:

1. Creating the environment inside the project folder `D:\project` just to keep everything local to the project.

2. Explicitly using the `--no-download` option (even if it enabled by default) to speed up the creation of the environment by not downloading the seed packages of `pip`, `setuptools` and `wheel` packages from the internet.

3. Explicitly creating the `batch` and `python` activators instead of the full suite of activators (introduced in version `20`).  For more information about activators, check out the [activator section] and the [command line arguments] from the [official help]

The batch activator allows us to activate the environment from the `cmd` shell which will be the shell of our choice.  If you have a different shell preference, like `powershell`, then select that instead of `batch`.  The shell activator doesn't really matter as we're more interested in the `python` activator.  That's the mechanism that will make this virtual environment a 3ds max side car environment.

## Editable installs

After the virtual environment is created, we now make the first connection in our development puzzle.  Fortunately, this is fairly straight forward and we'll use the standard module `pip` [editable install] to install the Python package in the side-car environment:

```batch
$ D:\project\.env27\script\activate.bat
(.env27) $ python -m pip install -r D:\project\requirements.txt
(.env27) $ python -m pip install -e D:\project
```

We're doing three things here:

1. We activate the virtual environment before executing the pip install command.  Otherwise you might be installing the package into the global installation.  The `virtualenv` usually modifies the prompt with the `virtualenv`'s name or path on disk.

2. We then instal our project's `requirement.txt` file.  If your project has any 3rd party dependencies, then you should store them in the `requirements.txt` file.  It's important to not rely on the project's setup.py's `install_requires` to do this for us as that serves a slightly different purpose.  There's more information about the difference in the PyPA's [install_requires vs requirements files] guidelines.

3. We then install our own project as an editable install.

This step relies solely on project structure to succeed, so this should still work even if your project imports the application's Python API package (such as `pymxs` for 3ds Max).  We're not executing any code here; instead we're simply setting up the various hooks we need to execute the package in the virtual environment in an editable way.

Behind the scenes, the editable install only modifies the virtual environment by creating a `pth` file.  These `pth` files contain the paths to locations outside of the environment and are processed by the [site] module during Python initialization.  There's more functionality here, as described by the [site] module's help page, but for the purpose of the editable installs this is what we care about.

## Next Steps

This part of the infrastructure has only focused on the Python parts of it.  With the virtual environment complete and our project properly installed for development, it's time to move onto [Part II].  There we'll look into how we'll graft the virtual environment onto the application using the _bootstrap_ script.

[chocolatey]: https://chocolatey.org/
[conda]: https://anaconda.org
[activator section]: https://virtualenv.pypa.io/en/latest/user_guide.html#activators
[official help]: https://virtualenv.pypa.io/en/latest/
[command line arguments]: https://virtualenv.pypa.io/en/latest/cli_interface.html#section-activators
[deprecated in Python 3.6]: https://docs.python.org/dev/whatsnew/3.6.html#deprecated-features
[venv]: https://docs.python.org/3/library/venv.html
[venv module]: https://docs.python.org/3/library/venv.html
[editable install]: https://pip.pypa.io/en/stable/cli/pip_install/#local-project-installs
[part ii]: {filename}2020-12-03-python-vscode-and-max-2.md
