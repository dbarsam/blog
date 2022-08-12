---
title: Logging Exceptions in Python
date: 2021-02-09 19:13
tags: python, logging
slug: python-logging-exceptions
authors: db
summary: How to use the logging system to capture exceptions.
header_cover: /images/home-bg.png
status: published
category: application development
type: article
---
<!--
spell-checker:ignore
-->
The various functions of `logger.debug`, `logger.info`, `logger.warning`, `logger.error` and `logger.critical` were introduced in the [quick-start article about logging].  The `logger.exception` function was not covered in that article and it has a very specific use.

## Logging during Exceptions

The Like the other conveinience functions, the `logger.exception` function is a wrapper around the base `logger.log` function.  The function, however, does two specific things:

1. It logs to the `error` level.
2. It includes the stack trace of the current exception from [sys.exc_info()].

These are useful when logging messages during an exception.  For example, consider this example script:

```python
import sys
import logging

def function():
    x = 1/ 0

def main(args=[]):
    logger = logging.getLogger(__name__)
    try:
        function()
    except Exception:
        logger.exception("Fatal error when calling function.")
        return 1
    return 0

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(name)s %(levelname)s : %(message)s', level=logging.NOTSET)
    sys.exit(main(sys.argv))
```

The script uses a catch-all pattern by using the base `Exception` object in the tr/except block.  This is normally discouraged and is only used here for sake of simplicity.

Executing the example intercepts the divide by 0 and prints out the messasge along with the respective call stack and -- it's important to note it here -- resumes the execution, returning 1 instead of 0.

Running this script yeilds the following output:

```console
$ python example.py
2021-02-09 21:34:23,560 : __main__ ERROR : Fatal error when calling function.
Traceback (most recent call last):
  File "example.py", line 10, in main
    function()
  File "example.py", line 5, in function
    x = 1/ 0
ZeroDivisionError: division by zero
```

The accompanying callstack appears right under the logging message, starting with `Traceback` and ending with the exception name, `ZeroDivisionError`.

## Logging Exceptions at other Levels

Underneath the hood, the `exception` function assigns the message to the `error` level and sets the `exc_info` parameter to `True`.  So with the parameter, we can accomplish the same thing by being more explict with the `logger.error` function:

```python
try:
    function()
except Exception:
    logger.error("Fatal error when calling function.", exc_info=True)
    return 1
```

Running the updated script yields the same output:

```console
$ python example.py
2021-02-09 21:42:23,560 : __main__ ERROR : Fatal error when calling function.
Traceback (most recent call last):
  File "example.py", line 10, in main
    function()
  File "example.py", line 5, in function
    x = 1/ 0
ZeroDivisionError: division by zero
```

The `exc_info` is a key word argument of the base `log` function so using it is not restricted to just the `error` function. The parameter is available to all convenience functions and can be used to log the message and callstack to any other level, like `info`, for example:

```python
try:
    function()
except Exception:
    logger.info("Handled exception when calling function.", exc_info=True)
```

Executing the script changes nothing -- except that the message is now emitted at the `info` level instead of the more severe `error` level.

```console
$ python example.py
2021-02-09 21:59:40,506 : __main__ INFO : Handled exception when calling function.
Traceback (most recent call last):
  File "example.py", line 10, in main
    function()
  File "example.py", line 5, in function
    x = 1/ 0
ZeroDivisionError: division by zero
```

Using this technique really should be done in special cases.  It's still best to use the `exception` method to log exception classtacks on the `error` level.  Callstack are rather synonymous with applications crashes so dumping a callstack at a client-visible level, like `info` or `warning` will end up confusing the user.  In the case of logging the handling of expected exceptions, simply use the regular conveience functions and skip the callstack.

[sys.exc_info()]: https://docs.python.org/3/library/sys.html#sys.exc_info
[quick-start article about logging]: {filename}../2021-02-08-python-logging-quick-start/python-logging-quick-start.md
