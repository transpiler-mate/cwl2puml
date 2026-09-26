# Create your first diagram

In this tutorial, you will create a small CWL workflow and turn it into a
PlantUML component diagram using Python. You need Python 3.10 or later and a
terminal. You will generate diagram source without running the workflow.

## 1. Prepare an environment

Create an empty working directory and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "cwl2puml>=0.48.0" "cwl-loader>=0.27.0"
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

## 2. Create a workflow

Save this document as `workflow.cwl`:

```yaml
cwlVersion: v1.2
$graph:
  - class: CommandLineTool
    id: echo
    baseCommand: echo
    inputs:
      message:
        type: string
        inputBinding:
          position: 1
    outputs: []
  - class: Workflow
    id: main
    inputs:
      message: string
    outputs: []
    steps:
      greet:
        run: '#echo'
        in:
          message: message
        out: []
```

The workflow has one input, `message`, and one step, `greet`, that uses the
`echo` tool. Both processes are present in the document.

## 3. Generate diagram source

Save the following as `render.py` in the same directory:

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
print("Created component.puml")
```

Run it:

```bash
python render.py
```

After the loader messages, you should see `Created component.puml`.

## 4. Inspect the result

Open `component.puml` in a text editor. It contains `@startuml` and `@enduml`
boundaries, a workflow component named `main`, an input named `message`, and a
frame for the `greet` step. A PlantUML viewer can render this source as an image.

You have converted a local CWL document into diagram source. Continue with the
[example notebook](examples.ipynb) to explore other diagram types, or use the
[command-line guide](../how-to/convert-workflows.md) to generate images through
the plugin.
