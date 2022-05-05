# Repo for Practicing MLflow


### MLflow Terminology

- `backend store` - location where metrics and params are stored
- `artifact store` - files associated with a run. Could include plots, data used to train the model, the model artifact itself
- `flavor` - framework used to build the model. There are "standard" flavors with built-in support from MLflow (see [here](https://www.mlflow.org/docs/latest/models.html#built-in-model-flavors) for this) and the option to bring your own (often referred to as `pyfunc` flavor) 


### Setting up the Model Registry Locally

When using clicking on "Models" tab through the mlflow UI when the "backend store" and the "artifacts store" are both using the `./mlruns`, this error is shown: 

```INVALID_PARAMETER_VALUE: Model registry functionality is unavailable; got unsupported URI './mlruns' for model registry data storage. Supported URI schemes are: ['postgresql', 'mysql', 'sqlite', 'mssql']. See https://www.mlflow.org/docs/latest/tracking.html#storage for how to run an MLflow server against one of the supported backend storage locations.``` 

The same is received when trying to include the `registered_model_name` in the `log_model_command`

To setup the pre-requisites required for the model registry to work, going to setup a local SQLite DB called `mlruns.db` and use this as the backend store. Steps to do this:

- Install SQLite using `brew install sqlite`
- `sqlite3 mlruns.db` -> `.database` -> `.exit` (should see DB created in directory specified)
- Start MLFlow server using DB for backend store using command `mlflow server --host 0.0.0.0 --backend-store-uri sqlite:////<absolute file path> --default-artifact-root file:///<file path to artifacts feed>` - note the four slashes in the sqlite connection string. Received the following error when using three:
``` 
WARNING mlflow.store.db.utils: SQLAlchemy engine could not be created. The following exception is caught.
(sqlite3.OperationalError) unable to open database file
```
- The Models tab should no longer give the error in the UI when going to `http://0.0.0.0:5000/#/model`

#### Registering the Model
- In the file being used for logging the data using MLFlow, set the tracking uri at the start using:
`mlflow.set_tracking_uri("http://localhost:5000")`
- To register the model, simply add the `registered_model_name=<model_name>` to the `log_model` command. Note in this approach, there isn't the option to add description, tags or stage. Stage can be added after, but can't find a programatic way of adding description and tags after this command has been run
- An alternative to the above, and potentially a more complete way of registering the model is 
1. Create an MLFlow client `client = mlflow.tracking.MlflowClient()`
2. Use the client rather than the `log_model` to register the model initially `client.create_registered_model(name=<model_name>, tags=<model_tags>, description=<model_description>)`. The model name needs to be unique (can`t run this command to overwrite the tags or description). This will register the model with tags and description, but no version or reference to the run
3. To add a version of the model, this can be done using the `log_model` command as described earlier. Update - this doesn't have tags or description for the model by default. The `create_model_version` command is able to do this `create_model_version(name=<model name>, source=<model_path>, tags=<tags>, description=<model_description>)`
4. To add the stage to the model, can use the client again with the command `client.transition_model_version_stage(name=<registered_model_name>, version=<model_version>, stage=<stage_name>)`

#### Transition the Model Stage Programatically
```
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(name=<registered_model_name>, version=1, stage=<stage_name>)
```

#### Serving the Registered Model Locally
`mlflow models serve -m "models:/<model name>/<stage>" --env-manager local --port 5001`

*Note - can use version instead of stage when serving the model*

### Moving Artifact Store to Remote Storage

- Keeping the artifacts on a local machine isn't suitable for a collaborative environment. MLFlow supports a [variety of different storage types](https://www.mlflow.org/docs/latest/tracking.html#artifact-stores). Going to use Azure Blob Storage for the time being as the artifact store 

Following the [MLflow documentation](https://www.mlflow.org/docs/latest/tracking.html#azure-blob-storage) to use Azure Blob Storage as the artifact store

- "MLflow expects Azure Storage access credentials in the AZURE_STORAGE_CONNECTION_STRING, AZURE_STORAGE_ACCESS_KEY environment variables or having your credentials configured such that the DefaultAzureCredential()". Setting the AZURE_STORAGE_CONNECTION_STRING using `export AZURE_STORAGE_CONNECTION_STRING=<value>`

- Adding `azure-storage-blob` to the requirements

- Running the MLFlow server specifying the Blob Storage as the artifact store:
`mlflow server --host 0.0.0.0 --backend-store-uri sqlite:////<absolute file path> --default-artifact-root wasbs://<container>@<storage-account>.blob.core.windows.net/<path>`

- Following the same steps as in the `Registering the Model` section earlier in the README achieves writing the artifacts such as the model binary and data to the artifact store

### Moving Backend Store to Remote DB

- Similar to the artifact store, having a local DB isn't scalable. MLFlow gives the option to set the backend store using the SQL dialects mysql, mssql, sqlite, and postgresql

- Going to setup the DB to a PostgreSQL flexible server in Azure:
`mlflow server --host 0.0.0.0 --backend-store-un
ri postgresql://'<username>':'<password>'@<host>:<port>/<database> --default-artifact-root wasbs://<container>@<storage-account>.blob.core.windows.net/<path>`

- When running experiments with the tracking tracking URI set to the MLServer, parameters and metrics from the run are stored in the remote DB

- Note - was required to install `psycopg2-binary` first

### Containarise MLflow Server

- Rather than hosting the MLflow server locally, requiring every user to spin it up locally in the terminal, requiring to add some credentials for auth, want to host it in the cloud. One way of doing this is through containerisation using a tool such as Docker.

- Example `Dockerfile` which can be used to dockerise the MLflow server:
```
FROM python:3.8.0

RUN pip install mlflow azure-storage-blob psycopg2-binary
RUN mkdir /mlflow/

EXPOSE 5000

## - Note need to set AZURE_STORAGE_CONNECTION_STRING environment variable to auth against Blob storage
CMD mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --default-artifact-root wasbs://mlflow-model-registry@${BLOB_STORAGE} \
    --backend-store-uri postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_NAME}.postgres.database.azure.com:5432/postgres
```
- The environment variables specified in the Dockerfile should be injected when the container is run. This can be done by defining a `.envfile` and populating it:

```
DB_USERNAME=<username>
DB_PASSWORD=<db_password>
DB_NAME=<db_name>
AZURE_STORAGE_CONNECTION_STRING=<Azure Storage Connection Key>
BLOB_STORAGE=<Blob Storage URL>
```
- This can be used at run time by specifying `docker run --env-file <path>/.envfile <image name>:<image tag>`

- Notes - [AWS tutorial on containerising MLflow server](https://aws.amazon.com/blogs/machine-learning/managing-your-machine-learning-lifecycle-with-mlflow-and-amazon-sagemaker/)
- [Passing in secure values into Azure Container Instance](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-environment-variables#secure-values)

### Gotchas
- When making changes the the `default-artifact-root` for storing artifacts associated with runs, the change in location only happens for new experiments. For existing experiments, such as ones where the artifacts were being written to the `/mlruns` directory, changes the the `default-artifact-root` defined when running the mlflow server will not change where the artifacts are being written for existing runs

