---
title: Qt DLLs in the Windows PATH
date: 2020-10-29T11:27:02.031Z
category: Troubleshooting
tags: Python,Qt,DLL
slug: qt-dll-mismatch
authors: db
summary: How to recognize a particular PySide's DLL load failure error in Windows.
header_cover: /images/article-bg.png
---

Every couple of months we'll get a report of some Python tool magically failing with a mysterious -- and unhelpful -- `DLL load failed` error message.  The error is unfortunately too generic to be helpful, but if the Python tool is a PySide application, then there might be a workaround to solve this problem.

## Wrong DLLs

It's easy to validate the problem right away with a simple import from the prompt:

```python
>>> from PySide2 import QtXml
Traceback (most recent call last):
  File "<console>", line 1, in <module>
ImportError: DLL load failed: The specified module could not be found.
```

The `QtXml` is just an example module from the `PySide2` package, but the above code should work out of the box.  The fact that PySide is failing to load a Qt DLL hints to a common problem with how applications are packaging their Qt DLLs.

Qt is a 3rd party UI framework and those DLLs are not unique to the application.  If another Qt-using application is installed on the same machine, then what most likely is happening with that failure is that your Qt application is finding the PySide package correctly, but PySide is somehow loading the Qt dlls from the other application instead of its own copies.

## Hack the Windows DLL Search Order

Instead of going into a deep dive about the [Windows DLL Search Order], the easiest workaround is to hack it so that your application's Qt DLL are given the highest priority. One way to do that is to adding the application's folder for Qt DLLs to the front of the `PATH` environment variable  You can do this in a permanent or temporary way with a script `launcher.cmd`:

```cmd
setlocal
set "PATH=C:\Program Files\My Application\bin;%PATH%"
C:\Program Files\My Application\bin\application.exe
```

Given that we're working around a conflicts between two (or more) applications, we don't have access to fix it properly.  Instead, it's probably easier to solve this with a launcher script and keep the change local to application.

[Windows DLL Search Order]: https://docs.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order
