---
title: Quick Start to Python Logging
date: 2021-02-08 19:13
tags: python, logging
slug: python-logging-quick-start
authors: db
summary: The bare minimum needed to get started with thePython logging system.
header_cover: /images/home-bg.png
status: published
category: application development
type: article
---
<!--
spell-checker:ignore
-->

Logging is pretty important.  It exists to capture real time data in a way that developers can accurately see how their code is running in the real world, outside of their dev environment.  This means that the more complex a program becomes, the greater the need for a robust and mature logging system.

Fortunately, Python has a logging service built into its core system libraries that is both so powerful and flexible that it's slightly intimidating.  This post will introduce the logging system and introduce a series of articles highlighting various feature and recipes using the logging system.

## Replacing `print`

The basic way of logging is to write messages to the console using the `print` function.

```python
print('This is an info message')
```

The `print` function writes text to the system's standard output stream and for small scraps of code the works well because they are small scraps of code.  However, if we were to continue using print in complex projects, like applications or system libraries -- where a single client is brining in various libraries from multiple developers -- all of the `print`s would overwhelm the user and the system console.

Library developers could work around this, maybe creating a dev and release mode of their libraries, but that's an adding extra extra layer of needless work and responsibility onto each library.  Fortunately, Python's logging system has a solution for this case and it's quite trivial.  With the logging system, the developer only needs to write his logging messages, deferring control of the output to the client.

## Using Logger Objects

The logging system works by creating logging objects and sending messages through them.  The logging object is aptly named the `logger`:

```python
import logging
logger = logging.getLogger(__name__)
logger.info('This is an info message')
```

There are a few things to note on with the snippet:

1. All logging calls must be done through the `logging` library.

    The logging library is a builtin system library and is quite mature, having been with Python standard library from almost the start.

2. Get a logging object by requesting one from the logging system with a name, preferable using the `__name__` value.

    The logger object is created on demand and managed by the logging system.  The name used is simply a label to refer to the logger object later on.  The name could be any pieces of text, but using the built-in `__name__` variable is a good habit to use from the start -- especially as you start developing more complex applications.

    The `__name__` variable is available in all files and contains the fully qualified module name.  This means that developers get a working naming scheme for free with the line `logger = logging.getLogger(__name__)` copied and pasted throughout your project.

3. Send messages through one of the logger's convenience functions.

    The logging system attaches severity or importance levels to each message.  The equivalent level of typical `print` messages is the `info` level and each logging object has a convenience function to send messages on that level.  There are other levels, but that's a level above and beyond a simple print replacement.

## Initializing with `basicConfig`

Printing messages with `print` works right out of the box.  Sending logging messages, like with the above snippet, does not.

The logging system must be initialized and configured to send logging messages to the system console.  This configuration step is important for larger projects that require more than one output for messages, but smaller ones can initialize the system in a single line using the  `basicConfig` function from the `logging` module.

The `basicConfig` function allows the user to configure the most frequently used options.  The `example.py` module below initializes the logging system with a opinionated configuration that works for basic usage.

```python
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info('This is an info message')
```

The function takes in multiple parameters, but the bare minimum should be the `format` and the `level` arguments.

The `format` text is the template to apply to all messages and in our case we have a simple one that makes a logging message from three logging message properties:

1. `asctime`: the time the message was created
2. `levelname`: the human readable name of the importance level
3. `message`: the message itself

Running the code example above yields the print message, but also the time and the level name as well:

```console
$ python example.py
2021-02-08 08:27:30,998 : INFO : This is an info message
```

The `level` argument is a filter.  Changing the value from `logging.INFO` to a higher level, like `logging.WARNING` will blocked the info messages from being displayed.  Similarly, going to a lower level, like `logging.DEBUG`, will allow the `info` messages, but also include all `debug` messages.  But again, with the goal of minimally replacing the print statement, this can be set to `logging.INFO`.

## How to Initialize

Initialization should occur only once in an application's lifespan as each initialization destroyers the previous initialization.  For this reason, initialization should not be done in a library but instead by done in the application's `__main__` block.

The official `__main__` [documentation] does a great job explaining what this block is.  But, for the purposed of logging, use the `__main__` block to initialize the logging system because it is the main entry point of the application and executed before anything else.  For example, add the `__main__` block to the `example.py`:

```python
import sys
import logging

def main(args=[]):
    logger = logging.getLogger(__name__)
    logger.info('This is an info message')
    return 0

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    sys.exit(main(sys.argv))
```

If we execute `example.py` directly, we see the logging statement.

```console
$ python example.py
2021-02-08 09:03:01,900 : INFO : This is an info message
```

However, if we `import` the module, the `__main__` block (and the initialization) is ignored and the logging statement is skipped:

```console
$ python -c "from example import main;main([])"
```

The second example doesn't have any logging messages because the `__name__` value contains the module name `example` instead of the `__main__` value.

## A note about logging's `name` and `__name__`

Remember that using `__name__` in `logger = logging.getLogger(__name__)` is considered a best practice because it leverages the python module value stored in that variable and simplifies the way to acquire the logger through the code.

However, when using `__name__` in the `__main__` block, the value of `__name__` changes to `__main__`.  If we include the `%(name)s` field in our initialization we can see this in practice.

```python
import sys
import logging

def main(args=[]):
    logger = logging.getLogger(__name__)
    logger.info('This is an info message')
    return 0

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(name)s %(levelname)s : %(message)s', level=logging.INFO)
    sys.exit(main(sys.argv))
```

Executing the file from the command line includes the `__main__` in the logging message.

```console
$ python example.py
2021-02-08 09:05:02,700 : __main__ - INFO : This is an info message
```

However, executing the code as a module (after we manually initialize the logging system), displays the name of the module `example` in the name value:

```console
$ python
>>> import logging
>>> logging.basicConfig(format='%(asctime)s : %(name)s %(levelname)s : %(message)s', level=logging.INFO)
>>> from example import main
>>> main([])
2021-02-08 09:07:03,600 : example - INFO : This is an info message
0
```

This is important to know as the client could very well use the `name` field to filter in or out logging messages from a particular module.

## Using Logging Levels

The logging system attaches a numerical severity level to each logging message.  These levels are actually customizable, but in practicaly all cases its best to use the default levels define in the `logging` module: `debug`, `info`, `warning`, `error`, and `critical`.

The logger object implements a convenience function for each logging level, wrapping around the actual `log` function.  The `log` function is public to use, and can be used for special handling or for custom levels:

```python
import sys
import logging

def main(args=[]):
    logger = logging.getLogger(__name__)
    logger.log(5, 'This is a custom message at level 5')
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
    logger.log(100, 'This is a custom message at level 100')
    return 0

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(name)s %(levelname)s : %(message)s', level=logging.INFO)
    sys.exit(main(sys.argv))
```

The uses all conveneince functions and uses custom levels `5` and `100`. Execute the above module yields the following results:

```console
$ python example.py
2021-02-08 10:19:58,867 : __main__ INFO : This is an info message
2021-02-08 10:19:58,867 : __main__ WARNING : This is a warning message
2021-02-08 10:19:58,867 : __main__ ERROR : This is an error message
2021-02-08 10:19:58,867 : __main__ CRITICAL : This is a critical message
2021-02-08 10:19:58,867 : __main__ Level 100 : This is a custom message at level 100
```

All of the logging messages appear -- except for the `5` and `debug` messages.  This is because we set the global level parameter to `logging.INFO` in our `basicConfig` call.  That `level` parameter configures the system to filter out all messages with a severity level less than given level.  Changing the value to `logging.ERROR` will filter out `5`, `debug`  `warning`, and `info` messages:

```python
import sys
import logging

def main(args=[]):
    ....
    return 0

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(name)s %(levelname)s : %(message)s', level=logging.ERROR)
    sys.exit(main(sys.argv))
```

Executing the above module yields the following results:

```console
$ python example.py
2021-02-08 10:36:05,829 : __main__ ERROR : This is an error message
2021-02-08 10:36:05,829 : __main__ CRITICAL : This is an critical message
2021-02-08 10:36:05,829 : __main__ Level 100 : This is an custom message at level 100
```

And likewise, setting the value to `logging.NOTSET` is the equivalent of setting the filter to `0` and letting all messages through:

```python
import sys
import logging

def main(args=[]):
    ....
    return 0

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(name)s %(levelname)s : %(message)s', level=logging.NOTSET)
    sys.exit(main(sys.argv))
```

```console
$ python example.py
2021-02-08 10:37:34,355 : __main__ Level 5 : This is an custom message at level 5
2021-02-08 10:37:34,355 : __main__ DEBUG : This is an debug message
2021-02-08 10:37:34,355 : __main__ INFO : This is an info message
2021-02-08 10:37:34,355 : __main__ WARNING : This is an warning message
2021-02-08 10:37:34,355 : __main__ ERROR : This is an error message
2021-02-08 10:37:34,355 : __main__ CRITICAL : This is an critical message
2021-02-08 10:37:34,355 : __main__ Level 100 : This is an custom message at level 100
```

[documentation]: https://docs.python.org/3/library/__main__.html
