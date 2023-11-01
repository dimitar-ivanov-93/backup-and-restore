# Wiki.js/Postgres Backup and Restore
This repository contains a Python script and associated files for automating the backup and restore process of a Wiki.js application with Postgres storage deployed in a Kubernetes cluster in Azure.

## Files
db.py: This is the main Python script that handles the creation, monitoring, and deletion of Kubernetes jobs for database backup and restore.
dump.sh: This shell script performs the database backup operation.
restore.sh: This shell script performs the database restore operation.
view.sh: This shell script lists all the backups available in the Azure Storage account.
backup.yaml: This is a Kubernetes CronJob configuration file for scheduling the backup jobs.
Dockerfile: This file is used to build the Docker image that runs the backup and restore jobs.
requirements.txt: The Python requirements for the environment you are working in.
## Usage
Set the environment variables JOB_NAME and NAMESPACE to the desired Kubernetes job name and namespace respectively.
Run the db.py script with the name of the script to run (restore, or view) as the first argument. If running the restore script, also provide the name of the backup file to restore from as the second argument.
Example:
```
pip install -r requirements.txt
export NAMESPACE={your_namespace}
export JOB_NAME={your_desired_job_name}
kubectl create secret generic azure-storage-credentials --from-literal=accountName={your_account_name} --from-literal=accountKey={your_account_key} -n {your_namespace}
kubectl create secret generic db-credentials --from-literal=username={your_db_username} --from-literal=password={your_db_password} -n {your_namespace}
kubectl apply -f backup.yaml -n {your_namespace}
python db.py restore wiki-db-20220101-000000.sql
python db.py view
```
## Requirements
Python 3.6+
Kubernetes Python client
Azure CLI
Kubernetes cluster with a running instance of Wiki.js and Postgres
Azure Storage account
## Backup and Restore Strategy
The backup process is automated using a Kubernetes CronJob that runs the dump.sh script every day at 2AM. This script uses the pg_dump command to create a backup of the Postgres database and then uploads the backup file to the Azure Storage account using the az storage file upload command.

The restore process is initiated by running the db.py script with the restore argument and the name of the backup file to restore from. This script creates a Kubernetes job that runs the restore.sh script. This script downloads the backup file from the Azure Storage account using the az storage file download command, drops the existing Postgres database, creates a new one, and then restores the database from the backup file using the pg_restore command.

The view.sh script can be used to list all the backups available in the Azure Storage account.

## Notes
The db.py script monitors the status of the Kubernetes jobs and retries them up to 5 times if they fail.
The Docker image used for the backup and restore jobs is built from the provided Dockerfile and includes the Postgres client and Azure CLI tools.

## Contact
For any queries or support, please email at [mitko930119@gmail.com].

## Acknowledgements
This project is based on open source/free tooling and is designed to be easily reproducible for other clients using the same Wiki.js/Postgres setup.

## Disclaimer
Use this script at your own risk. The author is not responsible for any data loss or other damages caused by the use of this script.

## TODO
Add error handling for Azure CLI commands.
Add support for customizing the backup schedule.
Add support for other cloud storage providers.
Make the overall process more flexible.
Create UI for better customer experience.
