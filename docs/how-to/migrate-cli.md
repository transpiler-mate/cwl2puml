# Migrate from the standalone CLI

Since cwl2puml 0.48.0, command-line conversion is provided by the
transpiler-mate runtime. The Python library remains available independently.

- Install the runtime alongside the plugin and replace `cwl2puml` with
  `transpiler-mate cwl2puml`.
- Replace `--workflow-id main` with a source fragment: `'workflow.cwl#main'`.
- Use `--convert-image` to enable images or `--no-convert-image` to disable them;
  do not pass `yes` or `no` after the flag.
- Update output consumers to include the workflow subdirectory.
- All seven diagram types are selected by default, including the two OGC types.

Verify the new invocation with `transpiler-mate cwl2puml --help`, then follow
the [conversion guide](convert-workflows.md) to render your existing workflow.
