from google.cloud import bigquery
import snowflake.connector
from dotenv import load_dotenv
import argparse
from sys import argv
import os
import zipfile
import json
from uuid import uuid4
import base64
import re

WORKFLOWS_TEMP_SCHEMA = "WORKFLOWS_TEMP"
EXTENSIONS_TABLENAME = "WORKFLOWS_EXTENSIONS"
WORKFLOWS_TEMP_PLACEHOLDER = "@@workflows_temp@@"

load_dotenv()

bq_workflows_temp = f"`{os.getenv('BQ_TEST_PROJECT')}.{os.getenv('BQ_TEST_DATASET')}`"
sf_workflows_temp = f"{os.getenv('SF_TEST_DATABASE')}.{os.getenv('SF_TEST_SCHEMA')}"

sf_client_instance = None
bq_client_instance = None

def bq_client():
    global bq_client_instance
    if bq_client_instance is None:
        try:
            bq_client_instance = bigquery.Client(project=os.getenv('BQ_TEST_PROJECT'))
        except Exception as e:
            raise Exception(f"Error connecting to BigQuery: {e}")
    return bq_client_instance

def sf_client():
    global sf_client_instance
    if sf_client_instance is None:
        try:
            sf_client_instance = snowflake.connector.connect(
                user=os.getenv('SF_USER'),
                password=os.getenv('SF_PASSWORD'),
                account=os.getenv('SF_ACCOUNT')
            )
        except Exception as e:
            raise Exception(f"Error connecting to SnowFlake: {e}")
    return sf_client_instance

def add_namespace_to_component_names(metadata):
    for component in metadata["components"]:
        component["name"] = f'{metadata["name"]}.{component["name"]}'
    return metadata


def _encode_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Icon file '{os.path.basename(image_path)}' not found in icons folder")
    with open(image_path, "rb") as f:
        if image_path.endswith(".svg"):
            return f"data:image/svg+xml;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        else:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"


def create_metadata():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    metadata_file = os.path.join(current_folder, "metadata.json")
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    components = []
    components_folder = os.path.join(current_folder, 'components')
    icon_folder = os.path.join(current_folder, 'icons')
    icon_filename = metadata.get("icon")
    if icon_filename:
        icon_full_path = os.path.join(icon_folder, icon_filename)
        metadata["icon"] = _encode_image(icon_full_path)
    for component in metadata["components"]:
        metadata_file = os.path.join(
            components_folder, component, "metadata.json")
        with open(metadata_file, "r") as f:
            component_metadata = json.load(f)
            components.append(component_metadata)
        help_file = os.path.join(
            components_folder, component, "doc", "README.md")
        with open(help_file, "r") as f:
            help_text = f.read()
            help_text = help_text.replace("\n", "\\n")
            component_metadata["help"] = help_text
        icon_filename = component_metadata.get("icon")
        if icon_filename:
            icon_full_path = os.path.join(icon_folder, icon_filename)
            component_metadata["icon"] = _encode_image(icon_full_path)

    metadata['components'] = components
    return metadata


def create_sql_code_bq(metadata):
    procedures_code = ""
    current_folder = os.path.dirname(os.path.abspath(__file__))
    components_folder = os.path.join(current_folder, 'components')
    for component in metadata["components"]:
        procedure_file = os.path.join(
            components_folder, component["name"], "src", "procedure.sql")
        with open(procedure_file, "r") as f:
            procedure_code = f.read()
            procedures_code += "\n" + procedure_code
    procedures = [c["procedureName"] for c in metadata["components"]]

    code = f'''
DECLARE procedures ARRAY <STRING>;
DECLARE i INT64 DEFAULT 0;

CREATE TABLE IF NOT EXISTS {WORKFLOWS_TEMP_PLACEHOLDER}.{EXTENSIONS_TABLENAME} (
    name STRING,
    metadata STRING,
    procedures STRING
);

-- remove procedures from previous installations

SET procedures = ARRAY(
    SELECT procedures
    FROM {WORKFLOWS_TEMP_PLACEHOLDER}.{EXTENSIONS_TABLENAME}
    WHERE name = '{metadata["name"]}'
);
LOOP
    SET i = i + 1;
    IF i > ARRAY_LENGTH(procedures) THEN
        LEAVE;
    END IF;
    EXECUTE IMMEDIATE 'DROP PROCEDURE {WORKFLOWS_TEMP_PLACEHOLDER}.' || procedures[ORDINAL(i)];
END LOOP;

DELETE FROM {WORKFLOWS_TEMP_PLACEHOLDER}.{EXTENSIONS_TABLENAME}
WHERE name = '{metadata["name"]}';

-- create procedures
{procedures_code}

-- add to extensions table

INSERT INTO {WORKFLOWS_TEMP_PLACEHOLDER}.{EXTENSIONS_TABLENAME} (name, metadata, procedures)
VALUES ('{metadata["name"]}', '{json.dumps(metadata)}', '{','.join(procedures)}');
    '''

    return code


def create_sql_code_sf(metadata):
    procedures_code = ""
    current_folder = os.path.dirname(os.path.abspath(__file__))
    components_folder = os.path.join(current_folder, 'components')
    for component in metadata["components"]:
        procedure_file = os.path.join(
            components_folder, component["name"], "src", "procedure.sql")
        with open(procedure_file, "r") as f:
            procedure_code = f.read()
            procedures_code += "\n" + procedure_code
    procedures = []
    for c in metadata["components"]:
        # Extract parameters using regex
        pattern = r'CREATE OR REPLACE PROCEDURE.*?\(([^()]*?)\)'
        match = re.search(pattern, procedure_code, re.DOTALL)
        # Get first group of the match and split by comma
        parameters = match.group(1).split(',')
        if len(parameters) == 1 and parameters[0].strip() == '':
            parameters = []
        # Remove starting and trailing spaces
        parameters = [param.strip() for param in parameters]
        param_types = [p.split()[1].upper() for p in parameters]
        procedures.append(f"{c['procedureName']}({','.join(param_types)})")
    code = f'''
DECLARE
    procedures STRING;
BEGIN
    CREATE TABLE IF NOT EXISTS {WORKFLOWS_TEMP_PLACEHOLDER}.{EXTENSIONS_TABLENAME} (
        name STRING,
        metadata STRING,
        procedures STRING
    );

    -- remove procedures from previous installations

    procedures := (
        SELECT procedures
        FROM {WORKFLOWS_TEMP_PLACEHOLDER}.{EXTENSIONS_TABLENAME}
        WHERE name = '{metadata["name"]}'
    );

    BEGIN
        EXECUTE IMMEDIATE 'DROP PROCEDURE IF EXISTS {WORKFLOWS_TEMP_PLACEHOLDER}.'
            || REPLACE(:procedures, ';', ';DROP PROCEDURE IF EXISTS {WORKFLOWS_TEMP_PLACEHOLDER}.');
    EXCEPTION
        WHEN OTHER THEN
            NULL;
    END;

    DELETE FROM {WORKFLOWS_TEMP_PLACEHOLDER}.{EXTENSIONS_TABLENAME}
    WHERE name = '{metadata["name"]}';

    -- create procedures
    {procedures_code}

    -- add to extensions table

    INSERT INTO {WORKFLOWS_TEMP_PLACEHOLDER}.{EXTENSIONS_TABLENAME} (name, metadata, procedures)
    VALUES ('{metadata["name"]}', '{json.dumps(metadata)}', '{';'.join(procedures)}');
END;
'''

    return code


def deploy_bq(metadata, destination):
    print("Deploying extension to BigQuery...")
    destination = f"`{destination}`" if destination else bq_workflows_temp
    sql_code = create_sql_code_bq(metadata)
    sql_code = sql_code.replace(
        WORKFLOWS_TEMP_PLACEHOLDER,
        destination
    )
    if verbose:
        print(sql_code)
    query_job = bq_client().query(sql_code)
    query_job.result()
    print("Extension correctly deployed to BigQuery.")


def deploy_sf(metadata, destination):
    print("Deploying extension to SnowFlake...")
    destination = destination or sf_workflows_temp
    sql_code = create_sql_code_sf(metadata)
    sql_code = sql_code.replace(
        WORKFLOWS_TEMP_PLACEHOLDER,
        destination
    )
    if verbose:
        print(sql_code)
    cur = sf_client().cursor()
    cur.execute(sql_code)
    print("Extension correctly deployed to SnowFlake.")


def deploy(destination):
    metadata = create_metadata()
    if metadata["provider"] == "bigquery":
        deploy_bq(metadata, destination)
    else:
        deploy_sf(metadata, destination)


def _upload_test_table_bq(filename, component):
    dataset_id = os.getenv('BQ_TEST_DATASET')
    table_id = f"_test_{component['name']}_{os.path.basename(filename).split('.')[0]}"

    dataset_ref = bq_client().dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    job_config.autodetect = True
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

    with open(filename, "rb") as source_file:
        job = bq_client().load_table_from_file(
            source_file,
            table_ref,
            job_config=job_config,
        )
    try:
        job.result()
    except Exception as e:
        pass


def _upload_test_table_sf(filename, component):
    with open(filename) as f:
        data = [json.loads(l) for l in f.readlines()]
    table_id = f"_test_{component['name']}_{os.path.basename(filename).split('.')[0]}"
    create_table_sql = f'CREATE OR REPLACE TABLE {sf_workflows_temp}.{table_id} ('
    for key, value in data[0].items():
        if isinstance(value, int):
            data_type = 'NUMBER'
        elif isinstance(value, str):
            data_type = 'VARCHAR'
        elif isinstance(value, float):
            data_type = 'FLOAT'
        else:
            data_type = 'VARCHAR'
        create_table_sql += f'{key} {data_type}, '
    create_table_sql = create_table_sql.rstrip(', ')
    create_table_sql += ');\n'
    cursor = sf_client().cursor()
    cursor.execute(create_table_sql)
    for row in data:
        insert_sql = f"INSERT INTO {sf_workflows_temp}.{table_id} ({', '.join(row.keys())}) VALUES ({', '.join(['%s'] * len(row))})"
        cursor.execute(insert_sql, list(row.values()))
    cursor.close()


def _get_test_results(metadata, component):
    if metadata["provider"] == "bigquery":
        upload_function = _upload_test_table_bq
        workflows_temp = bq_workflows_temp
    else:
        upload_function = _upload_test_table_sf
        workflows_temp = sf_workflows_temp
    results = {}
    if component:
        components = [c for c in metadata["components"] if c["name"] == component]
    else:
        components = metadata["components"]
    current_folder = os.path.dirname(os.path.abspath(__file__))
    components_folder = os.path.join(current_folder, 'components')
    for component in components:
        component_folder = os.path.join(components_folder, component["name"])
        test_folder = os.path.join(component_folder, "test")
        # upload test tables
        for filename in os.listdir(test_folder):
            if filename.endswith(".ndjson"):
                upload_function(os.path.join(test_folder, filename), component)
        # run tests
        test_configuration_file = os.path.join(test_folder, "test.json")
        with open(test_configuration_file, "r") as f:
            test_configurations = json.load(f)
        tables = {}
        component_results = {}
        for test_configuration in test_configurations:
            param_values = []
            test_id = test_configuration["id"]
            component_results[test_id] = {}
            for inputparam in component["inputs"]:
                param_value = test_configuration['inputs'][inputparam['name']]
                if param_value is None:
                    param_values.append(None)
                else:
                    if inputparam["type"] == "Table":
                        tablename = f"'{workflows_temp}._test_{component['name']}_{param_value}'"
                        param_values.append(tablename)
                    elif inputparam["type"] in ["String", "Selection"]:
                        param_values.append(f"'{param_value}'")
                    else:
                        param_values.append(param_value)
            for outputparam in component["outputs"]:
                tablename = f"{workflows_temp}._table_{uuid4().hex}"
                param_values.append(f"'{tablename}'")
                tables[outputparam["name"]] = tablename
            param_values.append(False) # dry run
            query = f'''CALL {workflows_temp}.{component['procedureName']}(
                {','.join([str(p) if p is not None else 'null' for p in param_values])}
            );'''
            if verbose:
                print(query)
            if metadata["provider"] == "bigquery":
                query_job = bq_client().query(query)
                result = query_job.result()
                for output in component["outputs"]:
                    query = f"SELECT * FROM {tables[output['name']]}"
                    query_job = bq_client().query(query)
                    result = query_job.result()
                    rows = [{k: v for k,v in row.items()} for row in result]
                    component_results[test_id][output["name"]] = rows
            else:
                cur = sf_client().cursor()
                cur.execute(query)
                for output in component["outputs"]:
                    query = f"SELECT * FROM {tables[output['name']]}"
                    cur = sf_client().cursor()
                    cur.execute(query)
                    rows = cur.fetchall()
                    component_results[test_id][output["name"]] = rows
        results[component['name']] = component_results
    return results


def test(component):
    print("Testing extension...")
    metadata = create_metadata()
    current_folder = os.path.dirname(os.path.abspath(__file__))
    components_folder = os.path.join(current_folder, 'components')
    deploy(None)
    results = _get_test_results(metadata, component)
    for component in metadata["components"]:
        component_folder = os.path.join(components_folder, component["name"])
        for test_id, outputs in results[component["name"]].items():
            test_folder = os.path.join(component_folder, "test", "fixtures")
            test_filename = os.path.join(test_folder, f"{test_id}.json")
            with open(test_filename, "r") as f:
                expected = json.load(f)
                for output_name, output in outputs.items():
                    output = json.loads(json.dumps(output))
                    assert \
                        sorted(expected[output_name], key=json.dumps) == sorted(output, key=json.dumps), \
                        f"Test '{test_id}' failed for component {component['name']} and table {output_name}."
    print("Extension correctly tested.")


def capture(component):
    print("Capturing fixtures... ")
    metadata = create_metadata()
    current_folder = os.path.dirname(os.path.abspath(__file__))
    components_folder = os.path.join(current_folder, 'components')
    deploy(None)
    results = _get_test_results(metadata, component)
    for component in metadata["components"]:
        component_folder = os.path.join(components_folder, component["name"])
        for test_id, outputs in results[component["name"]].items():
            test_folder = os.path.join(component_folder, "test", "fixtures")
            os.makedirs(test_folder, exist_ok=True)
            test_filename = os.path.join(test_folder, f"{test_id}.json")
            with open(test_filename, "w") as f:
                f.write(json.dumps(outputs, indent=2))
    print("Fixtures correctly captured.")


def package():
    print("Packaging extension...")
    current_folder = os.path.dirname(os.path.abspath(__file__))
    metadata = create_metadata()
    sql_code = create_sql_code_bq(
        metadata) if metadata["provider"] == "bigquery" else create_sql_code_sf(metadata)
    package_filename = os.path.join(current_folder, 'extension.zip')
    with zipfile.ZipFile(package_filename, "w") as z:
        with z.open("metadata.json", "w") as f:
            f.write(json.dumps(add_namespace_to_component_names(metadata), indent=2).encode("utf-8"))
        with z.open("extension.sql", "w") as f:
            f.write(sql_code.encode("utf-8"))

    print(f"Extension correctly packaged to '{package_filename}' file.")

def _param_type_to_bq_type(param_type):
    if param_type in ["Table", "String", "Selection", "Column"]:
        return ["STRING"]
    elif param_type == "Number":
        return ["INT64", "FLOAT64"]
    elif param_type == "Boolean":
        return ["BOOL", "BOOLEAN"]
    else:
        raise ValueError(f"Parameter type '{param_type}' not supported")

def _param_type_to_sf_type(param_type):
    if param_type in ["Table", "String", "Selection", "Column"]:
        return ["STRING", "VARCHAR"]
    elif param_type == "Number":
        return ["INTEGER", "FLOAT"]
    elif param_type == "Boolean":
        return ["BOOL"]
    else:
        raise ValueError(f"Parameter type '{param_type}' not supported")

def check():
    print("Checking extension...")
    current_folder = os.path.dirname(os.path.abspath(__file__))
    metadata = create_metadata()
    components_folder = os.path.join(current_folder, 'components')
    for component in metadata["components"]:
        component_folder = os.path.join(components_folder, component["name"])
        procedure_file = os.path.join(
            component_folder, "src", "procedure.sql")
        with open(procedure_file, "r") as f:
            procedure_code = f.read()
            assert f"CREATE OR REPLACE PROCEDURE {WORKFLOWS_TEMP_PLACEHOLDER}.{component['procedureName']}" in procedure_code, \
                f"Procedure '{WORKFLOWS_TEMP_PLACEHOLDER}.{component['procedureName']}' not found in component '{component['name']}'"
            # Extract parameters using regex
            pattern = r'CREATE OR REPLACE PROCEDURE.*?\(([^()]*?)\)'
            match = re.search(pattern, procedure_code, re.DOTALL)
            # Get first group of the match and split by comma
            parameters = match.group(1).split(',')
            if len(parameters) == 1 and parameters[0].strip() == '':
                parameters = []
            # Remove starting and trailing spaces
            parameters = [param.strip().lower() for param in parameters]
            parameter_names = [p.split()[0] for p in parameters]
            parameter_types = [p.split()[1].upper() for p in parameters]
            type_function = _param_type_to_bq_type if metadata["provider"] == "bigquery" else _param_type_to_sf_type
            metadata_parameter_names = \
                    [p["name"] for p in component["inputs"]] + \
                    [p["name"] for p in component["outputs"]] + \
                    ["dry_run"]
            metadata_parameter_types = \
                    [type_function(p["type"]) for p in component["inputs"]] + \
                    [type_function(p["type"])  for p in component["outputs"]] + \
                    [type_function("Boolean")]
            assert parameter_names == metadata_parameter_names, \
                f"Parameters in procedure '{WORKFLOWS_TEMP_PLACEHOLDER}.{component['procedureName']}' do not match with metadata in component '{component['name']}'"
            for i in range(len(parameter_types) - 1):
                assert parameter_types[i] in metadata_parameter_types[i], \
                    f"Parameter types in procedure '{WORKFLOWS_TEMP_PLACEHOLDER}.{component['procedureName']}' do not match with metadata in component '{component['name']}'"
    print("Extension correctly checked. No errors found.")

parser = argparse.ArgumentParser()
parser.add_argument('action', nargs=1, type=str, choices=[
                    'package', 'deploy', 'test', 'capture', 'check'])
parser.add_argument('-c','--component', help='Choose one component', type=str)
parser.add_argument('-d','--destination', help='Choose an specific destination', type=str, required="deploy" in argv)
parser.add_argument('-v','--verbose', help='Verbose mode', action='store_true')
args = parser.parse_args()
action = args.action[0]
verbose = args.verbose
if args.component and action not in ['capture', 'test']:
    parser.error("Component can only be used with 'capture' and 'test' actions")
if args.destination and action not in ['deploy']:
    parser.error("Destination can only be used with 'deploy' action")
if action == 'package':
    package()
elif action == 'deploy':
    deploy(args.destination)
elif action == 'test':
    test(args.component)
elif action == 'capture':
    capture(args.component)
elif action == 'check':
    check()
