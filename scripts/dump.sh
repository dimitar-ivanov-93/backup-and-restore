#!/bin/bash
filename="wiki-db-$(date +%Y%m%d-%H%M%S).sql"
PGPASSWORD=$PGPASSWORD pg_dump -Fc -b -h db-postgresql -U $PGUSER -d wiki-db > $filename
az storage file upload --source $filename --share-name backups --account-name $AZURE_STORAGE_ACCOUNT --account-key $AZURE_STORAGE_KEY