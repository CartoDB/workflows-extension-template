---
title: Quickstart Guide
description: Minimal path to creating your first CARTO Workflows extension component
version: 1.0.0
last-updated: 2025-01-27
depends-on: []
tags: [quickstart, getting-started, tutorial]
---

# Quickstart: Create Your First Component in 5 Minutes

This guide takes you from zero to a working extension component as quickly as possible, skipping optional features.

## Prerequisites

- Python 3.x installed
- Access to BigQuery or Snowflake
- Authenticated with your data warehouse (see [Authentication](#authentication))

## 5-Minute Setup

### 1. Create Repository (30 seconds)

```bash
# Create from template on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/YOUR_EXTENSION_NAME
cd YOUR_EXTENSION_NAME

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Extension Metadata (1 minute)

Edit `metadata.json` in the root folder:

```json
{
  "name": "my_extension",
  "title": "My Extension",
  "industry": "General",
  "description": "My first extension",
  "icon": "extension_icon.svg",
  "version": "1.0.0",
  "author": {
    "value": "Your Name"
  },
  "license": {
    "value": "MIT"
  },
  "lastUpdate": "Jan 27, 2025",
  "provider": "bigquery",
  "details": [],
  "components": ["add_uuid"]
}
```

### 3. Create Your Component (2 minutes)

```bash
# Copy the template
cp -r components/template components/add_uuid
```

Edit `components/add_uuid/metadata.json`:

```json
{
  "name": "add_uuid",
  "title": "Add UUID",
  "description": "Adds a UUID column to the input table",
  "version": "1.0.0",
  "icon": "component_icon.svg",
  "cartoEnvVars": [],
  "inputs": [
    {
      "name": "input_table",
      "title": "Input table",
      "description": "The table to add the UUID column to",
      "type": "Table"
    }
  ],
  "outputs": [
    {
      "name": "output_table",
      "title": "Output table",
      "description": "Table with UUID column added",
      "type": "Table"
    }
  ]
}
```

The SQL files (`src/fullrun.sql` and `src/dryrun.sql`) already implement a UUID component, so you can use them as-is.

### 4. Validate (30 seconds)

```bash
python carto_extension.py check
```

Expected output:
```
Checking extension...
Extension correctly checked. No errors found.
```

### 5. Deploy and Test (1 minute)

**For BigQuery:**
```bash
python carto_extension.py deploy --destination=myproject.workflows_temp
```

**For Snowflake:**
```bash
python carto_extension.py deploy --destination=MYDATABASE.WORKFLOWS_TEMP
```

Then test in CARTO Workflows UI by refreshing the components panel.

## What You Just Created

Your component:
1. Takes an input table
2. Adds a UUID column using `GENERATE_UUID()`
3. Outputs the result table
4. Works in both dry-run (schema preview) and full execution modes

## Next Steps

Now that you have a working component, explore:

- **[Add more inputs](./component_metadata.md#inputs)** - Add parameters like strings, numbers, selections
- **[Modify the logic](./procedure.md)** - Change what the component does
- **[Add tests](./running_tests.md)** - Ensure your component works correctly
- **[Package for distribution](./build_your_extension.md)** - Create a `.zip` file to share

## Authentication

### BigQuery
```bash
gcloud auth application-default login
```

### Snowflake
Set environment variables:
```bash
export SF_ACCOUNT=my_snowflake_account
export SF_USER=my_snowflake_user
export SF_PASSWORD=my_snowflake_password
```

## Troubleshooting

**"Extension incorrectly checked" error**
- Verify all required fields in metadata.json
- Check that component name matches folder name
- Ensure `components` array in root metadata lists your component

**Component doesn't appear in Workflows**
- Verify deployment destination matches Workflows temp location
- Default is `workflows_temp` (BigQuery) or `WORKFLOWS_TEMP` (Snowflake)
- Check data warehouse authentication

**Validation errors in JSON**
- Use schemas in `/doc/reference/` to validate your metadata files
- Ensure no trailing commas in JSON
- Check that all required fields are present

## Understanding the Template Component

The template component demonstrates key patterns:

**`fullrun.sql`** - Actual execution:
```sql
EXECUTE IMMEDIATE '''
CREATE TABLE IF NOT EXISTS ''' || output_table || '''
OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))
AS SELECT *, GENERATE_UUID() AS uuid
FROM ''' || input_table || ';';
```

**`dryrun.sql`** - Schema preview:
```sql
EXECUTE IMMEDIATE '''
CREATE TABLE IF NOT EXISTS ''' || output_table || '''
OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))
AS SELECT *, "uuid_string" AS uuid
FROM ''' || input_table || '''
WHERE 1 = 0;
''';
```

Key differences:
- Dry run uses `WHERE 1 = 0` to return no rows
- Dry run uses a string literal instead of `GENERATE_UUID()` (faster, same schema)
- Both create same table structure

## Variable Mapping

Input and output names in `metadata.json` become variables in SQL:
- `"name": "input_table"` → `input_table` variable in SQL
- `"name": "output_table"` → `output_table` variable in SQL

These contain the fully-qualified table names (FQN) in UI mode, or session table names in API mode.

## Further Reading

- **[Anatomy of an Extension](./anatomy_of_an_extension.md)** - Complete structure overview
- **[Component Metadata Reference](./component_metadata.md)** - All input types and options
- **[Writing Stored Procedures](./procedure.md)** - SQL patterns and best practices
- **[JSON Schemas](./reference/)** - Validate your metadata files
