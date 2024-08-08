-- This is a template for creating a BigQuery procedure.
-------------------------------------------------------

CREATE OR REPLACE PROCEDURE @@workflows_temp@@.ADD_FIXED_VALUE_COLUMN(input_table STRING, value STRING, output_table STRING, dry_run BOOL)
BEGIN
    IF (dry_run) THEN
        EXECUTE IMMEDIATE '''
        CREATE TABLE IF NOT EXISTS ''' || output_table || '''
        OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))
        AS SELECT *, \'''' || value || '''\' AS fixed_value_col
        FROM ''' || input_table || '''
        WHERE 1 = 0;
        ''';
    ELSE
        EXECUTE IMMEDIATE '''
        CREATE TABLE IF NOT EXISTS ''' || output_table || '''
        OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY))
        AS SELECT *, \'''' || value || '''\' AS fixed_value_col
        FROM ''' || input_table;
    END IF;
END;




-- This is a template for creating a SnowFlake procedure.
---------------------------------------------------------
/*
CREATE OR REPLACE PROCEDURE @@workflows_temp@@.ADD_FIXED_VALUE_COLUMN(input_table STRING, value STRING, output_table STRING, dry_run BOOLEAN)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
BEGIN
    IF (dry_run) THEN
        EXECUTE IMMEDIATE '
        CREATE TABLE IF NOT EXISTS ' || :output_table || '
        AS SELECT *, ''' || :value || ''' AS fixed_value_col
        FROM ' || :input_table || '
        WHERE 1 = 0;
        ';
    ELSE
        EXECUTE IMMEDIATE '
        CREATE TABLE IF NOT EXISTS ' || :output_table || '
        AS SELECT *, ''' || :value || ''' AS fixed_value_col
        FROM ' || :input_table ;
    END IF;
END;
$$;
*/