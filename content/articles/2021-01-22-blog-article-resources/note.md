---
title: How this blog manages article assets
date: 2021-01-22 19:13
tags: markdown, pelican
slug: how-this-blog-manages-article-assets
authors: db
summary: How to use Autostatic to re-organize Pelican's default article structure to be more article specific.
header_cover: /images/home-bg.png
status: published
categories: about the blog
category: about the blog
type: article
attachments:
    - '{static images/pelly2.png}'
    - '{static pdfs/pelly2.pdf}'
---

Sooner or later, an article will require an attachment.  These accompanying non-markdown files are usually images, maybe a pdf, or even an fully working piece of code that are used or reference by the article.

How exactly to best do this is open to debate. This article examines a strategy to make the management of article assets more modular than what's availabelw tih the default settings.

## Pelican Asset Management

Pelican treats the articles and assets as two different types of source material.  The article are, of course, [articles], but to Pelican, the assets are [static files].  For now, we're going to ignore pages.

Adding an extra layer of complexity, Pelican also splits the discovery and processing of these assets into two distinct operations.  So while the markdown files and the accompanying image files could be stored next to each other, the Pelican build command would we move them to different locations.

If you're used to writing Markdown in VSCode (or any other tool that immediately renders Markdown) this may be a bit jarring.  In those cases, everything will appear to work in the editor but fail in the final Pelican build.

## Global Assets

Out of the box, Pelican works with the following structure:

```console
project/
├── content
│   ├── articles/
│   │   ├── article1.md
│   │   └── article2.md
│   ├── images/
│   │   └── pelly.png
│   ├── pdfs/
│   │   └── pelly.pdf
│   └── pages/
│       └── test.md
└── pelican.conf.py
```

The `articles` and `pages` are both separate types of content and have their own distinctinct discover option, the respective `ARTICLE_PATH` and `PAGES_PATH` options.  However, the `images` and `pdf` are static files and are discovered by the `STATIC_PATHS` option.  These are all documented in the [url settings] section of the options page.

However, the images and pdfs in that structure are separateed from their respective articles.  This makes sense if these assets are meant to be accesible from any article or page in the website.

However if those assets are article specific, then this layout does not make sense.  As more articles are added to this structure it will be harder and harder to track which asset belongs to with files.

## Article Specific Assets

To make things more modular, we keep the assets specific to the article along side the article.  In our above example, this would transform `article1` from a file into a folder containing the image, the pdf, and the referring article:

```console
project/
├── content
│   ├── articles/
│   │   ├── article1/
│   │   │   ├── images/
│   │   │   │   └── pelly.png
│   │   │   ├── pdfs/
│   │   │   │   └── pelly.pdf
│   │   │   └── article.md
│   │   └── article2.md
│   └── pages/
│       └── test.md
└── pelican.conf.py
```

To make this work, we first configure Pelican to generate slug folders instead of individual pages.  We do this easily enough with the following options into our `pelicanconf.py` file:

```python
ARTICLE_PATHS = [
    'articles'
]
ARTICLE_URL = 'articles/{slug}/'
ARTICLE_SAVE_AS = 'articles/{slug}/index.html'
```

The above settings configure Pelican to disocver files in the `articles` folder, save them as `index.html` files in the pages's `slug` folder, and update the url to the cleander folder style that defaults to loading the `index.html` file.  The `slug` value comes from the article's slug [metadata field], which we set at the top of each article.

The next part is to configure Pelican to move the assets to a relative folder inside the slug folder instead of the global folder.  This is done by [attaching] the files to the article with the `{attach}` keyword inside our `article1\article.md` file:

=== "Markdown"
    ```markdown
    ---
    Title: Test Article
    Category: test
    Date: 2014-10-31
    Slug: article1
    ---

    This is an image:

    ![pelly.png]({attach}images/pelly.png)

    This is a link to a [pdf] files.

    [pdf]: {attach}pdfs/pelly.pdf
    ```

=== "Result"
    This is an image:

    ![pelly.png]({attach}images/pelly.png)

    This is a link to a [pdf] files.

    [pdf]: {attach}pdfs/pelly.pdf

Just like the `{static}` and `{filename}` tokens, Pelican uses a the `{attach}` to mark the link for special handling.  However, in this case, Pelican will move the asset relative to a path the file instead of the more global location denoted by `{static}`.

## The AutoStatic Plugin

The attach method works well for assets that are directly linked to the article.  This doesn't work for internal assets,like custom css or javascript files.  Those files are not displayed like an image or a download link so there is no way to `{attach}` them to the article.

Fortunately, Alexandre Fonseca's [autostatic plugin] handles these internal assets quite nicely.  His plugin creates a new `{static}` tag that copies the `{attach}` tag's functionality but also extends it.

There's more info in the project's readme, but one nice feature is that it reads the tag from anywhere in the article -- including the metadata section.  That allows us to lump all of the assets into a single place and removes any non-markdown tag from the actual article.

Consider our example from above where we used the `{attach}` tag in the links to the png and pdf files.  With `autostatic` we can restore those links to *pure* markdown links and register all local assets in the metadata:

=== "Markdown"
    ```markdown
    ---
    Title: Test Article
    Category: test
    Date: 2014-10-31
    Slug: article1
    Attachments:
        - '{static images/pelly3.png}'
        - '{static pdfs/pelly3.pdf}'
    ---

    This is an image:

    ![pelly2.png](images/pelly2.png)

    This is a link to a [another pdf] files.

    [another pdf]: pdfs/pelly2.pdf
    ```
=== "Result"
    This is an image:

    ![pelly2.png](images/pelly2.png)

    This is a link to a [another pdf] files.

    [another pdf]: pdfs/pelly2.pdf

There's a few things to note with our example:

- We created a new metadata field, `Attachment`, but that name is arbitrary and it could be called anything, like `Files` or even `Assets`.  Pelican allows dynamically created metadata fields, as long as it doesn't conflict with [existing metadata].

- The plugin scans the rendered metadata and the rendered html document, processing any `{static}` tag defined by the `AUTOSTATIC_REFERENCE_PATTERN` regex expression.  Any matching files are copied to the respective location and any references in the metadata or html is replaced with the qualified url, so as along as the file is referenced at least once, it will be copied.

- The example's YAML has formatted the metadata as a list of strings. This is to work around some YAML processor which might interpret the raw `- { .... }` as a list item referencing a mal-formed dictionary. We work around that by escaping the expression as a string ``- `{ .... }` ``.

- The plugin is a little too greedy with processing the various `{static}` tags in the file.  Out of the box, the plugin  will process everything, including any references in code samples -- even through it should be ignored because the content is rendered in a `<code>` html block.

    To work around that, this site changes the plugin's  `AUTOSTATIC_REFERENCE_PATTERN` setting to explicitly use the metadata's single line usage of `- '{static ...}'`.  We do this by changing the regex pattern in the `pelicanconf.py`:

    ```python
    AUTOSTATIC_REFERENCE_PATTERN = r"""^- '{static(?:\s+|\|)((?:"|')?)(?P<path>[^\1=]+?)\1(?:(?:\s+|\|)(?P<extra>.*))?\s*}'$"""
    ```

    This works because the plugin processes the rendered html as a single block of text and processes each value in the metadata list as single lines that starts with a `-` and ends with the `}`.

The ability to organize the attachments in the metadata (wether intentional or not) is a nice feature.  It allows us to manage the article assets as actual article as attachments, described in the metadata block and copied with the article whenever it is processed by Pelican.

[articles]: https://docs.getpelican.com/en/latest/content.html#articles-and-pages
[static files]: https://docs.getpelican.com/en/latest/content.html#static-content
[url settings]: https://docs.getpelican.com/en/latest/settings.html#url-settings
[metadata field]: https://docs.getpelican.com/en/latest/content.html#file-metadata
[attaching]: https://docs.getpelican.com/en/latest/content.html#attaching-static-files
[autostatic plugin]: https://github.com/AlexJF/pelican-autostatic
[pelly.png]: {attach}images/pelly.png
[pelly.pdf]: {attach}pdfs/pelly.pdf
[existing metadata]: https://docs.getpelican.com/en/stable/content.html#file-metadata
[official documentation]: https://github.com/AlexJF/pelican-autostatic
