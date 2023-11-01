from kubernetes import client, config
from time import sleep
from kubernetes.client.rest import ApiException
import argparse, os

JOB_NAME = os.getenv('JOB_NAME')
NAMESPACE = os.getenv('NAMESPACE')
MAX_RETRIES = 5

def create_job_object(script_name, script_arg=None):
    command = ["/bin/bash", f"/scripts/{script_name}.sh"]
    env_vars = [
        client.V1EnvVar(
            name="PGUSER",
            value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(
                    name="db-credentials",
                    key="username"
                )
            )
        ),
        client.V1EnvVar(
            name="PGPASSWORD",
            value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(
                    name="db-credentials",
                    key="password"
                )
            )
        ),
        client.V1EnvVar(
            name="AZURE_STORAGE_ACCOUNT",
            value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(
                    name="azure-storage-credentials",
                    key="accountName"
                )
            )
        ),
        client.V1EnvVar(
            name="AZURE_STORAGE_KEY",
            value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(
                    name="azure-storage-credentials",
                    key="accountKey"
                )
            )
        )
    ]
    if script_arg:
        env_vars.append(client.V1EnvVar(name="SQL_FILE", value=script_arg))
    container = client.V1Container(
        name="backup-manipulations",
        image="mitko9301/azuretest:latest",
        command=command,
        env=env_vars
    )

    # Create and configure a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "backup-manipulations"}),
        spec=client.V1PodSpec(restart_policy="OnFailure", containers=[container])
    )

    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template,
        backoff_limit=4
    )

    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=JOB_NAME),
        spec=spec
    )

    return job


def create_job(api_instance, job, args):
    try:
        api_instance.create_namespaced_job(
            body=job,
            namespace=NAMESPACE or "wiki")
        print(f"Job created. Please wait for results.")
        get_job_status(api_instance, args)
    except ApiException as e:
        print(f"Exception when calling BatchV1Api->create_namespaced_job: {e}")


def get_job_status(api_instance, args):
    retries = 0
    while retries < MAX_RETRIES:
        api_response = api_instance.read_namespaced_job_status(
            name=JOB_NAME,
            namespace=NAMESPACE or "wiki")
        if api_response.status.succeeded is not None:
            print_job_logs()
            return
        elif api_response.status.failed is not None:
            retries += 1
            print(f"Job failed. Retrying ({retries}/{MAX_RETRIES})...")
            delete_job(api_instance)
            create_job(api_instance, create_job_object(args.script_name, args.script_arg))
        sleep(0.5)
    print(f"Job failed after {MAX_RETRIES} retries.")


def print_job_logs():
    core_v1 = client.CoreV1Api()
    try:
        pod_list = core_v1.list_namespaced_pod(NAMESPACE, label_selector="app=backup-manipulations")
        for pod in pod_list.items:
            print(core_v1.read_namespaced_pod_log(pod.metadata.name, NAMESPACE))
    except ApiException as e:
        print(f"Exception when calling CoreV1Api->read_namespaced_pod_log: {e}")


def delete_job(api_instance):
    api_instance.delete_namespaced_job(
        name=JOB_NAME,
        namespace=NAMESPACE or "wiki",
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    print(f"Job deleted successfully.")


def job_exists(api_instance):
    try:
        api_instance.read_namespaced_job_status(
            name=JOB_NAME,
            namespace=NAMESPACE)
        return True
    except ApiException as e:
        if e.status == 404:
            return False
        else:
            raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("script_name", help="Name of the script to run")
    parser.add_argument("script_arg", nargs='?', default=None, help="Optional argument for the script")
    args = parser.parse_args()
    if args.script_name not in ["dump", "restore", "view"]:
        parser.error("Invalid script name. Must be 'dump', 'restore', or 'view'.")
    
    if args.script_name == "restore" and args.script_arg is None:
        parser.error("the following arguments are required: script_arg")

    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    job = create_job_object(args.script_name, args.script_arg)
    create_job(batch_v1, job, args)
    delete_job(batch_v1)


if __name__ == '__main__':
    main()