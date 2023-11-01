#!/bin/bash
az storage file list --share-name backups --account-name $AZURE_STORAGE_ACCOUNT --account-key $AZURE_STORAGE_KEY --output table
