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
spell-checker:ignore NOTSET asctime levelname
-->
Logging is pretty important.  It's the primary way to capture the performance of code after it has left the developer's controlled environment.  This means that the more complex a program becomes, the greater the need for a robust and mature logging system.

Fortunately, Python has a logging service built into its core system libraries that is both powerful and flexible -- so much so that it's slightly intimidating.  This post will introduce the logging system through a collection of basic logging topics.

## Replacing `print`

The most basic way of logging is to write messages to the console using the `print` function.

```python
print('This is an info message')
```

The `print` function writes text to the system's standard output stream.  For small scraps of code this works well because they are small scraps of code.  Scaling this practice up to more complex projects, like applications or system libraries, becomes problematic. In those situations, where a single client is brining in various libraries from multiple developers, all of the `print`s would overwhelm the user with information and turn the system console's into a performance bottleneck.

Library developers could work around this, maybe creating a dev and release mode of their library, but that's adding an extra layer of needless work and responsibility onto each individual library.  Python's logging system has already solved this problem and splits the responsibility between the developer and client.  The developer write the logging messages and the client controls the output.

## Using Logger Objects

The developer-facing part of the logging system is the [logger objects].  These logger objects are aptly named `logger`s and developers request one from the `logging` module.

```python
import logging
logger = logging.getLogger(__name__)
logger.info('This is an info message')
```

There are a few things to note with the snippet:

1. All logging calls must be done through the `logging` library.

    The logging library is a builtin system library and is quite mature, having been with Python standard library from the start.

2. Developers request logging objects from the logging system's `getLogger` function with a name, preferable using the `__name__` value.

    The logger object is created on demand and managed by the logging system.  The name parameter is simply a label to refer to the logger object later on.  The name could be any pieces of text, but using the built-in `__name__` variable is a good habit to use from the start -- especially as you start developing more complex applications.

    The `__name__` variable is available in all files and contains the fully qualified module name.  This means that developers get a working naming scheme for free with the line `logger = logging.getLogger(__name__)` copied and pasted throughout your project.

3. Developers send messages through one of the logger's convenience functions.

    While the logger's functions look like it is sending simple strings, each call makes a [logging record] that contains the text line as an attribute.  The logging system also attaches a severity or logging levels to each record.  The equivalent level of typical `print` messages is the `info` level and each logger object has a convenience function to send messages on that level.

    The [logging record] are the internal objects that represent messages and there are additional tools and utilities to work with them, but that's beyond the scope of this article.

## Initializing with `basicConfig`

Printing messages to the console with `print` works right out of the box.  Sending logging messages to the console, like in the above snippet, does not.

The logging system must be initialized and configured to send logging messages to the console.  This configuration step will be custom for larger projects that require more than one output for messages, but smaller projects can initialize the system in a single line using the `logging.basicConfig` function.

The `basicConfig` function allows the user to configure the most frequently used options.  The snippet from the `example.py` module below initializes the logging system with a opinionated configuration that works for basic usage.

```python
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info('This is an info message')
```

The function takes in multiple parameters, but the bare minimum should include the `format` and the `level` arguments.

The `format` text is the template to apply to all messages and in our case we have a simple one that makes a logging message from three logging message properties:

1. `asctime`: the time the message was created
2. `levelname`: the human readable name of the importance level
3. `message`: the message itself

Running the code example above yields the print message, but also the time and the level name as well:

```console
$ python example.py
2021-02-08 20:02:30,998 : INFO : This is an info message
```

The `level` argument is a filter.  Changing the value from `logging.INFO` to a higher level, like `logging.WARNING` will blocked the info messages from being displayed.  Similarly, going to a lower level, like `logging.DEBUG`, will allow the `info` messages, but also include all `debug` messages.  But again, with the goal of minimally replacing the print statement, this can be set to `logging.INFO`.

## How to Initialize

Initialization should occur only once in an application's lifespan as each initialization destroyers the previous initialization.  For this reason, initialization should not be done in a library but instead by done in the application's `__main__` block.

The official `__main__` [documentation] does a great job explaining what this block is.  But, it's best to use the `__main__` block to initialize the logging system because it is the main entry point of the application and executed before anything else.  For example, update the above `example.py` by adding a `__main__` block:

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
2021-02-08 20:03:01,900 : INFO : This is an info message
```

However, if we `import` the module, the `__main__` block (and the initialization) is ignored and the logging statement is skipped:

<!-- markdownlint-disable MD014 -->
```console
$ python -c "from example import main;main([])"
$
```
<!-- markdownlint-enable MD014 -->

The second example doesn't have any logging messages because the `__name__` value contains the module name `example` instead of the `__main__` value.

## A note about logging's `name` and `__name__`

Remember that using `__name__` in `logger = logging.getLogger(__name__)` is considered a best practice because it leverages the python module name stored in that variable and simplifies the way to acquire the logger through the code.

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
2021-02-08 20:05:02,700 : __main__ - INFO : This is an info message
```

However, executing the code as a module (after we manually initialize the logging system), displays the name of the module `example` in the name value:

```console
$ python
>>> import logging
>>> logging.basicConfig(format='%(asctime)s : %(name)s %(levelname)s : %(message)s', level=logging.INFO)
>>> from example import main
>>> main([])
2021-02-08 20:07:03,600 : example - INFO : This is an info message
0
```

This is important to know as the client could very well use the `name` field to filter in or out logging messages from a particular module.

## Using different logging levels

The logging system attaches a numerical severity level to each logging message.  These levels are actually customizable, but in practically all cases its best to just use the default levels define in the `logging` module: `debug`, `info`, `warning`, `error`, and `critical`.

The logger object implements a convenience logging function for each logging level, wrapping around the actual `log` function.  The `log` function is public to use, and can be used for special handling or for custom levels:

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

The uses all convenience functions and uses custom levels `5` and `100`. Execute the above module yields the following results:

```console
$ python example.py
2021-02-08 20:19:58,867 : __main__ INFO : This is an info message
2021-02-08 20:19:58,867 : __main__ WARNING : This is a warning message
2021-02-08 20:19:58,867 : __main__ ERROR : This is an error message
2021-02-08 20:19:58,867 : __main__ CRITICAL : This is a critical message
2021-02-08 20:19:58,867 : __main__ Level 100 : This is a custom message at level 100
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
2021-02-08 20:36:05,829 : __main__ ERROR : This is an error message
2021-02-08 20:36:05,829 : __main__ CRITICAL : This is an critical message
2021-02-08 20:36:05,829 : __main__ Level 100 : This is an custom message at level 100
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
2021-02-08 20:37:34,355 : __main__ Level 5 : This is an custom message at level 5
2021-02-08 20:37:34,355 : __main__ DEBUG : This is an debug message
2021-02-08 20:37:34,355 : __main__ INFO : This is an info message
2021-02-08 20:37:34,355 : __main__ WARNING : This is an warning message
2021-02-08 20:37:34,355 : __main__ ERROR : This is an error message
2021-02-08 20:37:34,355 : __main__ CRITICAL : This is an critical message
2021-02-08 20:37:34,355 : __main__ Level 100 : This is an custom message at level 100
```

[documentation]: https://docs.python.org/3/library/__main__.html
[logging record]: https://docs.python.org/3/library/logging.html#logrecord-attributes
[logger objects]: https://docs.python.org/3/library/logging.html#logger-objects
