---
title: How this blog styles keyboard keys
date: 2021-01-14 17:48
tags: markdown, pelican, pymdown extensions
slug: how-this-blog-renders-keyboard-keys
authors: db
summary: An quick example of one of how this blog uses PyMdown Extensions' 'keys' feature to render keyboard keys
header_cover: /images/home-bg.png
status: published
categories: about the blog
category: about the blog
type: article
---
<!--
spell-checker:ignore
-->
One of the features this blog uses from the [PyMdown Extensions] extension is the [Keys] option.  That options enables `++` as Markdown syntax and converts it to HTML5's `<kbd></kbd>` html.

This means that `++ctrl+alt+delete++` renders out as ++ctrl+alt+delete++.  Better information is available on the official [help].

## Installation

Install the Python package into Pelican's Python environment:

```console
pip install pymdown-extensions
```

## Configuration

Enable it in the `pelicanconf.py` file, in the `MARKDOWN` variable:

```python
# Extra configuration settings for the Markdown processor.
MARKDOWN = {
    "extension_configs": {
        ....
        'pymdownx.keys' : {},
        ....
    },
    'output_format': 'html5'
}
```

[pymdown extensions]: https://facelessuser.github.io/pymdown-extensions
[keys]: https://facelessuser.github.io/pymdown-extensions/extensions/keys/
[help]: https://facelessuser.github.io/pymdown-extensions/extensions/keys/
