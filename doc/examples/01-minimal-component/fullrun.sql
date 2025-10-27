-- Minimal Component - Full Execution
-- This demonstrates the simplest viable component SQL pattern

EXECUTE IMMEDIATE '''
    CREATE TABLE IF NOT EXISTS ''' || output_table || '''
    OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))
    AS SELECT
        *,  -- Preserve all input columns
        \'''' || constant_value || '''\' AS constant_col  -- Add new column
    FROM ''' || input_table;

-- VARIABLES AVAILABLE:
-- input_table: From Table input
-- output_table: From Table output
-- constant_value: From String input
