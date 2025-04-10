# icon docu

[![PyPI - Version](https://img.shields.io/pypi/v/icon-docu.svg)](https://pypi.org/project/icon-docu)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/icon-docu.svg)](https://pypi.org/project/icon-docu)

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Run](#run)
- [Project Structure](#project-structure)
- [License](#license)

## Features

- Equations per node using `.tex` files
- Custom LaTeX macros supported via `macros.tex`
- Cytoscape.js layout
- Flask backend

## Installation

```console
uv sync
uv pip install -e .
```

## Run

```bash
hatch run icon-docu
```

Open your browser at [http://localhost:5000](http://localhost:5000)

## Project Structure

```console
src/icon_docu/     # Main app source
static/            # HTML & frontend assets
tests/             # Unit tests
```

## License

`icon-docu` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
