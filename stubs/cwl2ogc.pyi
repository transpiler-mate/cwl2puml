"""Types for the cwl2ogc converter API used by the diagram renderer."""

from collections.abc import Mapping

from cwl_utils.parser import Process

class BaseCWLtypes2OGCConverter:
    def __init__(self, cwl: Process) -> None: ...
    def get_inputs(self) -> Mapping[str, object]: ...
    def get_outputs(self) -> Mapping[str, object]: ...
