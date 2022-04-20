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
3. To add a version of the model, this can be done using the `log_model` command as described earlier
4. To add the stage to the model, can use the client again with the command `client.transition_model_version_stage(name=<registered_model_name>, version=<model_version>, stage=<stage_name>)`

#### Transition the Model Stage Programatically
```
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(name=<registered_model_name>, version=1, stage=<stage_name>)
```

#### Serving the Registered Model Locally
`mlflow models serve -m "models:/<model name>/<stage>" --env-manager local --port 5001`

*Note - can use version instead of stage when serving the model*

### Gotchas

