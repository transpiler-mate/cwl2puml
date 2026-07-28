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

import time
from datetime import datetime
from enum import Enum, auto
from http import HTTPStatus
from io import StringIO
from pathlib import Path

import click
import requests
from cwl_loader import load_cwl_from_location
from loguru import logger
from plantuml import deflate_and_encode

from . import DiagramType, to_puml


class ImageFormat(Enum):
    PNG = auto()
    SVG = auto()


@click.command(context_settings={"show_default": True})
@click.argument("workflow", required=True)
@click.option(
    "--workflow-id", required=True, type=click.STRING, help="ID of the main Workflow"
)
@click.option(
    "--diagrams",
    required=False,
    type=click.Choice(DiagramType, case_sensitive=False),
    default=[diagram_type.name.lower() for diagram_type in list(DiagramType)],
    multiple=True,
    help="The PlantUML diagram to serialize (all the supported kinds, by default)",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    required=True,
    help="Output directory path",
)
@click.option(
    "--convert-image",
    required=False,
    type=click.BOOL,
    is_flag=True,
    default=False,
    help="Flag to ton on/off the image generation ",
)
@click.option(
    "--puml-server",
    required=False,
    type=click.STRING,
    default="uml.planttext.com",
    help="The host of a PlantUML as a service server",
)
@click.option(
    "--image-format",
    required=False,
    type=click.Choice(ImageFormat, case_sensitive=False),
    default=ImageFormat.PNG,
    help="The output image format of the PlantUML diagram",
)
def main(
    workflow: str,
    workflow_id: str,
    diagrams: list[DiagramType],
    output: Path,
    convert_image: bool,
    puml_server: str,
    image_format: ImageFormat,
):
    """
    Converts a CWL, given its document model, to a PlantUML diagram.

    Args:
        `workflow` (`str`): The CWL workflow file (it can be an URL or a file on the File System)
        `workflow-id` (`str`): The ID of the main Workflow to render
        `output` (`Path`): The output file where streaming the PlantUML diagram
        `convert_image` (`bool`): Flag to ton on/off the image generation (on, by default)
        `puml_server` (`str`): The host of a PlantUML as a service server (uml.planttext.com by default)
        `image_format` (`ImageFormat`): The output image format of the PlantUML diagram ('png' by default)

    Returns:
        `None`: none
    """
    start_time = time.time()

    cwl_document = load_cwl_from_location(path=workflow)

    logger.info(
        "------------------------------------------------------------------------"
    )

    output.mkdir(parents=True, exist_ok=True)

    for diagram_type in diagrams:
        logger.info(f"Converting to {diagram_type.name.lower()} PlantUML diagram...")
        out = StringIO()
        try:
            to_puml(
                cwl_document=cwl_document,
                workflow_id=workflow_id,
                diagram_type=diagram_type,
                output_stream=out,
            )

            target = Path(output, f"{diagram_type.name.lower()}.puml")

            clear_output = out.getvalue()
            logger.info(
                f"Saving PlantUML {diagram_type.name.lower()} diagram to {target}..."
            )

            with target.open("w") as f:
                f.write(clear_output)

            logger.success(
                f"PlantUML {diagram_type.name.lower()} diagram successfully dumped to {target}!"
            )

            if convert_image:
                logger.info(
                    f"Converting PlantUML {diagram_type.name.lower()} diagram to '{image_format.name.lower()}'..."
                )

                encoded = deflate_and_encode(clear_output)
                diagram_url = f"https://{puml_server}/plantuml/{image_format.name.lower()}/{encoded}"
                response = requests.get(diagram_url, timeout=30)
                if HTTPStatus.OK.value == response.status_code:
                    target = Path(
                        output,
                        f"{diagram_type.name.lower()}.{image_format.name.lower()}",
                    )
                    logger.info(
                        f"Saving PlantUML {diagram_type.name.lower()} {image_format.name.lower()} image to {target}..."
                    )

                    with target.open("wb") as f:
                        f.write(response.content)

                    logger.success(
                        f"PlantUML {diagram_type.name.lower()} {image_format.name.lower()} image successfully dumped to {target}!"
                    )
                else:
                    logger.error(
                        f"Impossible to render {diagram_type.name.lower()} {image_format.name.lower()} image, {puml_server} server replied: {response.status_code} {response.reason}"
                    )
                    logger.error(f"Deflated and encoded PlantUML Diagram: {encoded}")
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while converting to {diagram_type.name.lower()} PlantUML diagram: {e}"
            )

    end_time = time.time()

    logger.info(f"Total time: {end_time - start_time:.4f} seconds")
    logger.info(
        f"Finished at: {datetime.fromtimestamp(end_time).isoformat(timespec='milliseconds')}"
    )
