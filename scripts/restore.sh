#!/bin/bash
set -e
az storage file download --path $SQL_FILE --share-name backups --account-name $AZURE_STORAGE_ACCOUNT --account-key $AZURE_STORAGE_KEY
dropdb -h db-postgresql -U $PGUSER -f -e wiki-db
createdb -h db-postgresql -U $PGUSER -e wiki-db

# psql -h db-postgresql -U $PGUSER -c "CREATE DATABASE wiki-db;"
PGPASSWORD=$PGPASSWORD pg_restore -v --clean --if-exists -h db-postgresql -U $PGUSER -d wiki-db $SQL_FILE