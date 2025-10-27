---
title: Validation Rules Reference
description: Complete set of constraints, requirements, and validation rules for extensions and components
version: 1.0.0
last-updated: 2025-01-27
depends-on: [extension_metadata.md, component_metadata.md]
tags: [reference, validation, constraints, rules]
---

# Validation Rules Reference

Comprehensive validation constraints for extension development. Use this as a reference when creating or validating metadata and code.

---

## Naming Conventions

| Element | Pattern | Example Valid | Example Invalid | Notes |
|---------|---------|---------------|-----------------|-------|
| Extension name | `^[a-z0-9_]+$` | `my_extension` | `My-Extension`, `my.extension` | Lowercase, underscores only |
| Component name | `^[a-z0-9_]+$` | `add_uuid`, `spatial_join` | `addUUID`, `spatial-join` | Must match folder name exactly |
| Variable name (SQL) | `^[a-z0-9_]+$` | `input_table`, `output_table` | `inputTable`, `input-table` | Used in metadata and SQL |
| Input name | `^[a-z0-9_]+$` | `column_name`, `radius` | `columnName`, `radius-m` | Becomes SQL variable |
| Output name | `^[a-z0-9_]+$` | `output_table` | `outputTable`, `output.table` | Becomes SQL variable |
| Icon filename | `^.+\.svg$` | `icon.svg`, `my_icon.svg` | `icon.png`, `icon` | Must be SVG format |

**Key Rule:** All identifiers use `snake_case` (lowercase with underscores), not `camelCase` or `kebab-case`.

---

## Required vs Optional Fields

### Extension Metadata (`metadata.json` at root)

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `name` | ✓ | string | Must match pattern `^[a-z0-9_]+$` |
| `title` | ✓ | string | Display name, any format |
| `industry` | ✓ | string | Category for grouping |
| `description` | ✓ | string | Brief explanation |
| `icon` | ✓ | string | SVG filename (must exist in `/icons/`) |
| `version` | ✓ | string | Semantic version `^\\d+\\.\\d+\\.\\d+$` |
| `author` | ✓ | object | Must have `value` property |
| `author.value` | ✓ | string | Author name |
| `author.link` | ✗ | object | Optional hyperlink |
| `license` | ✓ | object | Must have `value` property |
| `license.value` | ✓ | string | License identifier |
| `license.link` | ✗ | object | Optional hyperlink |
| `lastUpdate` | ✓ | string | Human-readable date |
| `provider` | ✓ | string | Must be `"bigquery"`, `"snowflake"`, or `"oracle"` |
| `details` | ✓ | array | Can be empty `[]` |
| `components` | ✓ | array | List of component folder names (min 1) |

### Component Metadata (`components/<name>/metadata.json`)

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `name` | ✓ | string | Must match folder name and pattern |
| `title` | ✓ | string | Display name |
| `description` | ✓ | string | Brief explanation |
| `version` | ✓ | string | Semantic version |
| `icon` | ✓ | string | SVG filename |
| `externalReference` | ✗ | object | Optional external docs link |
| `cartoEnvVars` | ✓ | array | Can be empty `[]` |
| `inputs` | ✓ | array | Can be empty `[]` |
| `outputs` | ✓ | array | Min 1 output required |

### Input Properties (varies by type)

| Property | Table | Column | String | Number | Boolean | Selection | Range | Json | GeoJson | GeoJsonDraw | StringSql |
|----------|-------|--------|--------|--------|---------|-----------|-------|------|---------|-------------|-----------|
| `name` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `title` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `type` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `description` | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `parent` | - | ✓ | - | - | - | - | - | - | - | - | - |
| `dataType` | - | ✓ | - | - | - | - | - | - | - | - | - |
| `options` | - | - | - | - | - | ✓ | - | - | - | - | - |
| `min` | - | - | - | ✗ | - | - | - | - | - | - | - |
| `max` | - | - | - | ✗ | - | - | - | - | - | - | - |
| `mode` | - | - | ✗ | ✗ | - | ✗ | - | - | - | - | - |
| Generic options | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Generic options** (all optional): `placeholder`, `optional`, `default`, `helper`, `advanced`, `showIf`

**Legend:** ✓ = Required, ✗ = Optional, - = Not applicable

---

## Data Warehouse Compatibility

| Feature | BigQuery | Snowflake | Oracle | Notes |
|---------|----------|-----------|--------|-------|
| Supported | ✓ | ✓ | ✓ | Must set `provider` in extension metadata |
| FQN format | `project.dataset.table` | `DATABASE.SCHEMA.TABLE` | - | Case-sensitive for Snowflake (uppercase) |
| Session table format | `tablename` | `tablename` | - | Used in API/stored procedure mode |
| SQL dialect | Standard SQL | Snowflake SQL | Oracle SQL | Syntax differences apply |
| Temp table syntax | `CREATE TABLE ... OPTIONS (expiration_timestamp=...)` | `CREATE TEMPORARY TABLE ...` | - | Different patterns |
| UUID function | `GENERATE_UUID()` | `UUID_STRING()` | `SYS_GUID()` | Different function names |
| Dynamic SQL | `EXECUTE IMMEDIATE` | `EXECUTE IMMEDIATE` | `EXECUTE IMMEDIATE` | All support this |

**Provider Value:** Extension metadata must set `"provider"` to exactly one of: `"bigquery"`, `"snowflake"`, `"oracle"`

---

## File Structure Requirements

### Required Files

```
extension-root/
├── metadata.json                          # Required: Extension metadata
├── icons/                                 # Required: At minimum, extension icon
│   └── extension_icon.svg                # Required: Referenced in extension metadata
├── components/                            # Required: At least one component
│   └── <component_name>/                 # Folder name must match component "name"
│       ├── metadata.json                  # Required: Component metadata
│       └── src/                           # Required: Source folder
│           ├── fullrun.sql                # Required: Full execution logic
│           └── dryrun.sql                 # Required: Dry run logic
```

### Optional Files

```
extension-root/
├── .env                                   # Optional: Environment variables for testing
├── components/
│   └── <component_name>/
│       ├── doc/                           # Optional: Component documentation
│       │   └── README.md
│       ├── test/                          # Optional but recommended: Tests
│       │   ├── test.json                  # Test definitions
│       │   ├── *.ndjson                   # Test data
│       │   └── fixtures/
│       │       └── *.json                 # Expected outputs
│       └── icons/                         # Optional: Component-specific icons
│           └── component_icon.svg
```

### Naming Constraints

- Component folder name must **exactly match** component metadata `name` field
- Icon filename must **exactly match** reference in metadata
- Test data files can have any name (referenced in `test.json`)
- Fixture files must be named `<test_id>.json` (e.g., `1.json`, `2.json`)

---

## SQL Constraints

### Variable Availability

| Variable Source | Available In | Format | Example Value |
|-----------------|--------------|--------|---------------|
| Input parameters | fullrun.sql, dryrun.sql | String variable | `input_table` = `"myproject.mydataset.table1"` |
| Output parameters | fullrun.sql, dryrun.sql | String variable | `output_table` = `"myproject.mydataset.table2"` |
| cartoEnvVars | fullrun.sql, dryrun.sql | String variable | `analyticsToolboxDataset` = `"carto-un.carto"` |

### FQN vs Session Table Handling

**Rule:** Components must handle BOTH execution modes:

| Mode | Context | Table Name Format | Detection Pattern |
|------|---------|-------------------|-------------------|
| UI Execution | Workflows UI | FQN: `project.dataset.table` | Contains `.` (dot) |
| API Execution | Stored procedure/API | Session: `tablename` | No dots |

**Detection SQL:**
```sql
-- Check if table is FQN or session table
CASE
  WHEN REGEXP_CONTAINS(input_table, r'\.') THEN 'FQN'
  ELSE 'session'
END
```

### Dryrun Requirements

| Requirement | Fullrun | Dryrun | Notes |
|-------------|---------|--------|-------|
| Must produce same schema | ✓ | ✓ | Column names and types must match exactly |
| Must return rows | ✓ | ✗ | Dryrun returns 0 rows |
| Can use expensive operations | ✓ | ✗ | Dryrun should optimize (literals instead of functions) |
| Must use `WHERE 1 = 0` | - | ✓ | Critical: Ensures no rows returned |

**Pattern:**
```sql
-- Fullrun
SELECT *, GENERATE_UUID() AS uuid FROM input_table

-- Dryrun (same schema, no rows, faster)
SELECT *, "uuid_string" AS uuid FROM input_table WHERE 1 = 0
```

### Analytics Toolbox Location Reference

**Two approaches for different use cases:**

#### Approach 1: Placeholder (for procedure definitions)

| Aspect | Details |
|--------|---------|
| **Placeholder** | `@@analytics_toolbox_location@@` |
| **Usage** | `SELECT @@analytics_toolbox_location@@.FUNCTION_NAME(geom) FROM table` |
| **Use case** | When FQN must be in the stored procedure definition |
| **When substituted** | Once at extension installation time (static) |
| **Substituted with** | Connection-specific location (e.g., `carto-un.carto`) |
| **Who performs substitution** | CARTO Workflows frontend during installation |
| **Availability** | **BigQuery only** |

#### Approach 2: cartoEnvVars (for dynamic SQL)

| Aspect | Details |
|--------|---------|
| **Variable** | `analyticsToolboxDataset` |
| **Declaration** | Add to `cartoEnvVars` array in component metadata |
| **Usage** | `''' || analyticsToolboxDataset || '''.FUNCTION_NAME(geom)` (in EXECUTE IMMEDIATE) |
| **Use case** | When building SQL dynamically |
| **When evaluated** | At workflow execution time (dynamic) |
| **Evaluated by** | CARTO Workflows when generating SQL |
| **Flexibility** | Can change if connection settings change |
| **Availability** | BigQuery, Snowflake, Oracle |

**Key Difference:**
- **Placeholder** = Baked into procedure definition at installation time
- **cartoEnvVars** = Evaluated when building dynamic SQL at execution time

**For local testing:** Define in `.env` file as `analytics_toolbox_location=carto-un.carto`

---

## Icon Specifications

| Type | Size | Safe Area | Format | Location |
|------|------|-----------|--------|----------|
| Extension | 80x80px | 8px | SVG | `/icons/` |
| Component | 40x40px | 4px | SVG | `/icons/` or `/components/<name>/icons/` |

**Safe Area:** Padding where no important visual elements should be placed

**Validation:**
- Must be valid SVG format
- Referenced filename must exist in icons folder
- Case-sensitive filename matching

---

## Test Configuration Constraints

### test.json Structure

```json
[
  {
    "id": 1,                          // Required: Unique test ID (number)
    "inputs": {                       // Required: Object with input values
      "input_table": "table1",        // Table inputs reference .ndjson filename (no extension)
      "param1": "value1"              // Other inputs provide literal values
    },
    "env_vars": {                     // Optional: Environment variables for this test
      "analyticsToolboxDataset": "..."
    }
  }
]
```

**Rules:**
- Test IDs must be unique within component
- Fixture filename must match test ID: `fixtures/<id>.json`
- Table input values reference NDJSON files without `.ndjson` extension
- NDJSON files must exist in same `/test/` folder

### Fixture Structure

```json
{
  "output_table": [                   // Key matches output parameter name
    {                                 // Array of row objects
      "column1": "value1",
      "column2": 123
    }
  ]
}
```

**Rules:**
- Root object keys match output parameter names
- Values are arrays of row objects
- Column order doesn't matter (test compares sets)
- Placeholders are reverse-substituted during capture

---

## Input Type-Specific Constraints

### Column Input

| Constraint | Rule |
|------------|------|
| `parent` must reference Table input | Parent input must exist in same component's inputs array |
| `dataType` array must be non-empty | At least one type: `string`, `number`, `boolean`, `geography`, `timestamp`, `date` |
| Parent must be Table type | Referenced input must have `"type": "Table"` |

### Selection Input

| Constraint | Rule |
|------------|------|
| `options` array required | Must contain at least 1 option |
| `mode: "multiple"` | Generates array of selected values in SQL |
| Without mode | Generates single string value in SQL |

### Number Input

| Constraint | Rule |
|------------|------|
| `min` < `max` | If both provided, min must be less than max |
| `default` within bounds | If min/max provided, default must be in range |
| `mode: "slider"` | Renders slider UI, requires min/max for best UX |

### Range Input

| Constraint | Rule |
|------------|------|
| Always generates array | SQL receives `["min_value", "max_value"]` format |
| String values | Even numeric ranges come as strings |

### GeoJson / GeoJsonDraw

| Constraint | Rule |
|------------|------|
| Value format | Valid GeoJSON object structure |
| Passed to SQL as | Plain JSON object (not string) |

---

## CARTO Environment Variables

Valid values for `cartoEnvVars` array:

| Variable | Description | Type |
|----------|-------------|------|
| `analyticsToolboxDataset` | Location of Analytics Toolbox functions | string (FQN) |
| `analyticsToolboxVersion` | Version of Analytics Toolbox | string |
| `apiBaseUrl` | CARTO API base URL | string (URL) |
| `accessToken` | Authentication token | string |
| `dataExportDefaultGCSBucket` | Default GCS bucket | string |
| `bigqueryProjectId` | BigQuery project ID | string |
| `bigqueryRegion` | BigQuery region | string |
| `tempStoragePath` | Temporary storage path | string |

**Constraint:** Only these exact strings are valid. Any other value will fail validation.

---

## Common Validation Errors

| Error Pattern | Cause | Solution |
|---------------|-------|----------|
| "Component name doesn't match folder" | Folder: `my-component`, metadata name: `my_component` | Rename folder to match metadata |
| "Invalid provider" | `"provider": "bq"` | Use exact value: `"bigquery"` |
| "Icon file not found" | Icon referenced but file missing | Add SVG to `/icons/` folder |
| "cartoEnvVars is required" | Property missing or null | Add empty array: `"cartoEnvVars": []` |
| "Component not listed" | Component exists but not in extension's `components` array | Add to root metadata.json |
| "Invalid version format" | `"version": "1.0"` or `"v1.0.0"` | Use semantic version: `"1.0.0"` |
| "Parent input not found" | Column input references non-existent parent | Ensure parent input exists with `type: "Table"` |
| "Invalid dataType" | `"dataType": ["text"]` | Use valid type: `["string"]` |

---

## Best Practices

### Naming
- Use descriptive, not abbreviated names: `input_table` not `in_tbl`
- Component names should describe action: `add_uuid`, `spatial_join`
- Avoid generic names: `component1`, `output`

### Metadata
- Provide descriptions for all inputs/outputs (helps users)
- Use helper text for complex parameters
- Group related inputs under "Advanced options" with `"advanced": true`

### SQL
- Always handle both FQN and session table names
- Use `CREATE TABLE IF NOT EXISTS` for idempotency
- Set expiration timestamps on temporary tables
- Comment complex logic
- Validate inputs before processing

### Testing
- Write tests for all components (not optional in practice)
- Test edge cases (empty tables, null values, boundary conditions)
- Use descriptive test IDs that indicate what's being tested
- Capture fixtures after every logic change

---

## See Also

- [Extension Metadata Schema](./extension-metadata-schema.json)
- [Component Metadata Schema](./component-metadata-schema.json)
- [Glossary](../glossary.md)
- [Component Metadata Reference](../component_metadata.md)
