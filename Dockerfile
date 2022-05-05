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

