# Workflows extensions template repository

> **Warning** At the moment it only supports **BigQuery** and **Snowflake**.

Use this repository template to create a new extension for CARTO Workflows.

## Data Warehouse configuration

For running the `deploy`, `test` and `capture` scripts, you need to configure the access to the data warehouse where your extension is supposed to run. To do so, rename the `.env.template` file in the root of the repository to `.env` and edit it with the appropriate values.

If you are creating a BigQuery extension, install the Google Cloud SDK and run the following in your console to authenticate:

`$ gcloud auth application-default login`

## Implementing the extension

Follow these steps to implement your own extension, test and capture are optional steps but highly recommended.

1. Create a new repository based on this one.
2. Install the requirements needed by the repository scripts. Python 3 is required to run the repository scripts:

    `$ pip install -r ./requirements.txt`

3. Edit the `metadata.json` file in the root folder of the repo so it contains the correct information for the extension.
4. Copy the `template` folder and rename it with the desired internal name (i.e. mycomponent) of the component to add. It is important to avoid `-` in the name of the folder to  avoid errors in the data warehouse.
5. Edit the `procedure.sql` file in that copied folder to define the logic of the new component. For more details, see [here](./doc/procedure.md)
6. Edit the component metadata file. For more information, see [here](./doc/component_metadata.md)
7. (Optional) Setup the elements in the `test` folder to define how the test should be run to verify that the component is correctly working. Use the `test.json` file to define the test case, and add the tables that you need for your test as `.ndjson` files in that same folder. You can refer to those files as input values using the filename without the extension (see the provided example with the `table1.ndjson` file)
8. Write the component documentation in the `README` file.
9. Repeat steps 3-7 as many times as components will be included in the extension.
10. Use the `check` script to ensure that the extension is correctly defined.

    `$ python carto_extension.py check`

11. (Optional) Run the `capture` script to create the test fixtures from the results of running your components in the corresponding datawarehouse.

    `$ python carto_extension.py capture`

12. (Optional) Check the created files to ensure that the output is as expected. From that point, you can now run the `test` script to run tests and check if they match the captured outputs, whenever you change the implementation of any of the components.

    `$ python carto_extension.py test`

13. Run the `package` script to create the `extension.zip` file. It will create a zip file with the extension code and metadata.

    `$ python carto_extension.py package`

Now you are ready to distribute your extension.

The `capture` and `test` actions support a `--component` parameter, which will make them run only for the selected component, instead of all the ones in the extension.

`$ python carto_extension.py capture --component=mycomponent`

## Deploying the extension

You can deploy the extension in a given destination (project.dataset in the case of BigQuery, database.schema in the case of Snowflake), using the `deploy` command with the following syntax:

`$ python carto_extension.py deploy --destination=[myproject.mydataset]`

## CI configuration

The template includes a GitHub workflow to run the extension test suite when new changes are pushed to the repository (provided that the `capture` script has been run and test fixtures have been captured). GitHub secrets must be configured in order to have the workflow correctly running. Check the `CI_test.yml` file for more information.

## Commands and parameters
* `check`: Checks the extension code definition and metadata.
* `capture`: Captures the output of the components to use as test fixtures.
  * `--component`: The component to capture.
  * `--verbose`: Show more information about the capture process.
* `test`: Runs the tests for the components.
  * `--component`: The component to test.
  * `--verbose`: Show more information about the test process.
* `deploy`: Deploys the extension to the data warehouse.
  * `--destination`: The destination where the extension will be deployed in the data warehouse.
  * `--verbose`: Show more information about the deployment process.
* `package`: Packages the extension into a zip file.
  * `--verbose`: Show more information about the packaging process.
