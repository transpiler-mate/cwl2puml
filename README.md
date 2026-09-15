# cwl2puml

[![PyPI - Version](https://img.shields.io/pypi/v/cwl2puml.svg)](https://pypi.org/project/cwl2puml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cwl2puml.svg)](https://pypi.org/project/cwl2puml)

`cwl2puml` converts [Common Workflow Language](https://www.commonwl.org/) workflows into [PlantUML](https://plantuml.com/) diagrams.

It provides a Python API and a transpiler-mate plugin that write PlantUML source
and optionally render PNG or SVG images through a PlantUML server.

## Supported Diagrams

`activity`, `component`, `class`, `sequence`, `state`,
`ogc_processes_inputs`, and `ogc_processes_outputs`.

## Requirements

- Python `>=3.10`

### Local quality checks

Install [Hatch](https://hatch.pypa.io/) and [Taskfiles](https://taskfile.dev/docs/guide) and then install the Git hook:

```console
task quality:pre-commit:install
```

Every commit runs Ruff (including the configured McCabe complexity limit),
Ruff formatting, mypy checks, Bandit security checks, and the pytest suite.
Run the complete hook explicitly with:

```console
task quality:pre-commit:run
```

## Installation

For command-line use, install the runtime and plugin together:

```bash
pip install transpiler-mate-runtime "cwl2puml>=0.48.0"
```

For the Python library alone, use `pip install cwl2puml`. To install the current
checkout, use `pip install .`.

## CLI Usage

> [!NOTE]
> Since release **0.48.0**, `cwl2puml` is a transpiler-mate plugin.
> The standalone command was removed; use `transpiler-mate cwl2puml`.
> The Python library remains available.

```bash
transpiler-mate cwl2puml --help
transpiler-mate cwl2puml --output ./out 'workflow.cwl#main'
```

Omit `#main` to render all workflows. Select diagram types by repeating
`--diagrams`, and optionally request images:

```bash
transpiler-mate cwl2puml \
  --diagrams component \
  --diagrams sequence \
  --output ./out \
  --convert-image \
  --image-format svg \
  'workflow.cwl#main'
```

## Output

The plugin writes `<output>/<workflow.id>/<diagram>.puml`, plus `.png` or `.svg`
files when image conversion is enabled. The default output directory is
`./docs`; images are disabled by default. All seven diagram types are selected
unless `--diagrams` is supplied.

See the [plugin guide](docs/plugin.md) for all options and migration details,
and the [API guide](docs/api.md) for Python usage.

## Development

Install Hatch with `pip install hatch`, then run the test matrix:

```bash
hatch run test:test
```

Run coverage:

```bash
hatch run test:test-cov
```

Format the code:

```bash
hatch run dev:lint
```

Run Ruff fixes:

```bash
hatch run dev:check
```

## Documentation

Project documentation: https://Terradue.github.io/cwl2puml/

To preview the documentation locally, use an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install mkdocs mkdocs-mermaid2-plugin mkdocs-jupyter "mkdocstrings[python]" pymdown-extensions
mkdocs serve
```

Run `mkdocs build --strict` to validate the documentation. Notebook pages use
their saved outputs; regenerate those outputs in Jupyter when updating examples.

## Contributing

Open an issue at https://github.com/Terradue/cwl2puml/issues if you find a bug or want to propose a change.

## License

[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%20License%202.0-blue)](https://www.apache.org/licenses/LICENSE-2.0)
