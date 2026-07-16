# cwl2puml

[![PyPI - Version](https://img.shields.io/pypi/v/cwl2puml.svg)](https://pypi.org/project/cwl2puml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cwl2puml.svg)](https://pypi.org/project/cwl2puml)

`cwl2puml` converts [Common Workflow Language](https://www.commonwl.org/) workflows into [PlantUML](https://plantuml.com/) diagrams.

It provides a CLI that can:

- load a CWL workflow from a local path or URL
- render PlantUML source files
- optionally render PNG or SVG images through a PlantUML server

## Supported Diagrams

- `activity`
- `component`
- `class`
- `sequence`
- `state`

## Requirements

- Python `>=3.10`

## Installation

Install from the repository:

```bash
pip install .
```

For development:

```bash
pip install hatch
```

## CLI Usage

Show the CLI help:

```bash
cwl2puml --help
```

Basic example:

```bash
cwl2puml \
  https://raw.githubusercontent.com/eoap/application-package-patterns/refs/heads/main/cwl-workflow/pattern-1.cwl \
  --workflow-id pattern-1 \
  --output ./out
```

This writes one `.puml` file per diagram type into `./out`.

Generate only selected diagrams:

```bash
cwl2puml workflow.cwl \
  --workflow-id main \
  --diagrams component \
  --diagrams sequence \
  --output ./out
```

Generate SVG images through a PlantUML server:

```bash
cwl2puml workflow.cwl \
  --workflow-id main \
  --diagrams component \
  --output ./out \
  --convert-image \
  --image-format svg
```

Use a custom PlantUML server host:

```bash
cwl2puml workflow.cwl \
  --workflow-id main \
  --output ./out \
  --convert-image \
  --puml-server uml.planttext.com
```

## Output

For each selected diagram type, the CLI writes:

- `<diagram>.puml`
- optionally `<diagram>.png` or `<diagram>.svg`

## Development

Run the test matrix:

```bash
hatch run test:test-q
```

Run coverage:

```bash
hatch run test:test-cov
```

Run formatting checks:

```bash
hatch run dev:lint
```

Run Ruff fixes:

```bash
hatch run dev:check
```

## Documentation

Project documentation: https://Terradue.github.io/cwl2puml/

## Contributing

Open an issue at https://github.com/Terradue/cwl2puml/issues if you find a bug or want to propose a change.

## License

[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%20License%202.0-blue)](https://www.apache.org/licenses/LICENSE-2.0)
