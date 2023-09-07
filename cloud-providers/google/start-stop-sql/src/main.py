import base64
import functions_framework
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

credentials = GoogleCredentials.get_application_default()
FMSG_NOT_RUNNABLE = "Instance is not in RUNNABLE STATE"
FMSG_ALREADY_CONFIGURED = """
Instance is already configured with the desired policy: {policy}
"""
FMSG_CONFIGURED = """
Instance {instance} is now configured with the desired policy: {policy}.
"""


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def process_pubsub(cloud_event):
    msg = cloud_event.data["message"]
    msg = base64.b64decode(msg).decode("utf-8")
    assert isinstance(msg, dict), "message not found"

    # Get all the needed data
    instances = msg["instances"]
    project_id = msg["project_id"]
    policy = msg["policy"]

    success_list = []
    failure_list = []

    if isinstance(instances, list):
        print(f"Patching instances: {instances}.")
        for i in instances:
            if patch_instance(project_id, i, policy):
                success_list.append(i)
            else:
                failure_list.append(i)
    else:
        return '{"error": "Instance must be a list of strings."}'
    return f"{{'success': {success_list}, 'failure': {failure_list}}}"


def patch_instance(project_id, instance, desired_policy):
    try:
        service = discovery.build(
            "sqladmin", "v1beta4", credentials=credentials)

        request = service.instances().get(project=project_id, instance=instance)
        response = request.execute()

        current_state = str(response["state"])
        current_policy = str(response["settings"]["activationPolicy"])

        if current_state != "RUNNABLE":
            print(FMSG_NOT_RUNNABLE)
        else:
            if desired_policy != current_policy:
                instance_body = {"settings": {
                    "activationPolicy": desired_policy}}
                request = service.instances().patch(
                    project=project_id, instance=instance, body=instance_body
                )
                response = request.execute()
                print(
                    FMSG_CONFIGURED.format(
                        instance=instance, policy=desired_policy)
                )
            else:
                print(FMSG_ALREADY_CONFIGURED.format(policy=desired_policy))
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False
