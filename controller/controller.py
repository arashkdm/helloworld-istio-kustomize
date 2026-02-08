import os
import datetime
from kubernetes import client, config, watch

NAMESPACE = os.getenv("CONFIG_NAMESPACE", "default")
LABEL_SELECTOR = os.getenv("LABEL_SELECTOR", "app=helloworld")
DEPLOYMENT_BASENAME = os.getenv("DEPLOYMENT_BASENAME", "helloworld")

def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def main():
    config.load_incluster_config()

    v1 = client.CoreV1Api()
    apps = client.AppsV1Api()
    w = watch.Watch()

    print("controller started", flush=True)

    for event in w.stream(
        v1.list_namespaced_config_map,
        namespace=NAMESPACE,
        label_selector=LABEL_SELECTOR,
    ):
        if event["type"] != "MODIFIED":
            continue

        cm = event["object"]
        labels = cm.metadata.labels or {}
        env_value = labels.get("env")

        if env_value not in ("test", "prod"):
            continue

        deploy_name = f"{DEPLOYMENT_BASENAME}-{env_value}"

        print(f"configmap changed for env={env_value}, restarting {deploy_name}", flush=True)

        try:
            apps.patch_namespaced_deployment(
                name=deploy_name,
                namespace=NAMESPACE,
                body={
                    "spec": {
                        "template": {
                            "metadata": {
                                "annotations": {
                                    "kubectl.kubernetes.io/restartedAt": now()
                                }
                            }
                        }
                    }
                }
            )
        except client.exceptions.ApiException as e:
            print(f"failed to restart deployment {deploy_name}: {e}", flush=True)

if __name__ == "__main__":
    main()

