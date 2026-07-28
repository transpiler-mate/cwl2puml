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

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest import TestCase
from unittest.mock import patch

from click.testing import CliRunner
from cwl_loader import load_cwl_from_location

import cwl2puml
import cwl2puml.cli as cli
from cwl2puml import DiagramType, to_puml

if TYPE_CHECKING:
    from cwl_utils.parser import Process


class Testloading(TestCase):
    def setUp(self):
        self.graph: Process | list[Process] = load_cwl_from_location(
            path="https://raw.githubusercontent.com/eoap/application-package-patterns/refs/heads/main/cwl-workflow/pattern-1.cwl"
        )

    def _test_diagram(self, diagram_type: DiagramType):
        self.assertIsNotNone(self.graph, "Expected non null $graph, found None")
        self.assertIsInstance(
            self.graph, list, f"Expecting graph as list, found {type(self.graph)}"
        )

        out = StringIO()
        to_puml(
            cwl_document=self.graph,
            workflow_id="pattern-1",
            diagram_type=diagram_type,
            output_stream=out,
        )
        puml_output = out.getvalue()

        self.assertIsNotNone(
            puml_output,
            "Expected non null PlantUML text for {diagram_type.name()}, found None",
        )
        self.assertGreater(
            len(puml_output),
            0,
            "Expected non empty PlantUML text for {diagram_type.name()}",
        )

    def test_components_diagram(self):
        self._test_diagram(DiagramType.COMPONENT)

    def test_class_diagram(self):
        self._test_diagram(DiagramType.CLASS)

    def test_sequence_diagram(self):
        self._test_diagram(DiagramType.SEQUENCE)

    def test_state_diagram(self):
        self._test_diagram(DiagramType.STATE)

    def test_activity_diagram(self):
        self._test_diagram(DiagramType.ACTIVITY)


class TestHelpers(TestCase):
    def test_to_puml_name(self):
        self.assertEqual(cwl2puml._to_puml_name("a-b/c"), "a_b_c")

    def test_jinja_environment_registers_get_uri_anchor_filter(self):
        self.assertIs(
            cwl2puml._jinja_environment.filters["get_uri_anchor"],
            cwl2puml.get_uri_anchor,
        )

    def test_type_to_string_with_union(self):
        rendered = cwl2puml._type_to_string("test_id", str | int)
        self.assertEqual(rendered, "str | int")

    def test_type_to_string_with_list(self):
        rendered = cwl2puml._type_to_string("test_id", ["File", "Directory"])
        self.assertEqual(rendered, "File | Directory")

    def test_type_to_string_with_array_like_object(self):
        array_like = type("ArrayLike", (), {"items": "File"})()
        self.assertEqual(cwl2puml._type_to_string("test_id", array_like), "File[]")

    def test_type_to_string_with_enum_like_object(self):
        enum_like = type(
            "EnumLike",
            (),
            {"symbols": ["https://example.test/schema#A", "B"]},
        )()
        self.assertEqual(cwl2puml._type_to_string("test_id", enum_like), "TestId")

    def test_type_to_string_with_named_type(self):
        self.assertEqual(cwl2puml._type_to_string("test_id", int), "int")

    def test_type_to_string_with_fallback_object(self):
        rendered = cwl2puml._type_to_string("test_id", object())
        self.assertIn("object object", rendered)

    def test_not_single_item_list(self):
        self.assertTrue(cwl2puml._not_single_item_list(["a", "b"]))
        self.assertFalse(cwl2puml._not_single_item_list(["a"]))
        self.assertFalse(cwl2puml._not_single_item_list("a"))

    def test_get_value_from_str_or_single_item_list(self):
        self.assertEqual(cwl2puml._get_value_from_str_or_single_item_list(["a"]), "a")
        self.assertEqual(cwl2puml._get_value_from_str_or_single_item_list("a"), "a")

    def test_get_version_returns_na_when_package_is_missing(self):
        with patch("cwl2puml.version", side_effect=PackageNotFoundError):
            self.assertEqual(cwl2puml._get_version(), "N/A")

    def test_to_mapping_uses_trimmed_function_names(self):
        mapping = cwl2puml._to_mapping(
            [cwl2puml._to_puml_name, cwl2puml._not_single_item_list]
        )

        self.assertEqual(mapping["to_puml_name"], cwl2puml._to_puml_name)
        self.assertEqual(
            mapping["not_single_item_list"], cwl2puml._not_single_item_list
        )

    def test_to_puml_renders_single_process_documents(self):
        fake_document = object()
        fake_template = type(
            "FakeTemplate",
            (),
            {
                "render": lambda self, **kwargs: (
                    f"{kwargs['workflow_id']}|{kwargs['version']}"
                )
            },
        )()
        output = StringIO()

        with (
            patch("cwl2puml.assert_process_contained") as assert_process_contained,
            patch("cwl2puml.assert_connected_graph") as assert_connected_graph,
            patch("cwl2puml._get_version", return_value="1.2.3"),
            patch.object(
                cwl2puml._jinja_environment, "get_template", return_value=fake_template
            ),
        ):
            cwl2puml.to_puml(
                cwl_document=fake_document,
                workflow_id="main",
                diagram_type=DiagramType.COMPONENT,
                output_stream=output,
            )

        assert_process_contained.assert_called_once_with(
            process=fake_document, process_id="main"
        )
        assert_connected_graph.assert_called_once_with(fake_document)
        self.assertEqual(output.getvalue(), "main|1.2.3")

    def test_sequence_diagram_qualifies_reused_subworkflow_aliases(self):
        command = SimpleNamespace(id="tool", class_="CommandLineTool")
        shared_workflow = SimpleNamespace(
            id="shared",
            class_="Workflow",
            label=None,
            inputs=[SimpleNamespace(id="sub_in")],
            outputs=[],
            steps=[
                SimpleNamespace(
                    id="run-tool",
                    run="#tool",
                    in_=[
                        SimpleNamespace(
                            id="leaf_in",
                            source="sub_in",
                            pickValue=None,
                        )
                    ],
                    out=["leaf_out"],
                    when=None,
                    scatter=None,
                    scatterMethod=None,
                )
            ],
        )
        root_workflow = SimpleNamespace(
            id="main",
            class_="Workflow",
            label=None,
            inputs=[SimpleNamespace(id="root_input")],
            outputs=[],
            steps=[
                SimpleNamespace(
                    id="call-a",
                    run="#shared",
                    in_=[
                        SimpleNamespace(
                            id="sub_in",
                            source="root_input",
                            pickValue=None,
                        )
                    ],
                    out=[],
                    when=None,
                    scatter=None,
                    scatterMethod=None,
                ),
                SimpleNamespace(
                    id="call-b",
                    run="#shared",
                    in_=[
                        SimpleNamespace(
                            id="sub_in",
                            source="root_input",
                            pickValue=None,
                        )
                    ],
                    out=[],
                    when=None,
                    scatter=None,
                    scatterMethod=None,
                ),
            ],
        )
        output = StringIO()

        with (
            patch("cwl2puml.assert_process_contained") as assert_process_contained,
            patch("cwl2puml.assert_connected_graph") as assert_connected_graph,
            patch(
                "cwl2puml.to_index",
                return_value={
                    "main": root_workflow,
                    "shared": shared_workflow,
                    "tool": command,
                },
            ),
        ):
            cwl2puml.to_puml(
                cwl_document=[root_workflow, shared_workflow, command],
                workflow_id="main",
                diagram_type=DiagramType.SEQUENCE,
                output_stream=output,
            )

        assert_process_contained.assert_called_once_with(
            process=[root_workflow, shared_workflow, command], process_id="main"
        )
        assert_connected_graph.assert_called_once_with(
            [root_workflow, shared_workflow, command]
        )

        rendered = output.getvalue()
        self.assertIn(
            'control "step: call-a\\nWorkflow: shared" as main_or__call_a_or',
            rendered,
        )
        self.assertIn(
            'control "step: call-b\\nWorkflow: shared" as main_or__call_b_or',
            rendered,
        )
        self.assertIn(
            'participant "step: run-tool\\nCommandLineTool: tool" as '
            "main_or__call_a_or__run_tool",
            rendered,
        )
        self.assertIn(
            'participant "step: run-tool\\nCommandLineTool: tool" as '
            "main_or__call_b_or__run_tool",
            rendered,
        )


class TestCli(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_main_writes_puml_output(self):
        with (
            TemporaryDirectory() as tmpdir,
            patch("cwl2puml.cli.load_cwl_from_location", return_value=object()),
            patch("cwl2puml.cli.to_puml") as to_puml_mock,
        ):
            target = Path(tmpdir, "component.puml")
            to_puml_mock.side_effect = (
                lambda cwl_document, workflow_id, diagram_type, output_stream: (
                    output_stream.write("@startuml\n@enduml\n")
                )
            )

            result = self.runner.invoke(
                cli.main,
                [
                    "workflow.cwl",
                    "--workflow-id",
                    "main",
                    "--diagrams",
                    "component",
                    "--output",
                    tmpdir,
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue(target.exists())
            self.assertIn("@startuml", target.read_text())

    def test_main_writes_image_output_when_requested(self):
        response = type(
            "Response", (), {"status_code": 200, "content": b"svg-data", "reason": "OK"}
        )()

        with (
            TemporaryDirectory() as tmpdir,
            patch("cwl2puml.cli.load_cwl_from_location", return_value=object()),
            patch("cwl2puml.cli.to_puml") as to_puml_mock,
            patch(
                "cwl2puml.cli.deflate_and_encode", return_value="encoded-diagram"
            ) as encode_mock,
            patch("cwl2puml.cli.requests.get", return_value=response) as get_mock,
        ):
            target = Path(tmpdir, "component.svg")
            to_puml_mock.side_effect = (
                lambda cwl_document, workflow_id, diagram_type, output_stream: (
                    output_stream.write("@startuml\n@enduml\n")
                )
            )

            result = self.runner.invoke(
                cli.main,
                [
                    "workflow.cwl",
                    "--workflow-id",
                    "main",
                    "--diagrams",
                    "component",
                    "--output",
                    tmpdir,
                    "--convert-image",
                    "--image-format",
                    "svg",
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            encode_mock.assert_called_once()
            get_mock.assert_called_once_with(
                "https://uml.planttext.com/plantuml/svg/encoded-diagram", timeout=30
            )
            self.assertEqual(target.read_bytes(), b"svg-data")

    def test_main_skips_image_file_on_render_error(self):
        response = type(
            "Response",
            (),
            {"status_code": 500, "content": b"", "reason": "Server Error"},
        )()

        with (
            TemporaryDirectory() as tmpdir,
            patch("cwl2puml.cli.load_cwl_from_location", return_value=object()),
            patch("cwl2puml.cli.to_puml") as to_puml_mock,
            patch("cwl2puml.cli.deflate_and_encode", return_value="encoded-diagram"),
            patch("cwl2puml.cli.requests.get", return_value=response),
        ):
            target = Path(tmpdir, "component.png")
            to_puml_mock.side_effect = (
                lambda cwl_document, workflow_id, diagram_type, output_stream: (
                    output_stream.write("@startuml\n@enduml\n")
                )
            )

            result = self.runner.invoke(
                cli.main,
                [
                    "workflow.cwl",
                    "--workflow-id",
                    "main",
                    "--diagrams",
                    "component",
                    "--output",
                    tmpdir,
                    "--convert-image",
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertFalse(target.exists())

    def test_main_catches_conversion_exceptions(self):
        with (
            TemporaryDirectory() as tmpdir,
            patch("cwl2puml.cli.load_cwl_from_location", return_value=object()),
            patch("cwl2puml.cli.to_puml", side_effect=RuntimeError("boom")),
        ):
            target = Path(tmpdir, "component.puml")
            result = self.runner.invoke(
                cli.main,
                [
                    "workflow.cwl",
                    "--workflow-id",
                    "main",
                    "--diagrams",
                    "component",
                    "--output",
                    tmpdir,
                ],
            )

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertFalse(target.exists())
