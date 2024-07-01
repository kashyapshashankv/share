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

# Function to create a host object
def create_host_object(token, domain_uuid):
    url = f"https://<FMC_IP>/api/fmc_config/v1/domain/{domain_uuid}/object/hosts"
    headers = {
        'Content-Type': 'application/json',
        'X-auth-access-token': token
    }
    payload = {
        "name": "TestHost",
        "type": "Host",
        "value": "192.168.1.1"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

# Function to create a network group
def create_network_group(token, domain_uuid, host_object_id):
    url = f"https://<FMC_IP>/api/fmc_config/v1/domain/{domain_uuid}/object/networkgroups"
    headers = {
        'Content-Type': 'application/json',
        'X-auth-access-token': token
    }
    payload = {
        "name": "TestNetworkGroup",
        "type": "NetworkGroup",
        "objects": [
            {
                "type": "Host",
                "id": host_object_id
            }
        ]
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

# Main script
if __name__ == "__main__":
    try:
        token, domain_uuid = get_token()
        host_object = create_host_object(token, domain_uuid)
        print(f"Host Object Created: {host_object}")

        network_group = create_network_group(token, domain_uuid, host_object['id'])
        print(f"Network Group Created: {network_group}")
    except Exception as e:
        print(f"Error: {e}")
