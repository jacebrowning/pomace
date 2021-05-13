# Pomace

Dynamic page objects for browser automation.

[![Unix Build Status](https://img.shields.io/github/workflow/status/jacebrowning/pomace/main?label=unix)](https://github.com/jacebrowning/pomace/actions?query=branch%3Amain)
[![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/pomace/main.svg?label=window)](https://ci.appveyor.com/project/jacebrowning/pomace)
[![Coverage Status](https://img.shields.io/codecov/c/gh/jacebrowning/pomace)](https://codecov.io/gh/jacebrowning/pomace)
[![PyPI Version](https://img.shields.io/pypi/v/pomace.svg)](https://pypi.org/project/pomace)
[![PyPI License](https://img.shields.io/pypi/l/pomace.svg)](https://pypi.org/project/pomace)

# Usage

## Quick Start

Open **Terminal.app** in macOS and paste:

```
python3 -m pip install --upgrade pomace && python3 -m pomace run
```

or if you have Homebrew:

```
brew install pipx; pipx run --no-cache pomace run
```

## Installation

If you're planning to run Pomace multiple times, install it with [pipx](https://pipxproject.github.io/pipx/) first:

```
pipx install pomace
```

or get the latest version:

```
pipx upgrade pomace
```

Then download some site models:

```
pomace clone https://github.com/jacebrowning/pomace-twitter.com
```

And launch the application:

```
pomace run twitter.com
```

## Troubleshooting

If you are seeing this error:

```
Traceback (most recent call last):
  File "/Users/Me/.local/bin/pomace", line 5, in <module>
    from pomace.cli import application
  File "/Users/Me/.local/pipx/venvs/pomace/lib/python3.9/site-packages/pomace/cli.py", line 9, in <module>
    from . import models, prompts, server, utils
  File "/Users/Me/.local/pipx/venvs/pomace/lib/python3.9/site-packages/pomace/server.py", line 4, in <module>
    from flask_api import FlaskAPI
  File "/Users/Me/.local/pipx/venvs/pomace/lib/python3.9/site-packages/flask_api/__init__.py", line 1, in <module>
    from flask_api.app import FlaskAPI
  File "/Users/Me/.local/pipx/venvs/pomace/lib/python3.9/site-packages/flask_api/app.py", line 4, in <module>
    from flask._compat import reraise, string_types, text_type
ModuleNotFoundError: No module named 'flask._compat'
```

Trying uninstalling and reinstalling flask:

```
$ pip uninstall flask && python -m pip install flask
```

Then upgrading Pomace:

```
$ pipx upgrade pomace
```
