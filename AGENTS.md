# AGENTS.md

## Purpose

This repository uses automated quality gates to keep Python code readable, maintainable, type-safe, documented, and easy to review.

These rules apply to all code written or modified by coding agents.

Passing tests is necessary but not sufficient. Code must also satisfy the project's linting, typing, complexity, naming, documentation, and design expectations.

## Required quality checks

Before considering a task complete, run the relevant checks defined by the repository.

At minimum:

```bash
hatch run dev:check
hatch run dev:typecheck
hatch run test:test
hatch run dev:security
```

If non-mutating CI checks are available, prefer them for final verification:

```bash
hatch run dev:format-check
hatch run dev:lint-check
hatch run dev:typecheck
hatch run dev:security
hatch run test:test
```

Do not report a task as complete when known quality checks are failing.

## Do not bypass quality gates

Do not silence a tool merely to make CI pass.

Avoid adding any of the following unless there is a clear technical reason:

```python
# noqa
# type: ignore
# pylint: disable=...
```

Also avoid weakening types with:

```python
Any
cast(...)
```

when the underlying problem can be fixed with a better interface or type definition.

If a suppression is genuinely necessary:

1. keep it as narrow as possible;
2. prefer suppressing a specific rule rather than an entire tool or category;
3. add a short explanation when the reason is not obvious.

## Ruff

Ruff is the primary linting tool.

Code must comply with the configured Ruff rules.

Do not work around Ruff by rewriting code into a technically compliant but less readable form.

When Ruff identifies a simplification or structural issue, prefer improving the implementation over suppressing the rule.

### Complexity

Cyclomatic complexity is enforced through Ruff `C901`.

Keep functions simple and focused.

When a function exceeds the configured complexity threshold:

- reduce unnecessary nesting;
- separate independent responsibilities;
- extract meaningful operations;
- simplify conditionals;
- consider replacing boolean-driven control flow with clearer domain structures.

Do not extract trivial helper functions solely to reduce the complexity number.

A refactoring should improve readability and structure, not only satisfy the metric.

## Schema-first rule

Schema-first rule: Never hand-write Python representations of OpenAPI/JSON Schema objects. Change the schema and regenerate models using the repository’s Terradue `create_models` task.

## Function and method annotations

Follow the Google Python Style Guide principles for function and method annotations, with stricter enforcement for new code in this repository.

### Public APIs must be annotated

All public functions and methods must have type annotations for:

- every parameter except `self` and `cls`;
- the return value;
- callback signatures where applicable.

Prefer:

```python
def load_document(document_id: str) -> Document | None:
    ...
```

Do not write:

```python
def load_document(document_id):
    ...
```

Public APIs must remain understandable without requiring callers to inspect the implementation.

### New and modified functions should normally be fully annotated

For new code, annotate function and method parameters and return values even when the function is private.

Prefer:

```python
def parse_interval(value: str) -> tuple[Instant | None, Instant | None]:
    ...
```

over:

```python
def parse_interval(value):
    ...
```

Annotation is especially important when code:

- is part of a public API;
- performs non-trivial logic;
- has previously caused type-related defects;
- is difficult to understand from context;
- crosses module or package boundaries;
- has reached a stable interface.

### `self` and `cls`

Do not annotate `self` or `cls` unless required for correct typing.

Prefer:

```python
class Processor:
    def process(self, document: Document) -> Result:
        ...
```

Use `Self` when the relationship between receiver and return or argument type matters:

```python
from typing import Self


class Query:
    @classmethod
    def from_text(cls, value: str) -> Self:
        ...

    def merge(self, other: Self) -> Self:
        ...
```

### `__init__`

Use `-> None` for `__init__` in this repository:

```python
class Client:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint
```

Constructor parameters must still be annotated.

### Prefer precise return types

Return annotations must describe the actual contract.

Prefer:

```python
def find_record(record_id: str) -> Record | None:
    ...
```

over:

```python
def find_record(record_id: str) -> object:
    ...
```

Avoid `Any` when a more precise type can reasonably be expressed.

### Use abstract collection types for inputs

Prefer abstract collection interfaces when a concrete implementation is not required.

```python
from collections.abc import Sequence


def process_records(records: Sequence[Record]) -> Result:
    ...
```

Prefer this over `list[Record]` when the function does not require list-specific behavior or mutation.

### Optional values must be explicit

Represent nullable values explicitly:

```python
def get_timestamp() -> datetime | None:
    ...
```

Do not rely on undocumented `None` returns.

### Avoid redundant local annotations

Do not annotate obvious locals when inference is sufficient.

Avoid:

```python
count: int = 0
name: str = record.name
```

Prefer:

```python
count = 0
name = record.name
```

Use local annotations when they clarify an otherwise ambiguous type:

```python
result: ParsedResult | None = None
```

## Google-style docstrings

Use Google-style docstrings for Python modules, public APIs, classes, and non-trivial or non-obvious functions.

Use triple double quotes:

```python
"""Docstring."""
```

Do not use single quotes for docstrings.

### Summary line

Every docstring starts with a concise summary sentence.

The summary:

- should fit on one physical line where practical;
- should end with punctuation;
- should describe what the object does, not restate its name;
- should be understandable without reading the implementation.

Prefer:

```python
def parse_interval(value: str) -> Interval:
    """Parse an ISO-style datetime interval."""
```

Avoid:

```python
def parse_interval(value: str) -> Interval:
    """parse_interval."""
```

If additional documentation follows the summary, insert a blank line.

```python
def parse_interval(value: str) -> Interval:
    """Parse an ISO-style datetime interval.

    Open interval bounds are represented using ``..``.
    """
```

### Module docstrings

Production modules should begin with a module-level docstring after the license header and before imports.

The docstring should explain the module's responsibility and, when useful, how its public API is intended to be used.

Example:

```python
"""Datetime parsing and validation utilities.

This module provides parsing and validation for instant and interval
expressions accepted by the API.
"""
```

Do not add empty or redundant module docstrings such as:

```python
"""Datetime module."""
```

Test modules do not require module docstrings unless the docstring provides useful information about unusual setup, execution requirements, external dependencies, fixtures, or test strategy.

### Function and method docstrings

A docstring is required when a function or method is:

- part of the public API;
- non-trivial in size;
- non-obvious in behavior;
- responsible for an important domain operation;
- responsible for validation with caller-visible failure conditions.

A docstring should let a caller understand how to use the function without reading its implementation.

Document caller-visible semantics, not implementation details.

Prefer:

```python
def validate_datetime(datetime_value: str) -> None:
    """Validate an instant or datetime interval.

    Args:
        datetime_value: Instant or interval expression to validate.

    Raises:
        ValueError: If the value is malformed, represents an invalid open
            instant, or contains reversed interval bounds.
    """
```

Do not write:

```python
def validate_datetime(datetime_value: str) -> None:
    """Validate datetime."""
```

### Descriptive versus imperative style

Either descriptive or imperative docstring summaries are acceptable:

```python
"""Parse a datetime interval."""
```

or:

```python
"""Parses a datetime interval."""
```

Be consistent within a file or package.

Do not mix styles arbitrarily.

### `Args`

Use an `Args:` section when parameters need explanation beyond their names and annotations.

Format:

```python
def fetch_records(
    collection_id: str,
    limit: int = 100,
) -> list[Record]:
    """Fetch records from a collection.

    Args:
        collection_id: Identifier of the collection to query.
        limit: Maximum number of records to return.
    """
```

Parameter descriptions should explain semantics, constraints, units, allowed values, or special behavior.

Do not simply repeat the type.

Avoid:

```text
Args:
    limit: An integer.
```

Prefer:

```text
Args:
    limit: Maximum number of records to return.
```

Do not document `self` or `cls`.

### `Returns`

Use a `Returns:` section when the return value needs semantic explanation.

Example:

```python
def find_record(record_id: str) -> Record | None:
    """Find a record by identifier.

    Args:
        record_id: Identifier of the requested record.

    Returns:
        The matching record, or ``None`` when no record exists.
    """
```

For a trivial return value that is already completely obvious from the name and type, a `Returns:` section may be omitted.

Do not add:

```text
Returns:
    A Record.
```

when it contributes no information beyond `-> Record`.

### Functions returning `None`

Do not add a `Returns:` section solely to state that a function returns `None`.

Prefer:

```python
def validate(value: str) -> None:
    """Validate a datetime expression.

    Raises:
        ValueError: If the expression is invalid.
    """
```

### `Raises`

Use `Raises:` for exceptions that are part of the caller-visible contract.

Example:

```python
Raises:
    ValueError: If the interval syntax is invalid or its bounds are reversed.
    FileNotFoundError: If the referenced configuration file does not exist.
```

Do not document every incidental exception that an implementation might emit.

Document exceptions callers are reasonably expected to handle or understand.

### `Yields`

Generators should use `Yields:` rather than `Returns:` to describe yielded values.

Example:

```python
def iter_records(path: Path) -> Iterator[Record]:
    """Iterate over records stored in a file.

    Args:
        path: File containing serialized records.

    Yields:
        Records in their source order.

    Raises:
        ValueError: If a serialized record is malformed.
    """
```

### Classes

Public classes require a class docstring describing their responsibility.

Example:

```python
class DatetimeParser:
    """Parse and validate datetime query expressions."""
```

When more explanation is needed:

```python
class DatetimeParser:
    """Parse and validate datetime query expressions.

    The parser supports both individual instants and bounded or open
    datetime intervals.

    Attributes:
        timezone: Default timezone used for values without an explicit zone.
    """
```

Do not merely repeat the class name.

Avoid:

```python
class DatetimeParser:
    """DatetimeParser class."""
```

### `Attributes`

Document significant public class attributes using an `Attributes:` section.

Example:

```python
class Client:
    """Client for the records API.

    Attributes:
        endpoint: Base URL of the remote API.
        timeout: Request timeout in seconds.
    """
```

Do not list private implementation details unless they are important to subclassing or intended usage.

### Constructors

Document constructor arguments in the `__init__` docstring when construction requires meaningful explanation.

Example:

```python
class Client:
    """Client for the records API."""

    def __init__(
        self,
        endpoint: str,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the client.

        Args:
            endpoint: Base URL of the records API.
            timeout: Request timeout in seconds.

        Raises:
            ValueError: If the endpoint is not an HTTP or HTTPS URL.
        """
```

Do not duplicate extensive class-level documentation in `__init__`.

### Properties

Property docstrings should describe the value, not say "Returns".

Prefer:

```python
@property
def endpoint(self) -> str:
    """The configured API endpoint."""
```

Avoid:

```python
@property
def endpoint(self) -> str:
    """Returns the configured API endpoint."""
```

### Side effects

Document significant side effects when they are not obvious from the function name and signature.

Examples include:

- mutating an input argument;
- writing files;
- deleting files;
- modifying persistent state;
- making remote requests;
- modifying environment state.

Example:

```python
def normalize_records(records: list[Record]) -> None:
    """Normalize records in place.

    Args:
        records: Records to mutate.
    """
```

### Do not document implementation details

Docstrings describe contracts and semantics.

Implementation details belong in comments close to the implementation when necessary.

Avoid docstrings such as:

```python
"""Loop over every item, append valid items to a list, then sort the list."""
```

Prefer:

```python
"""Return validated records sorted by timestamp."""
```

### Do not duplicate type annotations

Types belong in function annotations.

Avoid:

```python
def fetch(limit: int) -> list[Record]:
    """Fetch records.

    Args:
        limit (int): Number of records.

    Returns:
        list[Record]: Records.
    """
```

Prefer:

```python
def fetch(limit: int) -> list[Record]:
    """Fetch records.

    Args:
        limit: Maximum number of records to return.

    Returns:
        Records in retrieval order.
    """
```

### Short functions

Simple private helpers do not need docstrings when the name, annotations, and implementation are self-explanatory.

This is acceptable:

```python
def _normalize_name(name: str) -> str:
    return name.strip().casefold()
```

Do not add low-value documentation solely to satisfy a documentation metric:

```python
def _normalize_name(name: str) -> str:
    """Normalize name."""
    return name.strip().casefold()
```

### Test docstrings

Tests do not require docstrings when the test name clearly communicates the behavior.

Prefer:

```python
def test_rejects_reversed_datetime_interval() -> None:
    ...
```

over:

```python
def test_rejects_reversed_datetime_interval() -> None:
    """Test that reversed datetime intervals are rejected."""
    ...
```

Add a test docstring only when it explains something that cannot be reasonably expressed by the test name, such as unusual setup or an external constraint.

## Naming

Use names that describe the role or meaning of a value.

Avoid vague names such as:

```python
d
r
x
v
obj
tmp
val
res
thing
```

when a more descriptive domain name is available.

Prefer:

```python
document = load_document(path)
records = parse(document)

for record in records:
    process(record)
```

over:

```python
d = load_document(path)
r = parse(d)

for x in r:
    process(x)
```

### Single-letter variables

Single-letter names are acceptable only when the meaning is conventional and the scope is extremely small.

Examples include:

```python
for i in range(count):
    ...
```

```python
{x: normalize(x) for x in values}
```

They may also be appropriate for genuine mathematical notation or coordinates.

Do not use single-letter variables for domain concepts or values spanning multiple statements.

### Function and method names

Use `lower_snake_case`.

Names should describe behavior or intent:

```python
parse_datetime_interval()
validate_request()
load_configuration()
```

Avoid generic verbs when a more precise name is available:

```python
handle()
process()
run()
do_work()
```

These names are acceptable only when their meaning is already explicit from the surrounding abstraction.

### Avoid shadowing meaningful names

Do not use parameter or local names that unnecessarily shadow common standard-library modules, built-ins, or important domain types.

Prefer:

```python
def validate_datetime(datetime_value: str) -> None:
    ...
```

over:

```python
def validate_datetime(datetime: str) -> None:
    ...
```

Similarly avoid ambiguous names such as `type`, `id`, `json`, or `input` when a clearer domain-specific name exists.

## Type safety

The repository uses `mypy`.

All new or modified code should preserve strong typing.

Prefer explicit domain types over loosely structured values.

For example:

```python
@dataclass(frozen=True)
class ProcessingResult:
    status: Status
    items: list[Item]
```

is preferable to repeatedly passing:

```python
dict[str, Any]
```

when the data has a stable shape.

Prefer:

- dataclasses;
- enums;
- protocols;
- typed models;
- explicit return types;
- domain-specific types.

Avoid spreading `Any` through the codebase.

If an external dependency is genuinely untyped, isolate the untyped boundary rather than weakening typing across the surrounding application.

## Interfaces and boundaries

Keep module and package boundaries explicit.

Do not introduce imports that violate the existing architecture.

Before adding a dependency between modules, check how similar dependencies are handled elsewhere in the repository.

Prefer depending on stable interfaces rather than implementation details.

Do not import private or internal implementation details from another component unless the repository already establishes that pattern intentionally.

## Classes

Keep classes focused.

Avoid classes with excessive:

- instance attributes;
- public methods;
- responsibilities;
- constructor arguments.

Prefer composition over expanding a class into a general-purpose manager.

Do not create classes solely to hold one stateless function when a module-level function would be clearer.

Conversely, when several functions share a genuine invariant or stateful responsibility, represent that explicitly rather than passing loosely related values everywhere.

## Error handling

Catch the narrowest meaningful exception.

Prefer:

```python
try:
    document = repository.load(document_id)
except DocumentNotFoundError:
    ...
```

over:

```python
try:
    document = repository.load(document_id)
except Exception:
    ...
```

Do not use bare exception handlers.

Do not silently discard exceptions.

At application boundaries where catching `Exception` is intentional, preserve diagnostic information and make the boundary explicit.

## Mutable state

Minimize shared mutable state.

Avoid module-level mutable globals.

Prefer explicit data flow through function arguments and return values.

Where practical:

- prefer immutable values;
- use frozen dataclasses for immutable domain objects;
- isolate side effects;
- keep transformation functions pure.

## Data structures

Do not use generic dictionaries as informal domain models when the structure is stable and meaningful.

Avoid:

```python
def process(data: dict[str, Any]) -> dict[str, Any]:
    ...
```

when the input and output represent known concepts.

Prefer explicit types that document the contract and allow `mypy` to verify callers.

## Boolean parameters

Be cautious with boolean parameters that significantly alter behavior.

Avoid:

```python
process(document, True, False, True)
```

Prefer explicit enums, configuration objects, or separate operations when they communicate intent more clearly.

## Tests

All behavioral changes should be covered by tests where practical.

Tests should cover:

- expected behavior;
- meaningful edge cases;
- failure paths;
- regressions;
- invalid inputs when relevant.

Do not write tests only to increase coverage.

Assertions should verify meaningful behavior.

Prefer tests against public behavior rather than implementation details.

Do not duplicate production logic in tests.

## Refactoring

When modifying existing code, improve nearby code only when the change is clearly related and low risk.

Do not turn a focused task into a broad cleanup unless required.

Preserve existing public interfaces unless the task explicitly requires changing them.

Prefer incremental refactoring over large unrelated rewrites.

## Generated abstractions

Do not introduce abstractions without a concrete current use case.

Avoid:

- single-use wrapper classes;
- unnecessary factories;
- generic managers;
- speculative interfaces;
- helpers that only rename another function;
- configuration layers with no real variability.

Prefer straightforward code until a real abstraction boundary is evident.

## Comments

Comments should explain why, constraints, trade-offs, or non-obvious behavior.

Do not add comments that merely restate the code.

Useful comments explain information that cannot be inferred directly from the implementation.

## Security

Run the configured Bandit checks for relevant changes.

Do not:

- hard-code credentials;
- log secrets;
- disable certificate verification without a justified reason;
- execute untrusted input;
- deserialize untrusted data with unsafe mechanisms;
- construct shell commands through unsafe string interpolation.

Security warnings should be investigated rather than automatically suppressed.

## Dependency changes

Do not add a dependency when the standard library or an existing project dependency is sufficient.

Before adding a dependency:

1. verify that it is necessary;
2. prefer actively maintained packages;
3. avoid dependencies for trivial functionality;
4. follow the project's existing versioning policy;
5. update relevant project metadata and tests.

Do not add development tooling casually if the same check is already provided by Ruff, mypy, pytest, Bandit, or existing project tooling.

## Keep changes focused

Do not modify unrelated files.

Do not reformat unrelated code unless required by the configured formatter.

Avoid drive-by renames and unrelated refactoring.

A pull request or agent change should remain easy to review.

## Before completing a task

Review the diff and verify:

- public functions and methods have complete annotations;
- new and modified functions have appropriate annotations;
- modules have useful docstrings where required;
- public, non-trivial, and non-obvious functions have Google-style docstrings;
- docstrings describe semantics rather than implementation;
- `Args`, `Returns`, `Raises`, `Yields`, and `Attributes` are used appropriately;
- docstrings do not redundantly repeat type annotations;
- properties describe their value instead of saying "Returns";
- trivial helpers and obvious tests have not been given redundant docstrings;
- names are descriptive;
- no unnecessary one-letter variables were introduced;
- functions remain focused;
- complexity remains reasonable;
- `Any` has not been introduced unnecessarily;
- suppressions have not been added merely to pass CI;
- exception handling is appropriately narrow;
- tests cover the behavior changed;
- no unnecessary abstraction was introduced;
- unrelated code was not modified.

Then run the configured project quality checks.

## Guiding principle

Quality tools define the minimum acceptable standard, not the target.

Code can pass Ruff, mypy, Bandit, and pytest and still be difficult to maintain.

Prefer code that is:

- explicit;
- unsurprising;
- readable;
- strongly typed;
- appropriately documented;
- locally simple;
- architecturally consistent;
- easy for another developer to review and modify.


## OpenAPI and generated models

APIs are schema-first.

When a Python model represents data defined by an OpenAPI or JSON Schema document, **the schema is the source of truth**.

Do not manually recreate schema-defined models using:

```python
TypedDict
dataclass
pydantic.BaseModel
NamedTuple
```

or equivalent hand-written structures.

For example, do **not** introduce:

```python
@with_config(ConfigDict(extra="allow"))
class PointGeometry(TypedDict):
    """USGS epicentre coordinates, optionally including depth in kilometres."""

    type: str
    coordinates: list[float]
```

when `PointGeometry` is already described, or should be described, by the project's OpenAPI or JSON Schema.

### Modify the schema, not generated Python

When an API model needs to be added or changed:

1. locate the authoritative OpenAPI or JSON Schema definition;
2. make the required change in the schema;
3. regenerate the Python models using the repository's configured model-generation task;
4. update application code to use the generated model;
5. run the normal quality and test checks.

Do not make the Python representation the source of truth for an API contract.

### Use the Terradue model generator

Terradue projects use the shared `taskfile-utils` JSON tasks for model generation.

Use the repository's configured invocation of the shared `create_models` task.

The shared task is defined in:

```text
https://github.com/Terradue/taskfile-utils/blob/main/json.yaml
```

It generates Pydantic v2 models using `datamodel-code-generator`.

Do not replace this workflow with an ad-hoc code generator or handwritten models unless the repository explicitly defines a different mechanism.

Before generating models, inspect the project's `Taskfile.yml` to determine:

- the imported task namespace;
- the schema path;
- the generated model output path;
- any configured base class;
- any additional imports or custom templates.

Run the task through the repository's Taskfile rather than invoking `datamodel-codegen` manually when the task is available.

### Generated files must not be manually edited

Files produced by `create_models` are generated artifacts.

Do not manually modify generated classes to:

- rename fields;
- change types;
- add aliases;
- add validation constraints;
- change optionality;
- change enum values;
- add schema descriptions;
- change inheritance;
- alter extra-field handling.

Make the equivalent change in the source OpenAPI or JSON Schema and regenerate.

If regeneration overwrites a manual change, that is evidence that the change belongs in the schema or generator configuration.

### Preserve schema semantics

Do not simplify generated types in a way that weakens the API contract.

For example, do not replace a schema-generated model with:

```python
dict[str, Any]
```

or:

```python
TypedDict
```

merely because it makes application code shorter.

Preserve schema-defined:

- required versus optional fields;
- nullability;
- enums and literals;
- aliases;
- numeric and string constraints;
- nested objects;
- unions;
- field descriptions;
- additional-property behavior.

### Schema documentation belongs in the schema

Descriptions for schema-derived objects and fields should normally be written in the OpenAPI or JSON Schema definition.

For example, prefer defining:

```yaml
PointGeometry:
  type: object
  description: USGS epicentre coordinates, optionally including depth in kilometres.
  properties:
    type:
      type: string
    coordinates:
      type: array
      items:
        type: number
```

and regenerating the Python representation.

Do not add a handwritten Python docstring merely to compensate for a missing schema description.

The Terradue model generator is configured to propagate schema and field descriptions into generated models.

### Distinguish domain models from API models

Hand-written models remain appropriate when the type represents an internal domain concept that is **not** part of an OpenAPI or JSON Schema contract.

For example, an internal object such as:

```python
@dataclass(frozen=True)
class ProcessingContext:
    request_id: str
    attempt: int
```

may be appropriate when it exists solely inside the application.

Before creating a new `TypedDict`, dataclass, or Pydantic model, determine whether the structure belongs to:

- the API/schema contract → define it in OpenAPI/JSON Schema and generate it;
- internal application state → a hand-written domain model may be appropriate.

Do not maintain two independently defined models for the same external contract.

### Before creating a model

Before adding any new structured Python model, check:

1. Does an OpenAPI or JSON Schema already define this structure?
2. Is there an existing generated model that should be reused?
3. Should this structure be added to the schema instead?
4. Is the file being edited generated?
5. What Taskfile command regenerates the models?

Only create a hand-written model after establishing that the type is genuinely application-internal and not schema-derived.