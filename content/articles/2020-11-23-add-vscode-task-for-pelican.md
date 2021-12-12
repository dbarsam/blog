---
title: VSCode tasks for Pelican blogs
date: 2020-11-23T03:40:27.619Z
category: about the blog
tags: blog,vscode,pelican
slug: vscode-task-pelican
authors: db
summary: How to run Pelican commands from within Visual Studio Code.
header_cover: /images/article-bg.png
---

VSCode's [tasks feature] is the editor's mechanism to execute building, testing, and other software development actions from the comfort of the IDE.  Most of the common tasks are built-in or provided by plugins, but it's also possible to define workspace tasks in the project's `tasks.json` file.

In this Pelican powered project, we can take advantage of that flexibility and add support for two Pelican specific commands:  build and serve.

## The `build` Task

The build command is pretty straight forward to adapt.  On the command line it looks like this:

```batch
python -m pelican .\content
```

And we can turn that into the following json block and add it to the `tasks.json` file in the project's `.vscode` folder:

```json
    {
        "label": "pelican-build",
        "type": "process",
        "isBuildCommand": true,
        "command": "${workspaceFolder}\\.conda\\env\\python.exe",
        "args": [
            "-m",
            "pelican",
            "${workspaceFolder}\\content"
        ],
        "problemMatcher": []
    },
```

We mark this task as an explicit *build* command with the `isBuildCommand` flag.  This adds it the list of commands automatically bound to VSCode's ++ctrl+shift+b++ keyboard mapping.

We also add an empty `problemMatcher`.  VSCode's [problem matching] feature is how the editor converts the text output of the command into the editor's [problems panel], accessible via ++ctrl+shift+m++.  Unfortunately Pelican does not output its error messages into a compatible format so we add the feature but leave it empty until a future change in either VSCode or Pelican.

## The `serve` Task

The `serve` command is also fairly simple to adapt.  Like the `build` command we take a command line and turn it into a json task entry.

The serve command line:

```shell
python -m pelican --autoreload --listen
```

The json equivalent of the command line, added it to the `tasks.json` file in the `.vscode` folder:

```json
    {
        "label": "pelican-serve",
        "type": "process",
        "isBackground": true,
        "runOptions": {
            "instanceLimit": 1
        },
        "command": "${workspaceFolder}\\.conda\\env\\python.exe",
        "args": [
            "-m",
            "pelican",
            "--autoreload",
            "--listen"
        ],
        "problemMatcher": []
    },
```

Since this task will be running the internal web server in the background, we mark it with the `isBackground` flag and we limit the instances to a single instance in the `runOptions`.  This allows us to launch it once from VSCode and any subsequent launch will prompt us to kill it or restart it, avoiding any awkwardness over the single HTTP port.

We don't bother with a keyboard shortcuts for two reasons:

1. Unlike the build task above, there's no support for a global *watcher* task that can be overridden; VSCode only supports *build* and *test* tasks and nothing else.

2. Project specific keyboard shortcuts are not possible.  See [Issue #23757] for more details.

And of course, we also add an empty `problemMatcher` for the same reasons listed above.

[tasks feature]: https://code.visualstudio.com/docs/editor/tasks
[problems panel]: https://code.visualstudio.com/docs/editor/editingevolved#_errors-warnings
[problem matching]: https://code.visualstudio.com/docs/editor/tasks#_defining-a-problem-matcher
[issue #23757]: https://github.com/Microsoft/vscode/issues/23757
