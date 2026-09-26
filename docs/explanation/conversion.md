# How CWL becomes a diagram

## Loading, conversion, and rendering

Conversion starts from loaded CWL process objects. The transpiler-mate runtime
loads the source, validates application metadata, and supplies a
`TranspilerContext` containing the document and optional process ID. The plugin
selects workflows and passes the document to the diagram converter.

The Python `to_puml()` function renders a Jinja template and writes PlantUML
source to a caller-owned text stream. It does not load CWL, execute workflow
steps, create output directories, or request images. Keeping these operations
separate lets applications choose their loader, output destination, and renderer.

The plugin adds file output and optional requests to a PlantUML server. A `.puml`
file is the diagram source; PNG and SVG files are rendered views of that source.
When image conversion is enabled, the encoded diagram is sent to the configured
server. Source generation alone does not require that server.

## Why the complete process index matters

A workflow can reference tools and subworkflows. Templates use the document's
process index to resolve these references. Selecting a workflow ID chooses the
root diagram; it does not remove its dependencies from the index. This is why
Python callers should retain all loaded processes when constructing the mapping.

Nested workflows are particularly visible in sequence diagrams, which show
interactions within each invocation. Separate invocation aliases distinguish
multiple calls to the same subworkflow.

## Different views of the same workflow

Activity diagrams emphasize steps and control flow. Component diagrams show
connections between workflow components, while class diagrams focus on inputs,
outputs, and their types. Sequence diagrams emphasize interactions and nested
workflow calls. State diagrams show input/output dependencies.

The two OGC diagram types describe process inputs or outputs as JSON, using
`cwl2ogc` to perform the conversion. They wrap that JSON in PlantUML JSON blocks.
They are descriptions of a process interface rather than workflow execution views.

See the [diagram reference](../reference/plugin.md#supported-diagrams) for the
exact option names, or explore the [notebook](../tutorials/examples.ipynb) to
compare the five workflow views.
