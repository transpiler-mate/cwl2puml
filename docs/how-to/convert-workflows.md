# Convert workflows from the command line

Use this guide with an existing CWL document accepted by the transpiler-mate runtime.

## Install the plugin

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

## Select workflows and diagrams

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

For defaults and file locations, see the [plugin reference](../reference/plugin.md).
