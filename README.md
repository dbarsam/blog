# blog

A project to contain the source code and content for the *#Dev* [blog].

## Setup

The blog is written in Markdown and compiled into HTML with [Pelican].  To setup a space for local development, first create a Python 3.6 environment and then install the Python packages in this project's `requirements.txt` file.

```console
python -m pip install -r requirements.txt
```

## Build

After setup, use the `pelican` module to build the content:

```console
python -m pelican .\content
```

Or use the pelican module to host a local server at <http://localhost:8000/> and auto-build html on any change:

```console
python -m pelican --autoreload --listen
```

[blog]: https://dbarsam.github.io/blog/
[pelican]: https://blog.getpelican.com/
