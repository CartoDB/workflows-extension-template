-- ============================================================================
-- FULLRUN.SQL: Complete Execution Logic
-- ============================================================================
-- This file contains the actual execution logic for the component.
-- It processes data and produces results when the workflow runs.
--
-- AVAILABLE VARIABLES:
-- - All inputs defined in metadata.json are available as variables
-- - All outputs defined in metadata.json are available as variables
-- - All cartoEnvVars defined in metadata.json are available as variables
--
-- For this template:
-- - input_table: Contains FQN (project.dataset.table) or session table name
-- - output_table: Contains FQN or session table name for result
-- - value: User-provided string value from component configuration
-- ============================================================================


-- ============================================================================
-- BIGQUERY IMPLEMENTATION
-- ============================================================================
-- This is the sample code for the BigQuery fullrun.
-------------------------------------------------------

-- PATTERN: Dynamic SQL Execution
-- WHY: Table names are dynamic (user-configured), so we use EXECUTE IMMEDIATE
-- to construct and run SQL statements with variable table names.

EXECUTE IMMEDIATE '''
    -- PATTERN: Idempotent Table Creation
    -- WHY: CREATE TABLE IF NOT EXISTS ensures the component can run multiple times
    -- without errors, even if the output table already exists from a previous run.
    CREATE TABLE IF NOT EXISTS ''' || output_table || '''

    -- PATTERN: Temporary Table with Expiration
    -- WHY: Workflow tables are temporary. Setting expiration_timestamp ensures
    -- automatic cleanup after 30 days, preventing storage accumulation.
    -- BIGQUERY-SPECIFIC: This OPTIONS clause is BigQuery syntax.
    OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))

    -- PATTERN: Select-Transform-Add Columns
    -- WHY: Most workflow components augment data rather than replace it.
    -- SELECT * preserves all input columns, then we add new computed columns.
    AS SELECT
        *,  -- PATTERN: Preserve all input columns

        -- PATTERN: String Value Escaping
        -- WHY: The \'''' || value || '''\' pattern properly escapes quotes
        -- in the dynamic SQL string to create a string literal in the final query.
        -- Example: If value = "test", this produces: 'test' in the executed SQL.
        \'''' || value || '''\' AS fixed_value_col
    FROM ''' || input_table;

-- EXECUTION CONTEXT HANDLING:
-- This code works in BOTH execution modes:
-- 1. UI Mode: input_table and output_table are FQNs (project.dataset.table)
-- 2. API Mode: input_table and output_table are session tables (tablename)
-- No special handling needed because table reference syntax is identical.

-- VARIABLE INTERPOLATION:
-- Variables like input_table, output_table, and value are interpolated BEFORE
-- the SQL executes. They are not SQL parameters - they're string concatenation
-- in the stored procedure that generates this EXECUTE IMMEDIATE statement.


-- ============================================================================
-- ORACLE IMPLEMENTATION (ALTERNATIVE)
-- ============================================================================
-- This is the sample code for the Oracle fullrun.
-------------------------------------------------------
-- UNCOMMENT and modify if targeting Oracle data warehouses.
-- Set "provider": "oracle" in extension metadata.json to use this version.
/*
EXECUTE IMMEDIATE '
    CREATE TABLE ' || output_table || ' AS
    SELECT t.*, ''' || value || ''' AS fixed_value_col
    FROM ' || input_table || ' t';
*/

-- KEY DIFFERENCES FROM BIGQUERY:
-- - No OPTIONS clause (Oracle doesn't support this syntax)
-- - Table alias 't' required in Oracle for some contexts
-- - No IF NOT EXISTS (Oracle syntax differs)
-- - String escaping simpler (different quoting rules)


-- ============================================================================
-- SNOWFLAKE IMPLEMENTATION (ALTERNATIVE)
-- ============================================================================
-- This is the sample code for the Snowflake fullrun.
---------------------------------------------------------
-- UNCOMMENT and modify if targeting Snowflake data warehouses.
-- Set "provider": "snowflake" in extension metadata.json to use this version.
/*
EXECUTE IMMEDIATE '
    CREATE TABLE IF NOT EXISTS ' || :output_table || '
    AS SELECT *, ''' || :value || ''' AS fixed_value_col
    FROM ' || :input_table ;
*/

-- KEY DIFFERENCES FROM BIGQUERY:
-- - Variables prefixed with : (e.g., :output_table) - Snowflake binding syntax
-- - No OPTIONS clause for expiration (use CREATE TEMPORARY TABLE instead)
-- - String escaping similar to BigQuery
-- - Table name handling identical (FQN vs session)

-- SNOWFLAKE TEMPORARY TABLES:
-- For temporary tables in Snowflake, use:
-- CREATE TEMPORARY TABLE ... instead of OPTIONS clause
-- Temporary tables auto-expire at session end.


-- ============================================================================
-- COMMON PATTERNS ACROSS ALL PROVIDERS
-- ============================================================================

-- 1. ALWAYS use EXECUTE IMMEDIATE for dynamic table names
-- 2. ALWAYS preserve input columns with SELECT *
-- 3. ALWAYS handle string escaping carefully in nested quotes
-- 4. ALWAYS set expiration/temporary flags for workflow tables
-- 5. NEVER hardcode table names - always use variables
-- 6. NEVER assume table format - handle both FQN and session tables

-- ============================================================================
-- TESTING YOUR COMPONENT
-- ============================================================================
-- After modifying this file:
-- 1. Run: python carto_extension.py check (validate syntax)
-- 2. Create tests in ../test/ folder
-- 3. Run: python carto_extension.py capture (create expected outputs)
-- 4. Run: python carto_extension.py test (verify behavior)
-- 5. Deploy: python carto_extension.py deploy --destination=...
-- ============================================================================
