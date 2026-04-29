---
name: build-workflows-extension
description: Use when working in a CARTO Workflows extension repo (forked from workflows-extension-template) to build, scaffold, modify, validate, test, package, or deploy a Workflows extension or its components. Triggers include "create a workflows component", "add a component to this extension", "build a CARTO extension package", "write metadata.json for a component", "add a UDF", "add a stored procedure", "edit fullrun.sql / dryrun.sql", "run carto_extension.py". Activate when the working directory contains carto_extension.py + metadata.json + components/ at root.
version: 1.0.0
---

# Build a CARTO Workflows Extension

This skill guides agents through building extension packages for CARTO Workflows on **BigQuery**, **Snowflake**, and **Oracle**. It assumes you are working inside a fork of the `workflows-extension-template` repo.

## When to use this skill

You are in the right place if the repo root contains all of:
- `carto_extension.py` — the build/test/deploy CLI
- `metadata.json` — extension-level metadata
- `components/` — directory of component scaffolds (must include `components/template/`)
- `functions/` — directory of optional UDFs and stored procedures

If any of these are missing, the user is not in an extension repo — stop and ask.

## Lifecycle overview

Every change to an extension follows the same five phases. Do them in order; skipping a phase is the most common cause of bugs.

1. **Scaffold** — copy `components/template/` (or a function example) into a new folder.
2. **Metadata** — fill out the component-level `metadata.json` and add the new component name to the extension-level `metadata.json` `components` array.
3. **SQL** — edit `src/fullrun.sql` (real logic) and `src/dryrun.sql` (schema-only preview, must match fullrun's output schema exactly).
4. **Tests** — fill out `test/test.json` with at least one test case and capture fixtures.
5. **Validate, package, deploy** — `python carto_extension.py check`, then `test`, then `package` or `deploy`.

---

## Phase 1 — Scaffold

For a new component:

```bash
cp -r components/template components/<component_name>
```

For a new UDF or stored procedure, pick the runtime and copy the matching example:

```bash
cp -r functions/example_python    functions/<function_name>   # Python UDF (numpy, etc.)
cp -r functions/example_javascript functions/<function_name>  # JavaScript UDF
cp -r functions/example_sql       functions/<function_name>   # Inline SQL function
cp -r functions/example_procedure functions/<function_name>   # Stored procedure
```

Resulting component file tree:

```
components/<component_name>/
├── metadata.json              # component definition
├── src/
│   ├── dryrun.sql             # schema-only preview (zero rows)
│   └── fullrun.sql            # actual execution
└── test/
    ├── test.json              # test config
    ├── *.ndjson               # input data per test
    └── fixtures/
        └── 1.json             # expected output snapshot
```

After copying, register the new component in the extension-level `metadata.json` (top-level `components` array, must contain the folder name) and likewise register any new function under `functions`.

---

## Phase 2 — Component metadata

A minimal valid `components/<name>/metadata.json`:

```json
{
  "name": "<component_name>",
  "title": "Human title",
  "description": "What it does, one line.",
  "version": "1.0.0",
  "icon": "component_icon.svg",
  "cartoEnvVars": [],
  "inputs": [
    { "name": "input_table", "title": "Input table", "description": "...", "type": "Table" }
  ],
  "outputs": [
    { "name": "output_table", "title": "Output table", "description": "...", "type": "Table" }
  ]
}
```

The `name` field **must** match the folder name. Each input/output `name` becomes a SQL variable available in `fullrun.sql` and `dryrun.sql`.

Input types: `Table`, `Column`, `String`, `StringSql`, `Number`, `Boolean`, `Selection`, `Range`, `Json`, `GeoJson`, `GeoJsonDraw`. Generic optional props: `placeholder`, `optional`, `default`, `helper`, `advanced`, `showIf` (conditional visibility).

Deep dives:
- Full input-type cheat sheet → `references/quick-reference.md`
- Formal validator → `references/component-metadata-schema.json`
- All constraints in tabular form → `references/validation-rules.md`
- Conditional inputs example → `examples/03-conditional-inputs/`
- All input types in one example → `examples/02-multi-input-component/`

---

## Phase 3 — SQL: `fullrun.sql` and `dryrun.sql`

Every component ships two SQL files. They share a contract: **they must produce the exact same output schema** (same columns, same names, same types, same order). The CLI's `check` command enforces this.

`fullrun.sql` runs the real logic. `dryrun.sql` runs only to expose the output schema to the Workflows UI — it should return zero rows as fast as possible (use `WHERE 1 = 0`) and substitute cheap literal values for any expensive computation in `fullrun.sql` (e.g., a literal `"uuid_string"` in place of `GENERATE_UUID()`), as long as the literal has the same type as the real result.

Each input/output `name` from `metadata.json` is available as a variable in both SQL files. Variables holding table names contain the fully-qualified name; build queries with `EXECUTE IMMEDIATE '...' || input_table || '...'`.

Use the placeholder `@@workflows_temp@@` to refer to the Workflows temp dataset/schema.

Deep dives:
- SQL pattern snippets (basic augmentation, dry-run skeleton, joins) → `references/quick-reference.md`
- Heavily-annotated reference implementation → `components/template/src/fullrun.sql` and `components/template/src/dryrun.sql`
- SQL constraints (escaping, identifier rules, multi-DB caveats) → `references/validation-rules.md`
- Working end-to-end example → `examples/01-minimal-component/`

---

## Phase 4 — Tests

`test/test.json` declares one or more test cases. Each test references an input `.ndjson` data file and a fixture file under `test/fixtures/` containing the expected output. The CLI runs the component against the input, diffs the output against the fixture, and reports pass/fail.

Workflow:
1. Write `test/test.json` with at least one test case.
2. Add input data as `test/<id>.ndjson`.
3. Run `python carto_extension.py capture --component=<name>` to record the current output as the fixture (only after you've reviewed `fullrun.sql` and trust the output).
4. From then on, `python carto_extension.py test` re-runs and diffs.

Cross-database geometry comparison is handled automatically (WKT/GeoJSON normalization) by the CLI.

Deep dives:
- Test config schema and constraints → `references/validation-rules.md` (Test Configuration section)
- Working test setup → `examples/01-minimal-component/test/`

---

## Phase 5 — Validate, package, deploy

| Command | What it does |
|---|---|
| `python carto_extension.py check` | Validate metadata + structure + SQL contract. Always run before packaging. |
| `python carto_extension.py test` | Deploy to a destination, run tests, diff against fixtures. `--component=<name>` to scope. `--no-deploy` to skip redeploy. |
| `python carto_extension.py capture` | Run SQL against a live DB and write outputs as fixtures. Use after intentional logic changes. |
| `python carto_extension.py deploy --destination=<dest>` | Deploy components to a database location for manual UI testing. BigQuery: `project.dataset`. Snowflake: `DATABASE.SCHEMA`. |
| `python carto_extension.py package` | Bundle into a distributable `extension.zip`. |
| `python carto_extension.py update` | Pull the latest `carto_extension.py` and `requirements.txt` from upstream. |

Authentication:
- **BigQuery**: `gcloud auth application-default login`
- **Snowflake**: env vars `SF_ACCOUNT`, `SF_USER`, `SF_PASSWORD`
- **Oracle**: see `references/quick-reference.md`

---

## Always-do checklist before declaring done

- [ ] Component folder name matches `metadata.json` `name`.
- [ ] Extension-level `metadata.json` lists the new component in `components` (or function in `functions`).
- [ ] `dryrun.sql` and `fullrun.sql` produce identical output schemas.
- [ ] `python carto_extension.py check` exits cleanly.
- [ ] `python carto_extension.py test` passes.
- [ ] No placeholder strings (`"My Extension"`, `"Your Name"`, etc.) in metadata.
- [ ] Icons exist at the paths referenced by metadata.
- [ ] `version` bumped if changing an existing component.

---

## Common pitfalls

- **Schema mismatch between dryrun and fullrun** — the #1 cause of `check` failures. Mirror the column list and types exactly; only the *values* may differ (literals in dryrun vs. real expressions in fullrun).
- **`dryrun.sql` is slow** — drop `WHERE 1 = 0` accidentally and the dryrun runs the full query. Always include it.
- **Component `name` ≠ folder name** — silently breaks discovery.
- **Forgetting to register the component** in the extension-level `metadata.json`.
- **Trailing commas in JSON** — the schema validator and `check` will reject them.
- **Hardcoded fully-qualified table names** in SQL — always use the input/output variables.
- **Provider-specific syntax** — BigQuery, Snowflake, and Oracle differ on identifier quoting, type names, and date functions. Test against your target provider.
- **Forgetting `cartoEnvVars: []`** — required even when empty.

For the full list see `references/validation-rules.md`.

---

## Reference index

Load on demand when the agent's task hits the matching topic.

| Need | File |
|---|---|
| Five-minute end-to-end walkthrough | `references/quickstart.md` |
| Domain term definitions (FQN, dryrun, etc.) | `references/glossary.md` |
| Cheat sheet: input types, CLI flags, SQL patterns | `references/quick-reference.md` |
| Every constraint in scannable tables | `references/validation-rules.md` |
| Formal extension-level JSON Schema | `references/extension-metadata-schema.json` |
| Formal component-level JSON Schema | `references/component-metadata-schema.json` |
| Working example with tests | `examples/01-minimal-component/` |
| All input types in one example | `examples/02-multi-input-component/` |
| Conditional input visibility (`showIf`) | `examples/03-conditional-inputs/` |
| Annotated SQL reference | `../../../components/template/src/` |

For deeper conceptual reading aimed at human developers, see the `doc/` directory at the repo root (anatomy, build guide, procedure walkthrough, UDFs, icons). Not required for task completion.
