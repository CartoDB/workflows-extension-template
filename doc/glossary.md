---
title: Glossary
description: Definitions of all domain terms used in CARTO Workflows extension development
version: 1.0.0
last-updated: 2025-01-27
depends-on: []
tags: [reference, glossary, terminology]
---

# Glossary

Comprehensive definitions of terms used throughout the CARTO Workflows extension documentation.

## A

### Analytics Toolbox
CARTO's collection of spatial analysis functions available in BigQuery, Snowflake, and other data warehouses. Components may use these functions.

### Advanced Options
Input parameters marked with `"advanced": true` appear collapsed under an "Advanced options" section in the Workflows UI.

## C

### CARTO Environment Variables (cartoEnvVars)
System-provided variables automatically injected into components at runtime. Examples: `analyticsToolboxDataset`, `apiBaseUrl`, `accessToken`. Declared in component metadata as an array (can be empty).

### Component
A single operation or transformation in a Workflow. Each component has its own folder containing metadata, SQL logic, tests, and documentation. Components receive inputs, perform operations, and produce outputs.

### Component Metadata
The `metadata.json` file within each component folder that defines the component's name, inputs, outputs, icon, and configuration options.

## D

### Data Type
The type of data a column contains. Used in `Column` inputs to filter which columns users can select. Valid values: `string`, `number`, `boolean`, `geography`, `timestamp`, `date`.

### Deploy
The process of installing an extension's stored procedures directly into a data warehouse for development/testing, bypassing the packaging step. Uses `python carto_extension.py deploy --destination=...`.

### Dry Run
A schema-only execution of a component that returns zero rows but with the correct output table structure. Workflows uses dry runs to preview schemas before full execution. Implemented in `dryrun.sql`.

## E

### Extension
A package containing one or more related components that can be installed into CARTO Workflows. Defined by root-level `metadata.json` and a `components/` folder.

### Extension Metadata
The `metadata.json` file in the repository root that defines extension-level properties: name, version, author, provider, and list of included components.

### External Reference
An optional link in component metadata pointing to external documentation (e.g., API docs, algorithm papers).

## F

### Fixture
Expected test output stored in JSON format. Created by the `capture` command and used by the `test` command to verify component behavior hasn't changed. Located in `components/<name>/test/fixtures/`.

### FQN (Fully Qualified Name)
A complete table reference including project, dataset, and table name. Format: `project.dataset.table` (BigQuery) or `DATABASE.SCHEMA.TABLE` (Snowflake). Components receive FQN table names when executed via the Workflows UI.

### Full Run
The actual execution mode of a component that processes data and produces results. Implemented in `fullrun.sql`.

## G

### Generic Input Options
Properties applicable to all input types: `placeholder`, `optional`, `default`, `helper`, `advanced`, `showIf`. These control UI behavior and validation.

### Geography
A spatial data type representing points, lines, polygons, or other geometries. Used in geospatial components.

## H

### Helper Text
Explanatory text displayed in a tooltip next to an input field. Defined by the `helper` property in input metadata.

## I

### Icon
SVG image representing an extension or component in the UI. Extensions use 80x80px icons (8px safe area). Components use 40x40px icons (4px safe area). Stored in the `icons/` folder.

### Industry
Category for organizing extensions (e.g., "Retail", "Logistics", "Finance"). Specified in extension metadata.

### Input
A parameter that a component receives from the user or from upstream components. Defined in the `inputs` array of component metadata. Types include: Table, Column, String, Number, Selection, etc.

### Input Type
The category of data an input accepts, determining its UI rendering and validation. See [Input Types](#input-types) section below.

## J

### JSON Schema
A formal specification defining the structure and validation rules for JSON files. This repository provides schemas for extension and component metadata in `/doc/reference/`.

## M

### Metadata
Configuration files (`metadata.json`) that define properties of extensions and components. Validated against JSON Schemas.

### Mode
Property that changes how an input is rendered. Examples: `"mode": "multiline"` for String inputs, `"mode": "slider"` for Number inputs, `"mode": "multiple"` for Selection inputs.

### Multiline
A mode for String inputs that renders a textarea instead of a single-line input. Enabled with `"mode": "multiline"`.

## N

### NDJSON (Newline Delimited JSON)
File format for test data where each line is a separate JSON object. Used in `components/<name>/test/*.ndjson` files.

### Node
Visual representation of a component in the Workflows UI. Connected nodes form a workflow graph.

## O

### Optional
An input marked with `"optional": true` that doesn't require a value. Optional inputs can be left empty by users.

### Output
Data produced by a component, typically a table. Defined in the `outputs` array of component metadata. Currently, only Table outputs are supported.

## P

### Package
The final `.zip` file created by `python carto_extension.py package` that can be uploaded to CARTO Workflows.

### Parent
In Column inputs, the `parent` property specifies which Table input contains the columns to select from.

### Placeholder
Hint text displayed in an empty input field. Defined by the `placeholder` property.

### Placeholder Substitution
The process of replacing `@@analytics_toolbox_location@@` in stored procedure SQL with the actual Analytics Toolbox location at extension installation time. **BigQuery only**. This is a **static, one-time** substitution performed by the CARTO Workflows frontend when a user installs the extension, baking the FQN into the procedure definition. This is different from `cartoEnvVars` like `analyticsToolboxDataset`, which are **dynamically evaluated** at workflow execution time when building SQL. Each approach serves different use cases based on how the component is structured. The `.env` file is only used for local testing during development.

### Provider
The data warehouse platform an extension targets. Valid values: `"bigquery"`, `"snowflake"`, `"oracle"`. Specified in extension metadata.

### Procedure (Stored Procedure)
SQL code that implements a component's logic. Each component has two procedures: `fullrun.sql` and `dryrun.sql`.

## R

### Range
Input type that allows selecting minimum and maximum values. Generates an array like `["10", "1000"]`.

## S

### Safe Area
Padding around icon edges where no important visual elements should be placed. 8px for extension icons, 4px for component icons.

### Schema
1. (Database) The structure of a table (column names and types)
2. (JSON) A specification defining valid structure for JSON files

### Session Table
Temporary table created during stored procedure execution with a simple name (no project/dataset prefix). Components receive session table names when executed via the Workflows API or as exported stored procedures.

### ShowIf
Conditional visibility for inputs. An input with `showIf` only appears when specified conditions are met (e.g., another input has a particular value).

### Stored Procedure
See [Procedure](#procedure-stored-procedure).

## T

### Table
1. (Database) A structured dataset with rows and columns
2. (Input Type) A special input representing a connection from an upstream component in the workflow

### Template
The example component in `components/template/` that serves as a starting point for creating new components.

### Test
Automated validation that verifies a component produces expected outputs. Defined in `components/<name>/test/test.json`.

### Test Fixture
See [Fixture](#fixture).

## U

### UUID (Universally Unique Identifier)
A 128-bit identifier used as an example in the template component. Generated using `GENERATE_UUID()` in BigQuery.

## V

### Variable
In SQL procedures, inputs and outputs declared in metadata become variables accessible in `fullrun.sql` and `dryrun.sql`. For example, an input named `input_table` becomes a variable containing the table's FQN or session name.

### Version
Semantic version number (e.g., "1.0.0") specified in extension and component metadata. Format: MAJOR.MINOR.PATCH.

## W

### Workflow
A directed graph of connected components that performs data processing. Created in the CARTO Workflows UI.

### Workflows
CARTO's application for building data processing pipelines using visual, node-based interfaces.

### Workflows Temp
Default destination for temporary tables created by workflows. Typically `workflows_temp` dataset (BigQuery) or `WORKFLOWS_TEMP` schema (Snowflake).

---

## Input Types

Complete list of input types with brief descriptions:

| Type | Description | Common Properties |
|------|-------------|-------------------|
| **Table** | Input connection from upstream component | name, title, type |
| **Column** | Column selector from a parent table | name, title, parent, dataType, type |
| **String** | Single or multiline text input | name, title, type, mode? |
| **StringSql** | SQL code editor with syntax highlighting | name, title, type |
| **Number** | Numeric input or slider | name, title, type, min?, max?, mode? |
| **Boolean** | Checkbox for true/false values | name, title, type, default? |
| **Selection** | Dropdown for selecting options | name, title, type, options, mode? |
| **Range** | Min/max range selector | name, title, type |
| **Json** | JSON code editor with validation | name, title, type |
| **GeoJson** | GeoJSON code editor with validation | name, title, type |
| **GeoJsonDraw** | Interactive map for drawing geometries | name, title, type |

---

## CARTO Environment Variables

Complete list of available `cartoEnvVars`:

| Variable | Description |
|----------|-------------|
| `analyticsToolboxDataset` | Location of CARTO Analytics Toolbox functions |
| `analyticsToolboxVersion` | Version of Analytics Toolbox being used |
| `apiBaseUrl` | Base URL for CARTO API calls |
| `accessToken` | Authentication token for CARTO API |
| `dataExportDefaultGCSBucket` | Default GCS bucket for data exports |
| `bigqueryProjectId` | BigQuery project ID for the connection |
| `bigqueryRegion` | BigQuery region for the connection |
| `tempStoragePath` | Path for temporary storage |

---

## File Extensions

| Extension | Purpose |
|-----------|---------|
| `.json` | Metadata files and test fixtures |
| `.sql` | Stored procedure logic (fullrun/dryrun) |
| `.ndjson` | Test data (newline-delimited JSON) |
| `.svg` | Vector icons for extensions and components |
| `.md` | Markdown documentation |
| `.zip` | Packaged extension ready for distribution |

---

## See Also

- [Component Metadata Reference](./component_metadata.md) - Detailed input type documentation
- [Extension Metadata Reference](./extension_metadata.md) - Extension-level properties
- [JSON Schemas](./reference/) - Formal validation schemas
- [Quickstart Guide](./quickstart.md) - Get started quickly
