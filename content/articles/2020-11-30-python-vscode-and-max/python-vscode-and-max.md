---
title: Set up VSCode to Debug Python in 3ds Max
date: 2020-11-30 10:10
tags: python, 3ds max, vscode
slug: python-vscode-max
authors: db
summary: A multipart article describing how to debug an application's embedded Python environment.
header_cover: /images/article-bg.png
status: published
categories: developer set-up
category: developer set-up
type: article
---
<!--
spell-checker:ignore
-->
Unfortunately, not every application embeds Python the same way.  This makes developing Python tools for these applications awkwardly challenging.  Some applications obfuscate the interpreter it by compiling directly it into the application, while others take a more modular approach and ship a complete Python installation -- including an equivalent `python.exe` and `site-package` folder -- in a easily accessible folder in the application's installation directory.

But even ignoring the differences between how the applications embed these Python environment, there's usually one or two additional design choices that makes developing these Python plugins even harder than they need to be. It's almost as if the applications' creators embed Python as an afterthought, slating it as an auxillary scripting language that's only there to implement a few automation macros.  Python is infinitely more open, so developing anything more powerful often takes on a journey of connecting mismatched puzzle pieces that ends up with a somewhat unsatisfying solution.

This is a multipart article that tries to come up with a satisfactory solution.  We work through the various puzzle pieces and come up the necessary glue to make them work together.  In order to keep us focus, we'll develop this solution with a specific goal of using VSCode to debug a local Python package in an application's embedded Python environment.  Most of this workflow is pretty generic, but in the few cases where it isn't, we'll use an example application of 3ds Max 2018, with Python 2.7, and running on Windows, to explain the specificities.

## The Infrastructure

Breaking it down, we are going to set-up a workflow with the following components:

1. A *side-car* virtual environment.
2. A *bootstrap* script to temporarily graft the side-car virtual environment onto the application.
3. A Python *debugging library* that can handle remote debugging.
4. An *auto-attach* workflow that gives the user a seamless debugging experience in VSCode.

## The tutorials

1. [Part I]: The Python side-car environments
2. [Part II]: The bootstrap script
3. [Part III]: The Python debugger library
4. [Part IV]:  The Attach-To-Process launcher in VSCode
5. [Part V]: The Auto-Attach-To-Process launcher in VSCode

This series starts with [Part I] by repurposing a very basic component of Python development, the virtual environment.

[part i]: {filename}../2020-12-01-python-vscode-and-max-1/python-vscode-and-max-1.md
[part ii]: {filename}../2020-12-03-python-vscode-and-max-2/python-vscode-and-max-2.md
[part iii]: {filename}../2020-12-05-python-vscode-and-max-3/python-vscode-and-max-3.md
[part iv]: {filename}../2020-12-07-python-vscode-and-max-4/python-vscode-and-max-4.md
[part v]: {filename}../2020-12-09-python-vscode-and-max-5/python-vscode-and-max-5.md
