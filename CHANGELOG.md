# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.49.0] - 2026-09-16

### Fixed

- disambiguate same name (in|out)puts, PlantUML error: `element already defined`

## [0.48.0] - 2026-09-15

### Changed

- click based custom CLI replaced by transpiler-plugin.

## [0.47.0] - 2026-07-29

### Changed

- Bumped `cwl-loader` to `0.24.0`.

## [0.46.0] - 2026-07-28

### Changed

- Bumped `cwl-loader` to `0.23.0`.
- Bumped `cwl-utils` to `0.42`.
- Bumped `click` to `8.4.2`
- Bumped `cwl2ogc` to `0.19.0`

### Removed

- `cwltool` is now useless.

## [0.45.0] - 2026-07-28

### Changed

- Bumped `cwl-loader` to `0.21.0`.

### Added

- Stronger code chekers with Ruff+McCabe & Bandit

## [0.44.0] - 2026-06-16

### Changed

- Bumped `cwl-loader` from `0.16.0` to `0.20.0`.
- Bumped `click` from `8.3.2` to `8.4.1`.
- Bumped `cwl2ogc` from `0.16.0` to `0.18.0`.

## [0.43.0] - 2026-05-11

### Added

- Activity diagrams now display the main workflow label by wrapping the workflow body in a PlantUML group.

## [0.42.0] - 2026-04-23

### Added

- Default quality checks through the shared Terradue Taskfile quality tasks.

### Changed

- Sequence diagrams now qualify reused workflow and step aliases by call site, avoiding alias reuse when the same workflow definition is invoked more than once.
- The default Taskfile task now delegates to the shared quality test and check tasks.

### Fixed

- PlantUML generation no longer crashes for workflow inputs without a source, such as default-only inputs.
- Sequence diagram rendering now handles the same definition being used from different call sites.

## [0.41.0] - 2026-04-10

### Fixed

- Upgraded `cwl2ogc` to `0.16.0` to avoid broken generated schemas from `cwl2ogc` `0.15.0`.

## [0.40.0] - 2026-04-08

### Changed

- Upgraded `cwl-loader` to `0.16.0`.

## [0.39.0] - 2026-04-08

### Changed

- Upgraded `cwl2ogc` to `0.15.0`.

## [0.38.0] - 2026-04-07

### Changed

- Upgraded `cwl2ogc` to `0.14.0`.
- Simplified the test environment dependency list to keep only test-specific dependencies.

### Fixed

- Resolved dependency conflicts in the test environment.

## [0.37.0] - 2026-04-07

### Changed

- Upgraded `click` to `8.3.2`.
- Upgraded `cwl-utils` to `0.41`.
- Upgraded `cwltool` to `3.1.20260315121657`.

## [0.36.0] - 2026-03-30

### Added

- OGC API Processes input and output JSON schema generation through `cwl2ogc`.

### Changed

- CWL records are now rendered as PlantUML records instead of PlantUML classes.
- Added the `cwl2ogc` `0.13.0` dependency.

## [0.35.0] - 2026-03-18

### Added

- SchemaDefRequirement type rendering and links in class diagrams.
- Dependabot configuration for dependency updates.

### Changed

- Upgraded `cwltool` to `3.1.20260108082145`.
- Upgraded `hatchling` to `1.29.0`.

## [0.34.0] - 2026-03-12

### Added

- Initial tagged release of `cwl2puml`, providing both a Python API and CLI for converting CWL workflows to PlantUML.
- PlantUML generation for activity, class, component, sequence, and state diagrams.
- CLI support for selecting the main workflow with `--workflow-id` and choosing one or more diagram types with `--diagrams`.
- Optional PNG and SVG image rendering through a PlantUML server.
- Rendering support for nested workflows, workflow inputs and outputs, requirements and hints, enums, scatter steps, `when` conditions, conditional branches, and graph checking.
- Documentation, notebooks, examples, unit tests, CI workflows, and MkDocs site configuration.

### Changed

- Adopted Jinja2 package-loaded templates for diagram rendering.
- Updated CWL loader and related project dependencies across the pre-tagged development history.
- Updated licensing, notice, packaging, and project metadata.
- Improved class, activity, sequence, and state diagram rendering.

### Fixed

- Guarded against null pointer errors while processing workflows.
- Fixed serialization so only the selected workflow is rendered.
- Fixed class diagram serialization errors.
- Fixed workflow output and intermediary output links.
- Fixed identifier escaping so characters such as `.` do not corrupt PlantUML identifiers.
- Fixed enum string rendering and Python doc generation issues.

[unreleased]: https://github.com/transpiler-mate/cwl2puml/compare/v0.49.0...HEAD
[0.49.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.48.0...v0.49.0
[0.48.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.47.0...v0.48.0
[0.47.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.46.0...v0.47.0
[0.46.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.45.0...v0.46.0
[0.45.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.44.0...v0.45.0
[0.44.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.43.0...v0.44.0
[0.43.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.42.0...v0.43.0
[0.42.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.41.0...v0.42.0
[0.41.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.40.0...v0.41.0
[0.40.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.39.0...v0.40.0
[0.39.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.38.0...v0.39.0
[0.38.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.37.0...v0.38.0
[0.37.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.36.0...v0.37.0
[0.36.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.35.0...v0.36.0
[0.35.0]: https://github.com/transpiler-mate/cwl2puml/compare/v0.34.0...v0.35.0
[0.34.0]: https://github.com/transpiler-mate/cwl2puml/releases/tag/v0.34.0
