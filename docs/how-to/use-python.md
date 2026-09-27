# Render diagrams and export JSON with Python

Use this guide to integrate conversion into an application with an existing CWL file.

## Render a workflow

Install the library and loader in the same environment:

```bash
pip install "cwl2puml>=0.48.0" cwl-loader
```

Load and index a CWL document before rendering it:

```python
from io import StringIO
from pathlib import Path

from cwl_loader import load_cwl_from_location
from cwl_loader.utils import to_index
from cwl2puml import DiagramType, to_puml

processes = load_cwl_from_location("workflow.cwl")
index = to_index(processes if isinstance(processes, list) else [processes])

output = StringIO()
to_puml(
    cwl_document=index,
    workflow_id="main",
    diagram_type=DiagramType.COMPONENT,
    output_stream=output,
)
Path("component.puml").write_text(output.getvalue(), encoding="utf-8")
```

`cwl_document` is a mapping of process IDs to CWL process objects, not raw YAML
or a filename. Keep the referenced tools and subworkflows in the mapping.
`workflow_id` defaults to `"main"`; choose the ID present in your loaded index.
`to_puml()` writes source to the supplied text stream and returns `None`.
The caller owns the stream and any file creation or image rendering.

## Export OGC process inputs and outputs

`get_ogc_inputs(process)` and `get_ogc_outputs(process)` return indented JSON
**strings**, using `BaseCWLtypes2OGCConverter` from `cwl2ogc`:

```python
from cwl2puml import get_ogc_inputs, get_ogc_outputs

process = index["main"]
Path("inputs.json").write_text(get_ogc_inputs(process), encoding="utf-8")
Path("outputs.json").write_text(get_ogc_outputs(process), encoding="utf-8")
```

Use `DiagramType.OGC_PROCESSES_INPUTS` or
`DiagramType.OGC_PROCESSES_OUTPUTS` with `to_puml()` to wrap these descriptions
in a PlantUML JSON diagram instead.

See the [API reference](../reference/api.md) for callable signatures.
