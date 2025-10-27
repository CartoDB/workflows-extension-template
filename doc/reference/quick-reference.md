---
title: Quick Reference Card
description: One-page cheat sheet for building CARTO Workflows extensions
version: 1.0.0
last-updated: 2025-01-27
depends-on: []
tags: [reference, cheatsheet, quick-reference]
---

# Quick Reference Card

Fast lookup guide for common patterns and commands.

---

## Input Types at a Glance

| Type | Use For | Required Props | Value in SQL | UI Render |
|------|---------|----------------|--------------|-----------|
| **Table** | Upstream connection | name, title, type | FQN or session table name | Connection port |
| **Column** | Select column | name, title, parent, dataType, type | Column name string | Dropdown (filtered) |
| **String** | Text input | name, title, type | String | Text input |
| **StringSql** | SQL code | name, title, type | String (SQL) | Code editor |
| **Number** | Numeric value | name, title, type | Number | Number input |
| **Boolean** | True/false | name, title, type | Boolean | Checkbox |
| **Selection** | Pick from list | name, title, type, options | String or array | Dropdown |
| **Range** | Min/max values | name, title, type | Array `["min", "max"]` | Range slider |
| **Json** | JSON data | name, title, type | JSON object | Code editor |
| **GeoJson** | GeoJSON data | name, title, type | GeoJSON object | Code editor |
| **GeoJsonDraw** | Draw geometry | name, title, type | GeoJSON object | Map interface |

**Generic Options** (optional for most types): `placeholder`, `optional`, `default`, `helper`, `advanced`, `showIf`

---

## File Structure

```
extension-root/
├── metadata.json              # Extension metadata (required)
├── icons/
│   └── *.svg                  # Icons (required)
└── components/
    └── <component_name>/      # Must match metadata "name"
        ├── metadata.json      # Component metadata (required)
        └── src/
            ├── fullrun.sql    # Full execution (required)
            └── dryrun.sql     # Schema preview (required)
        └── test/              # Tests (optional but recommended)
            ├── test.json
            ├── *.ndjson
            └── fixtures/
                └── *.json
```

---

## CLI Commands

```bash
# Validate extension structure and metadata
python carto_extension.py check

# Run component tests
python carto_extension.py test
python carto_extension.py test --component=component_name

# Capture test fixtures (expected outputs)
python carto_extension.py capture
python carto_extension.py capture --component=component_name

# Deploy to data warehouse for development
python carto_extension.py deploy --destination=project.dataset       # BigQuery
python carto_extension.py deploy --destination=DATABASE.SCHEMA       # Snowflake

# Create distributable package
python carto_extension.py package

# Update script to latest version
python carto_extension.py update
```

---

## SQL Patterns

### Basic Table Augmentation
```sql
EXECUTE IMMEDIATE '''
    CREATE TABLE IF NOT EXISTS ''' || output_table || '''
    OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))
    AS SELECT
        *,                              -- Preserve input columns
        NEW_COLUMN AS new_col           -- Add computed column
    FROM ''' || input_table;
```

### Dry Run Pattern
```sql
EXECUTE IMMEDIATE '''
    CREATE TABLE IF NOT EXISTS ''' || output_table || '''
    OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))
    AS SELECT
        *,
        "literal" AS new_col            -- Use literal instead of function
    FROM ''' || input_table || '''
    WHERE 1 = 0;                        -- CRITICAL: Zero rows
''';
```

### FQN Detection
```sql
-- Check if table name is FQN or session table
CASE
    WHEN REGEXP_CONTAINS(input_table, r'\.') THEN 'FQN'
    ELSE 'session'
END
```

### String Value Escaping
```sql
-- Escape quotes in dynamic SQL
\'''' || string_value || '''\' AS col_name

-- Example: If string_value = "test", produces: 'test' in SQL
```

---

## Metadata Quick Templates

### Minimal Component
```json
{
  "name": "component_name",
  "title": "Component Title",
  "description": "What it does",
  "version": "1.0.0",
  "icon": "icon.svg",
  "cartoEnvVars": [],
  "inputs": [
    {"name": "input_table", "title": "Input", "type": "Table"}
  ],
  "outputs": [
    {"name": "output_table", "title": "Output", "type": "Table"}
  ]
}
```

### Column Input
```json
{
  "name": "column_name",
  "title": "Select Column",
  "parent": "input_table",
  "dataType": ["string", "number"],
  "type": "Column"
}
```

### Conditional Input (showIf)
```json
{
  "name": "conditional_input",
  "title": "Conditional Input",
  "type": "String",
  "showIf": [
    {"parameter": "trigger_input", "value": "trigger_value"}
  ]
}
```

---

## Naming Conventions

| Element | Pattern | Example | Invalid |
|---------|---------|---------|---------|
| Extension name | `^[a-z0-9_]+$` | `my_extension` | `My-Extension` |
| Component name | `^[a-z0-9_]+$` | `add_uuid` | `addUUID` |
| Variable name | `^[a-z0-9_]+$` | `input_table` | `inputTable` |
| Version | `^\d+\.\d+\.\d+$` | `1.0.0` | `v1.0` |

**Rule:** Always use `snake_case` (lowercase with underscores).

---

## Data Warehouse Differences

| Feature | BigQuery | Snowflake | Oracle |
|---------|----------|-----------|--------|
| Provider value | `"bigquery"` | `"snowflake"` | `"oracle"` |
| FQN format | `project.dataset.table` | `DATABASE.SCHEMA.TABLE` | - |
| Variable syntax | `var_name` | `:var_name` | `var_name` |
| Temp table | `OPTIONS (expiration...)` | `CREATE TEMPORARY TABLE` | - |
| UUID function | `GENERATE_UUID()` | `UUID_STRING()` | `SYS_GUID()` |

---

## CARTO Environment Variables

Available in `cartoEnvVars` array:

- `analyticsToolboxDataset` - Location of Analytics Toolbox
- `analyticsToolboxVersion` - Version of Analytics Toolbox
- `apiBaseUrl` - CARTO API base URL
- `accessToken` - Authentication token
- `dataExportDefaultGCSBucket` - Default GCS bucket
- `bigqueryProjectId` - BigQuery project ID
- `bigqueryRegion` - BigQuery region
- `tempStoragePath` - Temporary storage path

---

## Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Component name doesn't match folder" | Mismatch | Rename folder to match metadata |
| "Invalid provider" | Wrong value | Use `"bigquery"`, `"snowflake"`, or `"oracle"` |
| "Icon file not found" | Missing file | Add SVG to `/icons/` |
| "cartoEnvVars is required" | Missing property | Add empty array: `[]` |
| "Invalid version format" | Wrong format | Use `"1.0.0"` format |
| "Parent input not found" | Column input issue | Ensure parent Table input exists |

---

## Testing Quick Reference

### Test Structure
```json
[
  {
    "id": 1,
    "inputs": {
      "input_table": "test_data",    // References .ndjson file
      "param1": "value1"              // Literal value
    },
    "env_vars": {                     // Optional
      "analyticsToolboxDataset": "..."
    }
  }
]
```

### Test Data (NDJSON)
```json
{"id":1,"name":"Alice"}
{"id":2,"name":"Bob"}
```

### Fixture (Expected Output)
```json
{
  "output_table": [
    {"id":1,"name":"Alice","new_col":"value"},
    {"id":2,"name":"Bob","new_col":"value"}
  ]
}
```

---

## Authentication

### BigQuery
```bash
gcloud auth application-default login
```

### Snowflake
```bash
export SF_ACCOUNT=my_account
export SF_USER=my_user
export SF_PASSWORD=my_password
```

Or set in `.env` file for testing.

---

## Icon Specifications

| Type | Size | Safe Area | Format |
|------|------|-----------|--------|
| Extension | 80x80px | 8px | SVG |
| Component | 40x40px | 4px | SVG |

---

## Common Workflow

1. **Create** component folder and metadata
2. **Implement** fullrun.sql and dryrun.sql
3. **Check** with `python carto_extension.py check`
4. **Test** with sample data
5. **Capture** expected outputs
6. **Deploy** to data warehouse
7. **Verify** in Workflows UI
8. **Package** for distribution

---

## Decision Trees

### Which Input Type?

```
Need user input?
├─ Upstream table → Table
├─ Column from table → Column
├─ Text?
│  ├─ Single line → String
│  ├─ Multiple lines → String (mode: multiline)
│  └─ SQL code → StringSql
├─ Number?
│  ├─ Precise value → Number
│  └─ Range selection → Number (mode: slider) or Range
├─ True/false → Boolean
├─ Pick one option → Selection
├─ Pick multiple → Selection (mode: multiple)
├─ Min/max values → Range
├─ JSON data → Json
└─ Spatial data?
   ├─ Paste GeoJSON → GeoJson
   └─ Draw on map → GeoJsonDraw
```

### Fullrun vs Dryrun?

```
Schema preview needed?
├─ Yes → Implement dryrun.sql
│  ├─ Same columns as fullrun
│  ├─ Same types as fullrun
│  ├─ Use literals instead of functions
│  └─ Add WHERE 1 = 0
└─ Actual execution?
   └─ Implement fullrun.sql
      ├─ Process data
      ├─ Add/transform columns
      └─ Create output table
```

---

## See Also

- [Glossary](../glossary.md) - All terms defined
- [Validation Rules](./validation-rules.md) - Complete constraints
- [Component Metadata](../component_metadata.md) - Detailed input types
- [Examples](../examples/) - Working code examples
- [Quickstart](../quickstart.md) - 5-minute tutorial
