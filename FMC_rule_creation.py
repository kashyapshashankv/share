import requests
import json

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

# Function to create a firewall rule
def create_firewall_rule(token, domain_uuid, policy_id, rule_name, source, destination, action):
    url = f"https://<FMC_IP>/api/fmc_config/v1/domain/{domain_uuid}/policy/accesspolicies/{policy_id}/accessrules"
    headers = {
        'Content-Type': 'application/json',
        'X-auth-access-token': token
    }
    payload = {
        "name": rule_name,
        "action": action,
        "enabled": True,
        "sourceNetworks": {
            "objects": source
        },
        "destinationNetworks": {
            "objects": destination
        },
        "type": "AccessRule"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

# Function to trigger policy deployment
def deploy_policy(token, domain_uuid, policy_id):
    deployment_url = f"https://<FMC_IP>/api/fmc_config/v1/domain/{domain_uuid}/deployment/deployments"
    headers = {
        'Content-Type': 'application/json',
        'X-auth-access-token': token
    }
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
        
        # Policy ID and rule details
        policy_id = "<your_policy_id>"
        rule_name = "Allow_HTTP"
        source = [{"type": "Network", "name": "any"}]  # Example source network
        destination = [{"type": "Network", "name": "any"}]  # Example destination network
        action = "ALLOW"
        
        # Create firewall rule
        rule = create_firewall_rule(token, domain_uuid, policy_id, rule_name, source, destination, action)
        print(f"Firewall Rule Created: {rule}")

        # Deploy the policy
        deployment_response = deploy_policy(token, domain_uuid, policy_id)
        print(f"Deployment triggered: {deployment_response}")

    except Exception as e:
        print(f"Error: {e}")
