---
title: How this blog detects broken links - update
date: 2021-02-01 19:25
tags: markdown, travis, bash
slug: how-this-blog-detects-broken-links-i
authors: db
summary: An update to validating local and internet links in markdown files.
header_cover: /images/article-bg.png
status: published
category: about the blog
type: article
---
<!--
spell-checker:ignore
-->
This article is a follow-up to [how this blog detects broken links], describing updated ways to use the [markdown-link-check] npm package.

## Batch Operation

The previous article used a `for` loop and an shortcut or-operator (`||`) with an `exit` command.

```bash
for file in  $(find ./content -name \*.md); do markdown-link-check --verbose "$file" || exit 1; done;
```

That `exit` command turned out to exit the shell in some cases and this was not desirable on some machines.  Instead, we switched to `xargs` and enforce single parameters with `--max-lines` argument:

```bash
find content -name \*.md -print0 | xargs --null --max-lines=1 markdown-link-check --config .markdown-link-check.json --verbose
```

Using `xargs` introduces some new changes.  At first `xargs` passed all arguments to `markdown-link-check`, but the additional flag executes it once per file.  Second, `xargs` will return back exit code 123 if any of invocations returns back a non-zero value, which is fine in the ci pipeline.  And lastly, `xargs` processes all arguments, regardless if one invocation fails.  This is desirable in our case because we need to check all links and not quit at the first failure.

## Ignore Rules

We have another update regarding Pelican's shorthand for [local links]: `{filename}` and `{static}`.  These are not valid links but we create a configuration file, `.markdown-link-check.json`, and use the `ignorePatterns` option to skip those special cases.  Before we could use the raw `{` and `}` characters.  Now, it looks like we have to use the html escape codes `%7B` and `%7D`:

```json
{
    "ignorePatterns": [
        {
            "pattern": "^({|%7B)filename(}|%7D)"
        },
        ....
    ]
}
```

For backwards compatibility, both characters are in a regex _or_ (`|`) group.

[local links]: https://docs.getpelican.com/en/latest/content.html#linking-to-internal-content
[how this blog detects broken links]: {filename}../2020-11-08-link-checker/link-checker.md
[markdown-link-check]: https://github.com/tcort/markdown-link-check
