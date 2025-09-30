BEGIN
  -- This is an example stored procedure
  DECLARE row_count INT64;
  DECLARE result_message STRING;
  
  -- Get count from the input table
  EXECUTE IMMEDIATE FORMAT('SELECT COUNT(*) FROM %s', input_table) INTO row_count;
  
  -- Log the message (in a real scenario this could insert into a log table)
  SET result_message = FORMAT('Processed table %s with %d rows. Message: %s', 
                               input_table, row_count, log_message);
  
  -- Return the result
  SELECT result_message as summary;
END
