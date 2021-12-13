---
title: How this blog is themed
date: 2020-09-10T03:19:06.034Z
category: about the blog
tags: blog,pipeline,travis-ci,github,pelican,python
slug: how-this-blog-themes
authors: db
summary: The set-up of this blog's theme.
header_cover: /images/article-bg.png
---

[Pelican] is the tool that makes this static website from the markdown files in the repository.  But, while it has the power to theme the website out of the box, it's not that clear exactly how that is supposed to work.

## Getting the Theme

Pelican themes are packaged as a raw bundle of files, but if you're used to CI workflows this concept is rather challenging.  Instead of installing a theme through the Python package managed `pip`, Pelican expects the files to be available somewhere on disk first and accesses them at run-time, either via a copy or symlink done with the Pelican utility [pelican-themes].

Up to this point in the blog set-up, we've been installing Pelican and its components as Python packages pinned at specific versions -- and pinning dependencies is such a basic requirement of pipeline automation that not having it feels like something is missing.  While some developers have made their theme available as packages (e.g. [Plumage]) most themes are collected as submodules of files in the [Pelican Themes GitHub Project].

## Embedding the Theme

There's different strategies to 'embedding' a theme.  This project has added it to the repo as a git submodule.  A git submodule is a git-specific way to embed one repo into another repo at a specific commit.  So instead of specifying a released version of the theme, the git submodule points to a specific code change in the repository.

Using the [pelican-clean-blog] as an example, we first add the submodule through git:

```console
git submodule add https://github.com/gilsondev/pelican-clean-blog pelican/themes/pelican-clean-blog
```

If you're working on window you'll need to watch out for file paths with slashes.  If you have any error that's like this,

```console
fatal: No url found for submodule path 'pelican/themes/pelican-clean-blog' in .gitmodules
```

Change the slashes from the escaped window slashes `pelican\\themes\\pelican-clean-blog` to the unix slashes `pelican/themes/pelican-clean-blog`.

## Enabling the Theme

After the files are on disk Pelican expects the theme to be enabled in the `pelicanconf.py` file.  First you set the theme's relative path with the `THEME` variable and then set any other auxillary theme setting with more variables:

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
CSS_OVERRIDE = 'extra/css/custom.css'
```

This should now be visible if the build or run the live local server:

```console
python -m pelican --autoreload --listen
```

## Theme as Submodule

Like a rug, a good theme really ties the whole website together.  So I appreciate the work that goes into making one; however, the one point I can't get over is use of copying and pasting files to install the theme.  While using submodules to embed the theme is a good step towards being modular, it feels dated and the wrong tool -- especially when we're already using Python packages.   Hopefully, this is just a transition.  It looks like Pelican 4.0 did start to push for better extension organization, but the current focus is on [Pelican Plugins].  Most of development for the themes in the [Pelican Themes GitHub Project] appears to be stagnant, and only a few talk about supporting Pelican 4.0, and of those even fewer publish their themes as Python package.

[github]: https://github.com
[travis ci]: https://travis-ci.com
[pelican]: http://docs.getpelican.com
[pelican plugins]: https://github.com/pelican-plugins
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
[plugins]: https://github.com/getpelican/cookiecutter-pelican-plugin
