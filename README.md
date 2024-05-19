# Pomace

Dynamic page objects for browser automation.

[![Linux Build](https://img.shields.io/github/actions/workflow/status/jacebrowning/pomace/main.yml?branch=main&label=linux)](https://github.com/jacebrowning/pomace/actions)
[![Windows Build](https://img.shields.io/appveyor/ci/jacebrowning/pomace/main.svg?label=windows)](https://ci.appveyor.com/project/jacebrowning/pomace)
[![Code Coverage](https://img.shields.io/codecov/c/github/jacebrowning/pomace)
](https://codecov.io/gh/jacebrowning/pomace)
[![PyPI License](https://img.shields.io/pypi/l/pomace.svg)](https://pypi.org/project/pomace)
[![PyPI Version](https://img.shields.io/pypi/v/pomace.svg?label=version)](https://pypi.org/project/pomace)
[![PyPI Downloads](https://img.shields.io/pypi/dm/pomace.svg?color=orange)](https://pypistats.org/packages/pomace)


## Quick Start

Open **Terminal.app** in macOS and paste:

```shell
python3 -m pip install --upgrade pomace && python3 -m pomace run
```

or if you have Homebrew:

```shell
brew install pipx; pipx run --no-cache pomace run
```

## Full Demo

If you're planning to run Pomace multiple times, install it with [pipx](https://pipxproject.github.io/pipx/) first:

```shell
pipx install pomace
```

or get the latest version:

```shell
pipx upgrade pomace
```

Then download some site models:

```shell
pomace clone https://github.com/jacebrowning/pomace-twitter.com
```

And launch the application:

```shell
pomace run twitter.com
```

# Usage

Install this library directly into an activated virtual environment:

```shell
pip install pomace
```

or add it to your [Poetry](https://poetry.eustace.io/) project:

```shell
poetry add pomace
```
