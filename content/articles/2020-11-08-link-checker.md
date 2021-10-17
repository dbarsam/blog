---
title: How this blog detects broken links
date: 2020-11-08T21:25:04.051Z
category: about the blog
tags: blog,markdown,travis,bash
slug: how-this-blog-detects-broken-links
authors: db
summary: How to validate local and internet links in markdown files.
header_cover: /images/article-bg.png
---

In VSCode, this blog use the [HTTP/s and relative link checker] extension to check url links in markdown files.  The extension is pretty basic, but it does what it says on the tin.

The blog's pipeline is slightly different and in there we use the [markdown-link-check] npm package.  To get started with the `markdown-link-check` the site recommends using this `find` shell command:

```bash
find . -name \*.md -exec markdown-link-check {} \;
```

However, that won't work for our Travis-CI powered pipeline.  When Travis is checking the result of that command, it only processes the exit code of the `find` command and not the result of `markdown-link-check`, which is executed by `find`'s `exec` option.

To fix this, we need to resort to a more basic shell loop -- but even then there are some issues.  First, we need to enable the `globstar` shell option, introduced in Bash 4.0:

```bash
shopt -s globstar
for x in **/*.md; do markdown-link-check --verbose "$x"; done
```

And second, we need to heed the warnings that the glob `**` pattern also traverses symbolic links.  This project is small enough that it doesn't have to worry about that feature, but it's worthwhile to note it and find a safer alternative.

Fortunately we can combine both solutions.  We'll use `find` to generate a list of files, but plug that list into the for loop and submit each file for inspection as a separate shell command:

```bash
for file in  $(find ./content -name \*.md); do markdown-link-check --verbose "$file" || exit 1; done;
```

The extra bit of magic here is that we check the result of `markdown-link-check` against the exit command with the short-circuit *or* condition (`||`):

- If `markdown-link-check` is successful, it returns `0` which is the equivalent of True, which then satisfies the *or* expressions, so it skips the `exit` command, continuing on with the loop.

- If `markdown-link-check` is not successful, it returns the equivalent of False, so the shell evaluates the other side of the *or* expression and exits the instance with the default error value of `1`.

This is a fancy shell trick that makes the final travis job  nice and compact:

```yaml
- stage: lint
    language: node_js
    node_js:
    - 12
    install:
    - npm install -g npm@latest
    - npm install -g markdown-link-check
    script:
    - for file in  $(find ./content -name \*.md); do markdown-link-check --verbose "$file" || exit 1; done;
```

[markdown-link-check]: https://github.com/tcort/markdown-link-check
[HTTP/s and relative link checker]: https://marketplace.visualstudio.com/items?itemName=blackmist.LinkCheckMD
