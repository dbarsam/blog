---
title: Headless Qt?
date: 2020-11-06T10:14:45.031Z
category:
tags: Python,Qt,Docker,GUI
slug: headless-qt
authors: db
summary: Can you configure Qt to work in systems with no UI?
header_cover: /images/article-bg.png
---

This isn't a real article.  Instead, it's more of an annotated bookmark of this [post], which was used in some research on how to configure Qt applications to run in Docker Windows containers -- and that Docker task is part of another, work-in-progress project that may not ever be completed. So, there are no solutions here.  Sorry.

The [post], archived here, says this:

> Since the launcher batch no longer requests "-style plastique" QT wants to apply the native style of the desktop environment. This fails on a headless system (or where the current user has no graphical shell to connect to) with the message "Gtk-WARNING **: cannot open display: ". Fortunately, QT provides a workaround in addition to the new "platform=offscreen" flag.
>
> In the tools that set *-no-gui*, beforehand export these variables into the environment
>
> ```console
> export QT_STYLE_OVERRIDE=""
> export QT_QPA_PLATFORM=offscreen
> export DISPLAY=""
> ```
>
> PS: QT-offscreen will not find fonts; unfortunately the workaround only allows for a single directory to search them (I need helvetica):
>
> ```console
> export QT_QPA_FONTDIR="/usr/local/share/fonts/type1"
> ```
>
> Maybe that should get reported upstream, so that like LD_LIBRARY_PATH several directories could be specified.

The post has some concepts that require some commentary, done here via unorganized bullet points:

* The solution should be as simple as setting the `QT_QPA_PLATFORM=offscreen` variable setting. However, it's probably wishful thinking that Qt would make it that easy to disable the UI part of their UI framework.

* This post is for Linux, in case it's not obvious.  Windows does not support the `export` command nor the `DISPLAY` environment variable:

    * The `export` command does has an equivalent `set` command.

    * The `DISPLAY` variable is actually part of the `X server` window system, which introduces an entirely different problem if you want this to work on Windows.  This is a awkward problem:  You have to either find the Windows equivalent or launch an X compatible window system, like [vcxsrv], on top of your system -- but why would if you do that if your goal is a to run as headless application?

* The Qt library does provide a [QOffscreenSurface] class but is it intended for cases common to [OpenGL rendering].  Despite the name it does not seem applicable to the problem.

* The Qt help page for [QtCoreApplication] describes it as the class for non-GUI applications:

    > This class is used by non-GUI applications to provide their event loop. For non-GUI application that uses Qt, there should be exactly one QCoreApplication object. For GUI applications, see QGuiApplication. For applications that use the Qt Widgets module, see QApplication.

    But since we need the UI application to only be headless in certain situations it's unclear if this is really applicable.  Our goal is to seamlessly work in the different environments without having to add additional code to switch between `QApplication` and `QCoreApplication`.

* Here's the unanswered [StackOverflow] question asking the same thing.  One comment confirms that it worked with the [offscreen] setting.

[post]: https://www.qcad.org/bugtracker/index.php?do=details&task_id=1534
[QOffscreenSurface]: https://doc.qt.io/qt-5/qoffscreensurface.html
[opengl rendering]: https://forum.qt.io/topic/56889/what-exactly-is-a-qoffscreensurface
[vcxsrv]: https://sourceforge.net/projects/vcxsrv/
[qtcoreapplication]: https://doc.qt.io/qt-5/qcoreapplication.html
[stackoverflow]: https://stackoverflow.com/questions/42686691/create-a-truly-headless-qapplication-instance
[offscreen]: https://doc.qt.io/qt-5/qguiapplication.html#platformName-prop
