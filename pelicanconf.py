#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# Standard Library
import os
import pathlib

# External Libraries
import pymdownx.emoji

# ####################################
# Metadata
# ####################################

AUTHOR = 'db'
SITENAME = '#Dev'
SITEINDEX_URL = 'enc'
SITESUBTITLE = 'A collection of software development notes'
SITEDESCRIPTION = SITESUBTITLE

# ####################################
# Time and Date
# ####################################

TIMEZONE = 'America/New_York'

# ####################################
# Translations
# ####################################

DEFAULT_LANG = 'en'

# ####################################
# Basic Setting
# ####################################

# Where to output the generated files.
OUTPUT_PATH = pathlib.Path(__file__).parent.resolve().joinpath('output')

# Base URL of your web site - set to localhost for development.
SITEURL = os.environ.get("PELICAN_SITEURL", OUTPUT_PATH.as_uri())

# Developper Setting
LOAD_CONTENT_CACHE = False

# Extra configuration settings for the Markdown processor.
MARKDOWN = {
    "extension_configs": {
        "markdown.extensions.attr_list": {},
        "markdown.extensions.codehilite": {
            "css_class": "highlight",  # highlight provided by pymdown-extensions
        },
        "markdown.extensions.fenced_code": {},
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {},
        'markdown.extensions.admonition': {},
        'markdown.extensions.def_list' : {},
        'pymdownx.superfences' : {
            'disable_indented_code_blocks': True
        },
        'pymdownx.highlight': {
            'legacy_no_wrap_code' : True,
            'linenums_style': 'table',
            'css_class': 'highlight',
            'guess_lang': False,
            'pygments_style': 'default',
            'noclasses': False,
            'use_pygments': True,
            'extend_pygments_lang': []
        },
        'pymdownx.arithmatex'  : {},
        'pymdownx.betterem' : {
            'smart_enable' : 'all'
        },
        'pymdownx.caret' : {},
        'pymdownx.critic' : {},
        'pymdownx.details' : {},
        'pymdownx.emoji': {
            "emoji_index": pymdownx.emoji.emojione,
            "emoji_generator": pymdownx.emoji.to_png,
        },
        'pymdownx.inlinehilite' : {},
        'pymdownx.magiclink' : {},
        'pymdownx.mark' : {},
        'pymdownx.keys' : {},
        'pymdownx.smartsymbols' : {},
        "pymdownx.superfences": {
            # No need for magic indention-based code blocks: all ours are
            # delimited by fences anyway.
            "disable_indented_code_blocks": True,
        },
        'pymdownx.tasklist' : {},
        'pymdownx.tilde' : {},
        'pymdownx.tabbed': {},
    },
    'output_format': 'html5'
}

# Where to output the generated files.
OUTPUT_PATH = 'output/'

# Path to content directory to be processed by Pelican.
PATH = 'content'

# A list of directories and files to look at for pages, relative to PATH.
PAGE_PATHS = [
    'pages'
]

# The article url and file processing options
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'
PAGE_LANG_SAVE_AS = False

# A list of directories and files to look at for articles, relative to PATH.
ARTICLE_PATHS = [
    'articles'
]

# The article url and file processing options
ARTICLE_URL = 'articles/{slug}/'
ARTICLE_SAVE_AS = 'articles/{slug}/index.html'

# The tag / tags index url and file processing options
TAG_URL = 'tag/{slug}/'
TAG_SAVE_AS = 'tag/{slug}/index.html'
TAGS_URL = 'tags/'
TAGS_SAVE_AS = None

# The category index url and file processing options
CATEGORY_URL = 'category/{slug}/'
CATEGORY_SAVE_AS = 'category/{slug}/index.html'

# A list of directories to look for static files, relative to PATH.
STATIC_PATHS = [
    'images',
    'extra'
]

# ####################################
# URL
# ####################################

# Defines whether Pelican should use document-relative URLs or not. Only set this to True when developing/testing
RELATIVE_URLS = False

# ####################################
# Feed settings
# ####################################

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# ####################################
# Pagination
# ####################################

DEFAULT_PAGINATION = 10

# ####################################
# Theme
# ####################################

THEME = os.path.join('pelican', 'themes', 'pelican-clean-blog')

# ####################################
# Theme Specific Settings
# ####################################

HEADER_COVER = 'images/home-bg.png'
HEADER_COLOR = '#004a59'
COLOR_SCHEME_CSS = 'tomorrow_night.css'
EXTRA_PATH_METADATA = {
    'extra/favicon.ico': {'path': 'favicon.ico'}
}
CSS_OVERRIDE = 'extra/css/custom.css'
SOCIAL = [
    ('github', 'https://github.com/dbarsam'),
]
DISPLAY_PAGES_ON_MENU = True
MENUITEMS = [
    ("Archives", "/archives.html"),
    ("Categories", "/categories.html"),
    ("Tags", "/tags.html"),
]

# ####################################
# Plugins
# ####################################
PLUGIN_PATHS = [
    os.path.join('pelican', 'plugins')
]
PLUGINS = [
    'autostatic'
]

# AutoStaic should only process files listed in the YAML metadata
AUTOSTATIC_REFERENCE_PATTERN = r"""^- '{static(?:\s+|\|)((?:"|')?)(?P<path>[^\1=]+?)\1(?:(?:\s+|\|)(?P<extra>.*))?\s*}'$"""
