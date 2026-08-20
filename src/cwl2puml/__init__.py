# Copyright 2025 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import re
import time
from collections.abc import Mapping
from datetime import datetime
from enum import Enum, auto
from importlib.metadata import PackageNotFoundError, version
from types import UnionType
from typing import Any, TextIO, Union, get_args, get_origin

from cwl2ogc import BaseCWLtypes2OGCConverter
from cwl_loader.utils import assert_connected_graph, assert_process_contained, to_index
from cwl_utils.parser import Process
from jinja2 import Environment, PackageLoader, select_autoescape


def _a_string(typ: Any) -> bool:
    return isinstance(typ, str)


def _a_list(typ: Any) -> bool:
    return isinstance(typ, list)


def _an_enum(typ: Any) -> bool:
    return hasattr(typ, "symbols")


def _to_camel_case(value: str) -> str:
    parts = re.split(r"[-_]+", value.strip())
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def _get_uri_split_part(uri: str, split_char: str) -> str:
    return uri.split(split_char)[-1]


def get_uri_anchor(uri: str) -> str:
    return _get_uri_split_part(uri, "#")


def get_uri_last_part(uri: str) -> str:
    return _get_uri_split_part(uri, "/")


class DiagramType(Enum):
    """The supported PlantUML diagram types"""

    ACTIVITY = auto()
    """Represents the PlantUML `activity' diagram"""
    COMPONENT = auto()
    """Represents the PlantUML `components' diagram"""
    CLASS = auto()
    """Represents the PlantUML `class' diagram"""
    SEQUENCE = auto()
    """Represents the PlantUML `sequence' diagram"""
    STATE = auto()
    """Represents the PlantUML `state' diagram"""
    OGC_PROCESSES_INPUTS = auto()
    """Represents the PlantUML `JSON' diagram for OGC API Processes - Process description inputs"""
    OGC_PROCESSES_OUTPUTS = auto()
    """Represents the PlantUML `JSON' diagram for OGC API Processes - Process description outputs"""


# START custom built-in functions to simplify the CWL rendering

translation = str.maketrans(
    {
        "-": "_",
        "/": "_",
        ".": "_",
    }
)


def _to_puml_name(identifier: str) -> str:
    return identifier.translate(translation)


def _type_to_ref(id: str, typ: Any) -> str:
    if get_origin(typ) in (Union, UnionType):
        return "\n".join([_type_to_ref(id, inner_type) for inner_type in get_args(typ)])

    if _a_list(typ):
        return "\n".join([_type_to_ref(id, t) for t in typ])

    if hasattr(typ, "items"):
        return _type_to_ref(id, typ.items)

    if _an_enum(typ):
        type_str = _to_camel_case(id)
    elif isinstance(typ, str):
        type_str = typ
    elif hasattr(typ, "__name__"):
        type_str = typ.__name__
    else:
        type_str = str(typ)

    return (
        f"{id} --> {get_uri_anchor(type_str)}"
        if "#" in type_str
        else f"' no need to add a {id} --> {type_str}"
    )


def _type_to_string(id: str, typ: Any) -> str:
    if get_origin(typ) in (Union, UnionType):
        return " | ".join(
            [_type_to_string(id, inner_type) for inner_type in get_args(typ)]
        )

    if _a_list(typ):
        return " | ".join([_type_to_string(id, t) for t in typ])

    if hasattr(typ, "items"):
        return f"{_type_to_string(id, typ.items)}[]"

    if _an_enum(typ):
        type_str = _to_camel_case(id)
    elif isinstance(typ, str):
        type_str = typ
    elif hasattr(typ, "__name__"):
        type_str = typ.__name__
    else:
        type_str = str(typ)

    return get_uri_anchor(type_str)


def _not_single_item_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 1


def _get_value_from_str_or_single_item_list(value: Any) -> Any:
    return value[0] if isinstance(value, list) else value


def _get_version() -> str:
    try:
        return version("cwl2puml")
    except PackageNotFoundError:
        return "N/A"


def _dump_json(data: Mapping[str, Any]):
    return json.dumps(data, indent=2)


def get_ogc_inputs(process: Process):
    return _dump_json(BaseCWLtypes2OGCConverter(process).get_inputs())


def get_ogc_outputs(process: Process):
    return _dump_json(BaseCWLtypes2OGCConverter(process).get_outputs())


def _to_mapping(functions: list[Any]) -> dict[str, Any]:
    mapping: dict[str, Any] = {}

    for function in functions:
        name = function.__name__
        mapping[name[1:] if name.startswith("_") else name] = function

    return mapping


_jinja_environment = Environment(
    autoescape=select_autoescape(
        disabled_extensions=("puml",),
        default_for_string=False,
        default=False,
    ),
    loader=PackageLoader(package_name="cwl2puml"),
)

for key, value in _to_mapping(
    [_type_to_ref, _type_to_string, get_ogc_inputs, get_ogc_outputs]
).items():
    _jinja_environment.globals[key] = value

_jinja_environment.filters.update(
    _to_mapping(
        [
            get_uri_anchor,
            get_uri_last_part,
            _to_camel_case,
            _to_puml_name,
            _get_value_from_str_or_single_item_list,
        ]
    )
)
_jinja_environment.tests.update(
    _to_mapping([_an_enum, _a_list, _a_string, _not_single_item_list])
)

# END


def to_puml(
    cwl_document: Process | list[Process] | tuple[Process, ...],
    diagram_type: DiagramType,
    output_stream: TextIO,
    workflow_id: str = "main",
):
    """
    Converts a CWL, given its document model, to a PlantUML diagram.

    Args:
        `cwl_document` (`Processes`): The Processes object model representing the CWL document
        `diagram_type` (`DiagramType`): The PlantUML diagram type to render
        `output_stream` (`Stream`): The output stream where serializing the PlantUML diagram

    Returns:
        `None`: none
    """
    assert_process_contained(process=cwl_document, process_id=workflow_id)

    assert_connected_graph(cwl_document)

    index = (
        to_index(cwl_document)
        if isinstance(cwl_document, list)
        else {workflow_id: cwl_document}
    )

    template = _jinja_environment.get_template(f"{diagram_type.name.lower()}.puml")

    output_stream.write(
        template.render(
            version=_get_version(),
            timestamp=datetime.fromtimestamp(time.time()).isoformat(
                timespec="milliseconds"
            ),
            workflows=index.values(),
            workflow_id=workflow_id,
            index=index,
        )
    )
