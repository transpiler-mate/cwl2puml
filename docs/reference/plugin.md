# Command-line plugin reference

```text
transpiler-mate cwl2puml [OPTIONS] SOURCE
```

`SOURCE` is a CWL location, optionally followed by a workflow fragment such as
`workflow.cwl#main`. Without a fragment, the plugin renders every workflow.
Only `Workflow` processes are selected as top-level targets.

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
[Python I/O helpers](../how-to/use-python.md#export-ogc-process-inputs-and-outputs).

## Plugin registration

The package declares this entry point:

```toml
[project.entry-points."transpiler_mate.plugins"]
cwl2puml = "cwl2puml.plugin:cwl2puml"
```

The plugin validates options with `Cwl2PumlOptions` and receives a
`TranspilerContext` from the runtime. See the [API reference](api.md) for the
registration and options model.

For installation and commands, see [Convert workflows](../how-to/convert-workflows.md).
