---
title: How this blog renders code samples
date: 2020-09-14T01:29:08.051Z
modified: 2020-09-14 12:30
category: about the blog
tags: blog,pipeline,
slug: how-this-blog-renders-code-sample
authors: db
summary: A summary about the blog's code formatting
---

Sometimes it's easier just to show to copy and paste-able code.  Pelican doesn't handle this out of the box so we need to extend it with a couple of plugins and extensions.

## Handling Code with Markdown

The first part is to use the correct Markdown syntax.  The problem here is that most examples explaining how to do this are written for different flavours of Markdown and may not be applicable to our Pelican powered blog.

Starting with the basics, Markdown handles code blocks with code fences, denoted by the 3 backticks (` ``` `).  For example, consider the below Markdown:

````markdown
```
This is a monospace code block
```
````

This gets rendered as:

```markdown
This is a monospace code block
```

However that's the basic case and unfortunately, there's more needed to take that and make it display code sample in a Pelican blog.

## Syntax Highlighting

Markdown doesn't handle syntax highlighting.  Instead it passes the code-fence's attributes to the renderer and it interprets in some way.  In most cases, it adds it to the resulting html as a css class.  Consider this bit of Markdown describing Python code:

````markdown
```python
print("Hello world")
```
````

The `python` text there is just an text attribute is passed through to the html as a interpreted as css class for that particular scope.  [Python-Markdown] has a much better explanation about attributes and syntax highlighting in its [Fenced Code] section, so please refer to that for more information.

The important thing to note is that in [Python-Markdown] it's actually the [codehilite] extension that is responsible for the syntax highlighting and the actual rendering of the text is controlled by its `css_class` option, which by default is also set to `codehilite`.

The basic code fence and the syntax highlighting work pretty much out of the box so there's no need to tinker with the settings.  However, this blog does tinker with the settings because of requiring more specialized way of rendering code blocks.

## Nested Code Blocks

Instructional steps are nice and having those steps point to fully rendered code blocks is even nicer.  This is one part where the standard Markdown specification doesn't really provide a definition and [Python-Markdown] doesn't seem to support it, so this a case where it's up to other groups provide a solution and implement this feature in their Markdown 'flavour'.

Consider this this bit of Markdown:

```markdown
1. Step 1

2. Step 2, but with Python code.

    ```
    print("Hello world")
    ```

3. Step 3, but with syntax highlighted Python code.

    ```python
    print("Hello world")
    ```
```

This Markdown sample lists a series of steps and, in Step 2 and 3, adds a bit of sample Python code.  The code in Step 2 should render as monospace text, but the code in Step 3 should be rendered with syntax colouring appropriate for Python.  Unfortunately, this is somewhat fragile and only works in a very specific scenario:

1. Indent your fenced block by an indent at your level (i.e. add extra 4 spaces).
2. The fence requires a newline above and below the fenced block, so to be consistent, make the whole list double spaced.

And even then, this is only made possible by some behind the scenes work in our Pelican configuration file.  By default, Pelican is being powered by [Python-Markdown] and that will not render our example correctly.  Instead, we need to first install another package, [pymdown-extensions] and then enable its [superfences] extension in the `pelicanconf.py` file:

```python
MARKDOWN = {
    "extension_configs": {
        ....
        'pymdownx.superfences' : {}
        ....
    },
    'output_format': 'html5'
}
```

After that, the aboves renders as expected with the [pymdown-extensions]'s default settings:

1. Step 1

2. Step 2, but with Python code.

    ```text
    print("Hello world")
    ```

3. Step 3, but with syntax highlighted Python code.

    ```python
    print("Hello world")
    ```

## Adding line numbering

Line numbering is handles by [superfences] and it's help page is great at aswering questions.  For this blog, it's important to note that out of the box, there are two options to rendering line numbers:

1. Embedded
2. Separate Table Column

Note:  [pymdown-extensions] does add third option, `pymdownx-inline`, but that's not working with this current theme. Incidentally, this seems to be part of a larger problem of non-working extensions, like `markdown.extensions.admonition` and `pymdownx.tabbed`, and its not clear if the fault lies with the theme, Pelican, or something on the blog's configuration side.  As a result, this blog uses the separate table column as configured in thr `pelicanconf.py`, under the `pymdownx.highlight` extension:

```python
MARKDOWN = {
    "extension_configs": {
        ....
        'pymdownx.highlight' : {
            ....
            'linenums_style': 'table',
            ....
        }
        ....
    },
    'output_format': 'html5'
}
```

The `pelicanconf.py` configurat has line number disabled by default. Line numbers are enabled by adding the `linenums` attribute to each individual code block with the starting line number as its argument.

For example, this Markdown:

````markdown
```python linenums="3"
for i in range(10):
    print("Hello world!")
print("Goodbye")
```
````

Renders this code, with line number starting on line 3.

```python linenums="3"
for i in range(10):
    print("Hello world!")
print("Goodbye")
```

To highlight a specific lines use the `hl_lines` option.

For example, this Markdown:

````markdown
```python linenums="5" hl_lines="2-3"
for i in range(10):
    print("Hello world!")
print("Goodbye")
```
````

Renders this code, with line number starting on line 5, but highlighted code block lines 2 and 3:

```python linenums="5" hl_lines="2-3"
for i in range(10):
    print("Hello world!")
print("Goodbye")
```

Note that the `hl_lines` refers to lines in the code block, not the lines as numbered by `linenums`.

## Line Numbering And Line Wrapping

There's one small problem with the theme and [pymdown-extensions].  If a line of code is too long, the theme will wrap the code but not update the line numbering accordingly.  The ends up with mis-aligned line numbering and breaks the feature.

To work around this, this blog disables word wrapping for code blocks in the `pelicanconf.py` file with the `legacy_no_wrap_code`.

```python
MARKDOWN = {
    "extension_configs": {
        ....
        'legacy_no_wrap_code' : True,
        'pymdownx.highlight' : {
            ....
            'linenums_style': 'table',
            ....
        }
        ....
    },
    'output_format': 'html5'
}
```

For example, this Markdown:

````markdown
```python linenums="5"
for i in range(10):
    print("ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ")
print("Goodbye")
```
````

Renders the long line at line `6` un-wrapped and preserves the alignment with the table columns:

```python linenums="5"
for i in range(10):
    print("ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ")
print("Goodbye")
```

It's important to also note that this is behaving differently if there were no line numbering at all. For example, the above code block with the `linenums` attribute removed renders this code block:

```python
for i in range(10):
    print("ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ")
print("Goodbye")
```

The above code block is not wrapped, but embedded in a scroll box to work around that.  The problem lies with the table mechanism used for the table column line numbering. Underneath the hood, the code block with `linenums` renders this html:

```html
<table class="highlighttable"><tr><td class="linenos"><div class="linenodiv"><pre><span></span><span class="normal">5</span>
<span class="normal">6</span>
<span class="normal">7</span></pre></div></td><td class="code"><div class="highlight"><pre><span></span><span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="mi">10</span><span class="p">):</span>
    <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;</span><span class="p">)</span>
<span class="nb">print</span><span class="p">(</span><span class="s2">&quot;Goodbye&quot;</span><span class="p">)</span>
</pre></div>
</td></tr></table>
```

While the one without, renders this html (which is the same as the table cell containing the code in the above example):

```html
<div class="highlight"><pre><span></span><span class="k">for</span> <span class="n">i</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="mi">10</span><span class="p">):</span>
    <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ ABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;</span><span class="p">)</span>
<span class="nb">print</span><span class="p">(</span><span class="s2">&quot;Goodbye&quot;</span><span class="p">)</span>
</pre></div>
```

[python-markdown]: https://python-markdown.github.io/extensions/fenced_code_blocks/
[pymdown-extensions]: https://facelessuser.github.io/pymdown-extensions/
[superfences]: https://facelessuser.github.io/pymdown-extensions/extensions/superfences/
[Fenced Code]: https://python-markdown.github.io/extensions/fenced_code_blocks/
[codehilite]: https://python-markdown.github.io/extensions/code_hilite/
