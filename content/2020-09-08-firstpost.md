---
title: How this blog works
date: 2020-09-14T01:29:08.051Z
modified: 2020-09-14 12:30
category: misc
tags: blog
slug: how-this-blog-works
authors: D Barsam
summary: A quick summary about the blog's backend structure.
---

# How this blog works

This project is a blog with a pipeline.  The pipeline builds the blog's web site with a number of CI/CD components:

1. The content for this blog is stored as a project on [GitHub].
2. An article (written in Markdown, a plain text mark up language) is subitted to the project.
3. [Travis CI], which has been watching for this change, kicks off a build step with the repository.
4. The build step launches [Pelican] and generates all html pages from the project markdown files.
5. Travis CI [submits the html files] to the `master` branch back on GitHub.
6. GiHub displays the html files as a static web site.

[github]: https://github.com
[travis ci]: https://travis-ci.org
[pelican]: http://docs.getpelican.com
[submits the html files]: https://docs.travis-ci.com/user/deployment/pages/
