import requests
import json
import time

# FMC credentials and URL
FMC_URL = "https://<FMC_IP>/api/fmc_platform/v1/auth/generatetoken"
USERNAME = "<your_username>"
PASSWORD = "<your_password>"

# Headers
HEADERS = {
    'Content-Type': 'application/json'
}

# Function to obtain a token
def get_token():
    response = requests.post(FMC_URL, auth=(USERNAME, PASSWORD), headers=HEADERS, verify=False)
    response.raise_for_status()
    headers = response.headers
    token = headers.get('X-auth-access-token', default=None)
    domain_uuid = headers.get('DOMAIN_UUID', default=None)
    if token is None:
        raise Exception("Failed to obtain token")
    return token, domain_uuid

# Function to trigger policy deployment
def deploy_policy(token, domain_uuid, policy_name):
    # Get policy by name
    policy_url = f"https://<FMC_IP>/api/fmc_config/v1/domain/{domain_uuid}/policy/accesspolicies?name={policy_name}"
    headers = {
        'Content-Type': 'application/json',
        'X-auth-access-token': token
    }
    response = requests.get(policy_url, headers=headers, verify=False)
    response.raise_for_status()
    policies = response.json().get('items', [])
    if not policies:
        raise Exception(f"No policy found with name {policy_name}")
    policy_id = policies[0]['id']

    # Trigger deployment
    deployment_url = f"https://<FMC_IP>/api/fmc_config/v1/domain/{domain_uuid}/deployment/deployments"
    payload = {
        "type": "DeploymentRequest",
        "version": "1.0",
        "forceDeploy": True,
        "ignoreWarning": True,
        "deviceList": [],  # List of devices to deploy to (empty means all devices in policy)
        "policyList": [
            {
                "type": "AccessPolicy",
                "id": policy_id
            }
        ]
    }
    response = requests.post(deployment_url, headers=headers, data=json.dumps(payload), verify=False)
    response.raise_for_status()
    return response.json()

# Main script
if __name__ == "__main__":
    try:
        token, domain_uuid = get_token()
        
        # Name of the policy to be deployed
        policy_name = "TestPolicy"

        # Trigger policy deployment
        deployment_response = deploy_policy(token, domain_uuid, policy_name)
        print(f"Deployment triggered: {deployment_response}")

    except Exception as e:
        print(f"Error: {e}")
