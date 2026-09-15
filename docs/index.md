# CWL to PlantUML

`cwl2puml` converts Common Workflow Language (CWL) workflows into PlantUML
diagrams. Use the transpiler-mate plugin for command-line conversion, or the
Python API to render a loaded CWL document to a text stream.

## Installation

Python 3.10 or later is required. For command-line use:

```bash
pip install transpiler-mate-runtime "cwl2puml>=0.48.0"
```
!!! note "cwl2puml 0.48.0"

    Since **0.48.0**, command-line conversion is provided by
    `transpiler-mate cwl2puml`. The standalone `cwl2puml` command was removed.
    The Python library remains available independently of the runtime.

## Quick start

Render all diagrams for a workflow named `main`:

```bash
transpiler-mate cwl2puml --output ./out 'workflow.cwl#main'
```

This writes seven `.puml` files under `out/main/`. Omit the source fragment to
render every workflow in the document. Images are disabled by default; add
`--convert-image --image-format svg` to request SVG images from a PlantUML
server.

See the [plugin guide](plugin.md) for options, output layout, and migration
instructions.

## Supported diagrams

| Diagram name | Content |
| --- | --- |
| `activity` | Workflow steps and control flow. |
| `component` | Workflow components and their connections. |
| `class` | Process inputs, outputs, and types. |
| `sequence` | Step interactions, including nested workflows. |
| `state` | Input/output dependencies. |
| `ogc_processes_inputs` | OGC API - Processes input descriptions as a PlantUML JSON diagram. |
| `ogc_processes_outputs` | OGC API - Processes output descriptions as a PlantUML JSON diagram. |

## Python usage

The library does not require the CLI runtime. Install `cwl2puml` and a CWL
loader for the example in the [API guide](api.md#render-a-workflow).
`to_puml()` accepts a mapping of process IDs to loaded CWL process objects and
writes to a text stream; it does not load files or render images itself.

The [example notebook](examples.ipynb) demonstrates the five workflow diagram
types. The site displays saved notebook outputs without executing the examples
during a documentation build.
