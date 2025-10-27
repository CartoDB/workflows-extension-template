-- ============================================================================
-- DRYRUN.SQL: Schema-Only Execution Logic
-- ============================================================================
-- This file implements a "dry run" - producing the output schema without
-- processing actual data or performing expensive operations.
--
-- PURPOSE:
-- Workflows needs to preview the schema (column names and types) of each
-- component's output BEFORE executing the full workflow. This allows the UI
-- to show schema information and validate connections between components.
--
-- KEY REQUIREMENT:
-- Must produce EXACTLY the same schema as fullrun.sql, but return ZERO rows.
--
-- OPTIMIZATION STRATEGY:
-- Replace expensive operations (functions, computations) with literals that
-- produce the same data type. This makes dry runs fast regardless of data size.
--
-- AVAILABLE VARIABLES:
-- Same as fullrun.sql - all inputs, outputs, and cartoEnvVars from metadata.json
-- ============================================================================


-- ============================================================================
-- BIGQUERY IMPLEMENTATION
-- ============================================================================
-- This is the sample code for the BigQuery dryrun.
-------------------------------------------------------

-- PATTERN: Dynamic SQL Execution (same as fullrun)
EXECUTE IMMEDIATE '''
    -- PATTERN: Idempotent Table Creation (same as fullrun)
    CREATE TABLE IF NOT EXISTS ''' || output_table || '''

    -- PATTERN: Temporary Table with Expiration (same as fullrun)
    -- NOTE: Must match fullrun.sql table creation options exactly
    OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))

    -- PATTERN: Schema-Matching SELECT
    -- CRITICAL: Column names and types must exactly match fullrun.sql
    AS SELECT
        *,  -- PATTERN: Preserve all input columns (same as fullrun)

        -- PATTERN: Literal Value Instead of Computation
        -- COMPARISON WITH FULLRUN:
        -- - fullrun.sql: \'''' || value || '''\' AS fixed_value_col
        -- - dryrun.sql:  \'''' || value || '''\' AS fixed_value_col (same!)
        -- Both produce STRING type, so schema is identical.
        --
        -- WHEN TO OPTIMIZE:
        -- If fullrun used GENERATE_UUID(), we'd use "literal_string" here instead.
        -- If fullrun used complex calculation, we'd use simple constant here.
        \'''' || value || '''\' AS fixed_value_col
    FROM ''' || input_table || '''

    -- PATTERN: Zero Rows Return
    -- CRITICAL: WHERE 1 = 0 ensures query returns no rows while preserving schema.
    -- This makes dryrun instant regardless of input table size.
    -- NEVER omit this clause - it's what makes this a "dry run".
    WHERE 1 = 0;
''';

-- WHY DRY RUN MATTERS:
-- Without dry runs, Workflows would need to execute every component just to
-- discover output schemas. This would be:
-- 1. Slow (processing potentially huge tables)
-- 2. Expensive (compute costs)
-- 3. Risky (side effects before user confirms)
--
-- Dry runs solve this by providing schema instantly with zero data processing.


-- ============================================================================
-- COMMON OPTIMIZATION PATTERNS
-- ============================================================================

-- Replace expensive operations with cheap equivalents that match schema:
--
-- Fullrun                          Dryrun Alternative
-- ----------------------------------------
-- GENERATE_UUID()          -->     "uuid_literal"
-- CURRENT_TIMESTAMP()      -->     TIMESTAMP("2000-01-01 00:00:00")
-- complex_function(x)      -->     CAST(NULL AS appropriate_type)
-- ST_DISTANCE(a, b)        -->     0.0
-- ML_PREDICT(model, x)     -->     NULL
-- HTTP_REQUEST(url)        -->     "response"
--
-- The key: Same data TYPE, minimal computation


-- ============================================================================
-- ORACLE IMPLEMENTATION (ALTERNATIVE)
-- ============================================================================
-- This is the sample code for the Oracle dryrun.
-------------------------------------------------------
-- UNCOMMENT if targeting Oracle. Must match fullrun.sql schema exactly.
/*
EXECUTE IMMEDIATE '
    CREATE TABLE ' || output_table || ' AS
    SELECT t.*, ''' || value || ''' AS fixed_value_col
    FROM ' || input_table || ' t
    WHERE 1 = 0';
*/

-- KEY POINTS:
-- - WHERE 1 = 0 is cross-platform SQL for "no rows"
-- - Schema must match fullrun.sql Oracle version
-- - No OPTIONS clause (Oracle doesn't support it)


-- ============================================================================
-- SNOWFLAKE IMPLEMENTATION (ALTERNATIVE)
-- ============================================================================
-- This is the sample code for the Snowflake dryrun.
---------------------------------------------------------
-- UNCOMMENT if targeting Snowflake. Must match fullrun.sql schema exactly.
/*
EXECUTE IMMEDIATE '
    CREATE TABLE IF NOT EXISTS ' || :output_table || '
    AS SELECT *, ''' || :value || ''' AS fixed_value_col
    FROM ' || :input_table || '
    WHERE 1 = 0;
';
*/

-- KEY POINTS:
-- - Variables prefixed with : (Snowflake binding syntax)
-- - WHERE 1 = 0 works identically in Snowflake
-- - Schema must match fullrun.sql Snowflake version


-- ============================================================================
-- SCHEMA MATCHING CHECKLIST
-- ============================================================================
-- Before finalizing dryrun.sql, verify:
--
-- ✓ Column count matches fullrun.sql exactly
-- ✓ Column names match fullrun.sql exactly (case-sensitive)
-- ✓ Column types match fullrun.sql exactly
-- ✓ Column order matches fullrun.sql exactly
-- ✓ WHERE 1 = 0 is present and correct
-- ✓ Table creation options match fullrun.sql
-- ✓ No expensive operations remain (replaced with literals)
--
-- TEST YOUR DRYRUN:
-- 1. Deploy both fullrun and dryrun: python carto_extension.py deploy ...
-- 2. Compare schemas in your data warehouse:
--    SELECT column_name, data_type FROM information_schema.columns
--    WHERE table_name IN ('fullrun_output', 'dryrun_output')
--    ORDER BY ordinal_position;
-- 3. Schemas must be identical (dryrun just has 0 rows)


-- ============================================================================
-- COMMON MISTAKES TO AVOID
-- ============================================================================

-- ❌ MISTAKE 1: Forgetting WHERE 1 = 0
-- Result: Dryrun processes all data (slow, expensive, defeats purpose)
--
-- ❌ MISTAKE 2: Different column names/order than fullrun
-- Result: Workflows UI shows wrong schema, connections fail
--
-- ❌ MISTAKE 3: Different data types than fullrun
-- Result: Type mismatches when connecting to downstream components
--
-- ❌ MISTAKE 4: Keeping expensive operations
-- Result: Dryrun takes long time, especially on large tables
--
-- ❌ MISTAKE 5: Different table OPTIONS than fullrun
-- Result: Inconsistent behavior between preview and execution


-- ============================================================================
-- DEBUGGING DRY RUN ISSUES
-- ============================================================================
--
-- If Workflows shows wrong schema:
-- 1. Check column names match fullrun.sql exactly
-- 2. Check data types match (use CAST if needed)
-- 3. Check column order is identical
-- 4. Verify WHERE 1 = 0 is present
--
-- If dryrun is slow:
-- 1. Ensure WHERE 1 = 0 exists and is not overridden
-- 2. Replace function calls with literals
-- 3. Remove JOINs if possible (use LIMIT 0 alternative)
-- 4. Check input table has proper indexing
--
-- If tests fail:
-- 1. Run fullrun and dryrun separately
-- 2. Compare output schemas manually
-- 3. Check for whitespace differences in column names
-- 4. Verify data types with explicit CAST if needed
-- ============================================================================
