-- Minimal Component - Dry Run (Schema Only)
-- Must produce same schema as fullrun.sql but with zero rows

EXECUTE IMMEDIATE '''
    CREATE TABLE IF NOT EXISTS ''' || output_table || '''
    OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))
    AS SELECT
        *,  -- Same columns as fullrun
        \'''' || constant_value || '''\' AS constant_col  -- Same column as fullrun
    FROM ''' || input_table || '''
    WHERE 1 = 0;  -- CRITICAL: Return zero rows
''';
