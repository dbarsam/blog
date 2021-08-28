---
title: How this blog works
date: 2020-09-14T01:29:08.051Z
modified: 2020-09-14 12:30
category: about the blog
tags: blog,pipeline,travis-ci,github,markdown,python
slug: how-this-blog-works
authors: db
summary: A summary of the blog's infrastructure.
---

This project is a blog with a pipeline; the pipeline compiles the project's text files into static html pages and pushes them to a host, which displays it as a website.  The whole process is split along these steps:

1. All content for this blog is stored as files in a project on [GitHub].
2. Articles (written in [Markdown], a plain text mark up language) are submitted as files into the project via Git, the source control of the project.
3. [Travis-CI], which has been watching for any change by Git, creates and launches a build pipeline on one of its servers.
4. A stage in the build pipeline launches [Pelican] and generates all html pages from the project markdown files.
5. Another stage [submits the html files] to the `gh-pages` branch back on GitHub, where Github displays anything on the `gh-pages` branch a static web site.

## GitHub

This project and all of its content is stored and hosted on [GitHub].  There's already too much information about getting started with GitHub so this article assumes that that information is already known.  However, it is important to note that this project is using GitHub in a relatively simple way -- as a *static html site*, hosted by [GitHub Pages] -- and does not use any of the other features that it offers.  For example, this project does not use Jekyll so any mention of that can be ignored.

## Markdown

The actual content of the files is stored as [Markdown] files all in the `content/` folder in a flat listing.  Markdown is a markup language that is easy to read in plain text form and is popular enough that it just makes sense to use it instead of something else.

However, the blog converts markdown to html with the [Python-Markdown] library and uses some custom features provided by [PyMdown Extensions].

## Travis CI

This project's automated actions are executed on [Travis-CI].  Like GitHub, there are almost too many tutorials about how to get started with Travis; services.  This project is using Travis in a relatively simple way and most of the work is handled by the built-in [support of GitHub Pages].  The `.travis-ci.yml` file in this project defines two jobs:

1. Markdown Linting with [MarkdownLint].

    ```yaml
    - stage: lint
      language: node_js
      node_js:
        - 12
      install:
        - npm install -g npm@latest
        - npm install -g markdownlint-cli
      script:
        - markdownlint **/*.md
    ```

2. Build with [Pelican] and publish to [GitHub Pages].

    ```yaml
    - stage: build
      language: python
      python:
        - 3.6
      install:
        - python -m pip install --upgrade pip
        - python -m pip install -r requirements.txt
      script:
        - make publish
      deploy:
        provider: pages
        skip_cleanup: true
        strategy: git
        token: $GITHUB_TOKEN  # Set in the settings page of your repository, as a secure variable
        keep_history: true
        local_dir: output
        on:
          branch: master
    ```

## Pelican

[Pelican] is the tool that generates the static website from the markdown files.  Pelican is a Python package and is installed by Python's package manager, `pip`.  All dependency and their respective versions are listed in the project's `requirements.txt`.

Pelican's configuration files are also written in Python and Pelican's default set-up splits the configuration into two files:

1. `pelicanconf.py` for local development.

2. `publishconf.py` for publishing (which imports `pelicanconf.py` and overrides any setting needed for publishing a website).

Pelican's default set-up also simplifies the execution by providing a convenience `Makefile`.  The `Makefile` is an standard convention that contains pre-configured commands for various tasks.

The `.travis-ci.yml` files executes all of the set-up and Pelican steps during the build and publish step.

## The `gh-pages` branch

GitHub Pages is one of the features that comes with every project and its only job is to display a collection of html files as a website.  Even with that scope, there's still a lot of the different ways to use that feature; a quick search on GitHub Pages will find tutorials that seem contradictory or mention seemly irrelevant or confusing configurations.  This project is creating a *project site* (not a *user site* or *organization*) where the final url will be something like  `https://<user>.github.io/<repository>`.  More information is available from the [GitHub Pages Documentation]

The `gh-pages` branch is a git branch named `gh-pages`.  There is nothing special about the branch, except that `gh-pages` is the default value for that branch that GitHub uses for as a [publishing source].  Travis-Ci follows GitHub's lead and its publish commanded uses `gh-pages` as a default value its `target_branch` setting.

[github]: https://github.com
[travis-ci]: https://travis-ci.com
[pelican]: http://docs.getpelican.com
[submits the html files]: https://docs.travis-ci.com/user/deployment/pages/
[pelican-themes]: https://docs.getpelican.com/en/stable/pelican-themes.html
[Pelican Themes GitHub Project]: https://github.com/getpelican/pelican-themes
[plumage]: https://pypi.org/project/plumage/
[github pages]: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
[markdown]: https://daringfireball.net/projects/markdown/
[support of GitHub Pages]: https://docs.travis-ci.com/user/deployment/pages/
[markdownlint]: https://github.com/DavidAnson/markdownlint
[github pages documentation]: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#types-of-github-pages-sites
[publishing source]: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#publishing-sources-for-github-pages-sites
[Python-Markdown]: https://python-markdown.github.io/extensions/fenced_code_blocks/
[PyMdown Extensions]: https://facelessuser.github.io/pymdown-extensions/
