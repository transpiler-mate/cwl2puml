# Using the transpiler-mate plugin

!!! note "Available since cwl2puml 0.48.0"

    Since **0.48.0**, command-line conversion is provided by
    `transpiler-mate cwl2puml`. The standalone `cwl2puml` command was removed.
    The Python library remains available independently of the runtime.

The plugin renders CWL workflows as PlantUML source, with optional PNG or SVG
images. It also supports PlantUML JSON diagrams of OGC API - Processes inputs
and outputs.

## Installation

Install the runtime and plugin in the same Python environment (Python 3.10 or
later):

```bash
pip install transpiler-mate-runtime "cwl2puml>=0.48.0"
```

The plugin depends on `transpiler-mate-api`. The separate
`transpiler-mate-runtime` package provides the command and discovers installed
plugins automatically.

```bash
transpiler-mate --help
transpiler-mate cwl2puml --help
```

## Convert a CWL document

Render all supported diagrams for every workflow in a document:

```bash
transpiler-mate cwl2puml --output ./out workflow.cwl
```

Select one workflow using a source fragment, and repeat `--diagrams` to select
diagram types:

```bash
transpiler-mate cwl2puml \
  --diagrams component \
  --diagrams sequence \
  --output ./out \
  'workflow.cwl#main'
```

The runtime loads the source and supplies the document and optional process ID.
The plugin selects `Workflow` processes; a fragment restricts conversion to the
selected workflow. Tools can appear within workflow diagrams but are not
rendered as separate top-level targets by the plugin.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `--diagrams NAME` | All seven types | Repeat to select multiple diagram types. |
| `--output PATH` | `./docs` | Output directory. |
| `--convert-image / --no-convert-image` | Disabled | Render images through a PlantUML server. |
| `--puml-server HOST` | `uml.planttext.com` | Server hostname, without a URL scheme or path. |
| `--image-format NAME` | `png` | Image format: `png` or `svg`. |

Diagram names are `activity`, `component`, `class`, `sequence`, `state`,
`ogc_processes_inputs`, and `ogc_processes_outputs`. Enum choices are
case-insensitive in the runtime CLI.

Source loading and application metadata validation happen in the runtime before
conversion. See the runtime's help for shared options and source requirements.

## Render images

```bash
transpiler-mate cwl2puml \
  --diagrams component \
  --output ./out \
  --convert-image \
  --image-format svg \
  --puml-server uml.planttext.com \
  'workflow.cwl#main'
```

Image conversion sends the encoded PlantUML source to
`https://<host>/plantuml/<format>/<encoded-diagram>`. Each request has a
30-second timeout. PlantUML source is written before the image request; a
rendering failure raises a plugin execution error and can leave source files
and earlier outputs on disk.

## Generated output

Files are written under `<output>/<workflow.id>/`, using the workflow ID
supplied by the runtime. For a workflow named `main`, selecting `component` and
`sequence` with SVG conversion produces:

```text
out/
└── main/
    ├── component.puml
    ├── component.svg
    ├── sequence.puml
    └── sequence.svg
```

Missing directories are created and existing files with the same names are
overwritten. Unselected files in the output directory are retained.

The OGC diagram types write `ogc_processes_inputs.puml` and
`ogc_processes_outputs.puml`, containing JSON inside PlantUML
`@startjson` / `@endjson` blocks. They do not create a `processes.json` file.
For JSON strings without PlantUML wrappers, use the
[Python I/O helpers](api.md#ogc-process-io).

## Migrating from the former CLI

- Install the runtime alongside the plugin and replace `cwl2puml` with
  `transpiler-mate cwl2puml`.
- Replace `--workflow-id main` with a source fragment: `'workflow.cwl#main'`.
- Use `--convert-image` to enable images or `--no-convert-image` to disable them;
  do not pass `yes` or `no` after the flag.
- Update output consumers to include the workflow subdirectory.
- All seven diagram types are selected by default, including the two OGC types.

## Plugin registration

The package declares this entry point:

```toml
[project.entry-points."transpiler_mate.plugins"]
cwl2puml = "cwl2puml.plugin:cwl2puml"
```

The plugin validates options with `Cwl2PumlOptions` and receives a
`TranspilerContext` from the runtime. See the [API reference](api.md) for the
registration and options model.
