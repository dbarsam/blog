---
title: How this blog centers images
date: 2021-01-15 18:45
tags: markdown, pelican, python, css, pymdown extensions
slug: how-this-blog-centers-images
authors: db
summary: One of the many ways to center an image with Markdown and CSS in a Pelican blog.
header_cover: /images/home-bg.png
status: published
categories: about the blog
category: about the blog
type: article
---
<!--
spell-checker:ignore
-->
Here is a common question that has almost an infinite number of answers:  [How do I center an image in Markdown]?

The solution (for this blog, at least) comes in two parts:  CSS and Markdown Attributes.

## CSS Classes

We skip over any embedded HTML shenanigans and go for the CSS option.  There, we define two new CSS classes.  One will handle images and another one to handle text:

```css
.center-image
{
    margin: 0 auto;
    display: block;
}

.center-text
{
    text-align: center;
}
```

We write them in the site's `custom.css` file (`extra/css/custom.css`) and we inject that into the current [theme] via its [CSS_OVERRIDE] setting:

```python
CSS_OVERRIDE = 'extra/css/custom.css'
```

This configuration expose the CSS class names for the Markdown parser to later manipulate.

## Attributes

With the classes defined, we link them to the Markdown element via attributes.  Attributes are a non-standard feature, provided by Python Markdown's [attr_list] extension, that makes CSS attributes accessible in Markdown syntax.  Without attributes, we would have to resort to embedding raw HTML in the Markdown files.  But with them, we have a cleaner syntax to add HTML style and class names to the Markdown content.

### Installation

We first install the Python package into Pelican's Python environment:

```console
pip install markdown
```

## Configuration

And then we enable it in the `pelicanconf.py` file, in the `MARKDOWN` variable:

```python
# Extra configuration settings for the Markdown processor.
MARKDOWN = {
    "extension_configs": {
        ....
         "markdown.extensions.attr_list": {},
        ....
    },
    'output_format': 'html5'
}
```

The extension is also bundled with the [extra] extension, so enabling that extension will have the same effect -- but watch out for the conflict if you're also going to use [PyMdown Extensions]' own version of `extra`.

### No Attributes

The vanilla version of our content consists of a simple image and paragraph:

```markdown
![pelican-logo]

This is a logo.

[pelican-logo]: https://raw.githubusercontent.com/getpelican/pelican-blog/main/content/logo/pelican-logo-small.png
```

And that renders out as this:

![pelican-logo]

This is a logo.

### Centered Attributes

We now update the content with our image and text attributes:

```markdown
![pelican-logo]{: .center-image}

This is a logo.
{: .center-text}

[pelican-logo]: https://raw.githubusercontent.com/getpelican/pelican-blog/main/content/logo/pelican-logo-small.png
```

Note: The `{: .center-text}` attribute goes at the end of the element because the text paragraph is a *block level element*.  More information is available from the official [Python-Markdown help].

The above renders out as this:

![pelican-logo]{: .center-image}

This is a logo.
{: .center-text}

[how do i center an image in markdown]: https://stackoverflow.com/questions/3912694/using-markdown-how-do-i-center-an-image-and-its-caption
[pelican-logo]: https://raw.githubusercontent.com/getpelican/pelican-blog/main/content/logo/pelican-logo-small.png
[python-markdown help]: https://python-markdown.github.io/extensions/attr_list/#block-level
[extra]: https://python-markdown.github.io/extensions/extra/
[attr_list]: https://python-markdown.github.io/extensions/attr_list
[pymdown extensions]: https://facelessuser.github.io/pymdown-extensions/extensions/extra/
[theme]: https://github.com/gilsondev/pelican-clean-blog
[css_override]: https://github.com/gilsondev/pelican-clean-blog#user-defined-css
