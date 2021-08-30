---
title: How this blog is themed
date: 2020-09-14T01:29:08.051Z
category: about the blog
tags: blog,pipeline,travis-ci,github,markdown,python
slug: how-this-blog-themes
authors: db
summary: A summary of the blog's theming infrastructure.
header_cover: /images/article-bg.png
---

[Pelican] is the tool that generates the static website from the markdown files and part of its appeal is its ability to theme the website.  However, it's not that clear exactly how that is supposed to work.

## Getting the Theme

Pelican themes are packaged as a raw bundle of files and if you're used to CI workflows, then this concept is rather challenging.  Instead of installing a theme through the Python package managed `pip`, Pelican expects the files to be available somewhere on disk first and accesses them at run-time, either via a copy or symlink with the Pelican utility [pelican-themes].

Up to this point in the blog set-up, we've been installing Pelican and its components as Python packages pinned at specific versions -- and pinning dependencies is such a basic requirement of pipeline automation that not having it feels like something is missing.  While some developers have made their theme available as packages (e.g. [Plumage]) most themes are collected as submodules of files in the [Pelican Themes GitHub Project].

## Embedding the Theme

This project has selected a theme and added it to the repo as a git submodule.  A git submodule is a git-specific way to embed one repo into another repo at a specific commit.  So instead of specifying a released version of the theme, the git submodule points to a specific point in the repository.

 Using the [pelican-clean-blog] as an example, we first add the submodule through git:

```console
git submodule add https://github.com/gilsondev/pelican-clean-blog pelicam/themes/pelican-clean-blog
```

If you're working on window, watching for file path slashes.  If you have any error that's like

```console
fatal: No url found for submodule path 'pelican/themes/pelican-clean-blog' in .gitmodules
```

Change the slashes from the escaped window slashes `pelican\\themes\\pelican-clean-blog` to the unix slashes `pelican/themes/pelican-clean-blog`


## Enabling the Theme

After the files are on disk, you enable the theme in the `pelicanconf.py` file.  First you set the theme with the `THEME` variable and then set any other auxillary theme setting with more variables:

```python
# ####################################
# The Theme
# ####################################
THEME = 'pelican/themes.pelican-clean-blog'

# ####################################
# The Theme Specific Settings
# ####################################
HEADER_COVER = 'images/home-bg.png'
HEADER_COLOR = '#004a59'
COLOR_SCHEME_CSS = 'tomorrow_night.css'
EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'favicon.ico'}
}
```

[github]: https://github.com
[travis ci]: https://travis-ci.com
[pelican]: http://docs.getpelican.com
[submits the html files]: https://docs.travis-ci.com/user/deployment/pages/
[pelican-themes]: https://docs.getpelican.com/en/stable/pelican-themes.html
[Pelican Themes GitHub Project]: https://github.com/getpelican/pelican-themes
[plumage]: https://pypi.org/project/plumage/
[github pages]: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
[markdown]: https://daringfireball.net/projects/markdown/
[support of ghitub pages]: https://docs.travis-ci.com/user/deployment/pages/
[markdownlint]: https://github.com/DavidAnson/markdownlint
[github pages documentation]: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#types-of-github-pages-sites
[publishing source]: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#publishing-sources-for-github-pages-sites
[pelican-clean-blog]: https://github.com/gilsondev/pelican-clean-blog
