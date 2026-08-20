# Copyright 2026 Terradue
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

from enum import Enum, auto
from http import HTTPStatus
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from loguru import logger
from plantuml import deflate_and_encode
from pydantic import BaseModel, ConfigDict, Field
from transpiler_mate.api import (
    PluginExecutionError,
    PluginFailureError,
    transpiler_plugin,
)

from . import DiagramType, to_puml

if TYPE_CHECKING:
    from transpiler_mate.api import TranspilerContext


class ImageFormat(Enum):
    PNG = auto()
    SVG = auto()


class Cwl2PumlOptions(BaseModel):
    """Options accepted by the cwl2puml plugin."""

    model_config = ConfigDict(extra="forbid")

    diagrams: list[DiagramType] = Field(
        default=list(DiagramType),
        description="The PlantUML diagram to serialize (all the supported kinds, by default).",
    )

    output: Path = Field(description="Output directory path")
    convert_image: bool = Field(
        default=False, description="Flag to turn on/off the image generation."
    )
    puml_server: str = Field(
        default="uml.planttext.com",
        description="The host of a PlantUML as a service server.",
    )

    image_format: ImageFormat = Field(
        default=ImageFormat.PNG,
        description="The output image format of the PlantUML diagram.",
    )


@transpiler_plugin(
    name="cwl2puml",
    description="Converts a CWL, given its document model, to PlantUML diagram(s).",
    options_model=Cwl2PumlOptions,
)
def cwl2puml(context: TranspilerContext, options: Cwl2PumlOptions) -> None:
    """Converts a CWL, given its document model, to PlantUML diagram(s)."""

    if not context.resolved_process:
        raise PluginFailureError(
            "Please specify the The ID of the main Workflow to render via #<workflow-id>"
        )

    options.output.mkdir(parents=True, exist_ok=True)

    for diagram_type in options.diagrams:
        logger.info(f"Converting to {diagram_type.name.lower()} PlantUML diagram...")
        out = StringIO()
        to_puml(
            cwl_document=context.document,
            workflow_id=context.resolved_process.id,
            diagram_type=diagram_type,
            output_stream=out,
        )

        target = Path(options.output, f"{diagram_type.name.lower()}.puml")

        clear_output = out.getvalue()
        logger.info(
            f"Saving PlantUML {diagram_type.name.lower()} diagram to {target}..."
        )

        with target.open("w") as f:
            f.write(clear_output)

        logger.success(
            f"PlantUML {diagram_type.name.lower()} diagram successfully dumped to {target}!"
        )

        if options.convert_image:
            image_format: str = options.image_format.name.lower()

            logger.info(
                f"Converting PlantUML {diagram_type.name.lower()} diagram to '{image_format}'..."
            )

            encoded = deflate_and_encode(clear_output)
            diagram_url = (
                f"https://{options.puml_server}/plantuml/{image_format}/{encoded}"
            )
            response = requests.get(diagram_url, timeout=30)
            if HTTPStatus.OK.value == response.status_code:
                target = Path(
                    options.output,
                    f"{diagram_type.name.lower()}.{image_format}",
                )
                logger.info(
                    f"Saving PlantUML {diagram_type.name.lower()} {image_format} image to {target}..."
                )

                with target.open("wb") as f:
                    f.write(response.content)

                logger.success(
                    f"PlantUML {diagram_type.name.lower()} {image_format} image successfully dumped to {target}!"
                )
            else:
                raise PluginExecutionError(
                    f"Impossible to render {diagram_type.name.lower()} {image_format} image",
                    f"{options.puml_server} server replied: {response.status_code} {response.reason}",
                    f"Deflated and encoded PlantUML Diagram: {encoded}",
                )
