# code-atlas
CodeAtlas is a code-intelligence and project-mapping platform that scans source code repositories, extracts structural and semantic metadata, and emits normalized JSON artifacts that describe the codebase in a way that both machines and LLMs can understand.

## CLI usage

Analyze any project folder directly:

```bash
codeatlas <project_root>
```

Optional output directory:

```bash
codeatlas <project_root> --output-dir <output_dir>
```

If `--output-dir` is omitted, output is written to `<project_root>/atlas`.

Use the interactive selector entrypoint (for hardcoded project presets):

```bash
codeatlas-select
```

`codeatlas-select` shows configured projects, asks which one to run, and defaults output to `<selected_project_root>/atlas` unless `--output-dir` is provided.

