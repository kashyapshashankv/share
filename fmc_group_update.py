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

# Function to get object by name
def get_object_by_name(token, domain_uuid, object_type, object_name):
    url = f"https://<FMC_IP>/api/fmc_config/v1/domain/{domain_uuid}/object/{object_type}?name={object_name}"
    headers = {
        'Content-Type': 'application/json',
        'X-auth-access-token': token
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    objects = response.json().get('items', [])
    if not objects:
        raise Exception(f"No object found with name {object_name}")
    return objects[0]

# Function to get group by name
def get_group_by_name(token, domain_uuid, group_name):
    url = f"https://<FMC_IP>/api/fmc_config/v1/domain/{domain_uuid}/object/networkgroups?name={group_name}"
    headers = {
        'Content-Type': 'application/json',
        'X-auth-access-token': token
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    groups = response.json().get('items', [])
    if not groups:
        raise Exception(f"No group found with name {group_name}")
    return groups[0]

# Function to update the group with new objects
def update_group(token, domain_uuid, group_id, objects_to_add):
    url = f"https://<FMC_IP>/api/fmc_config/v1/domain/{domain_uuid}/object/networkgroups/{group_id}"
    headers = {
        'Content-Type': 'application/json',
        'X-auth-access-token': token
    }
    # Get the current group details
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    group = response.json()
    
    # Add the new objects to the group
    group['objects'].extend(objects_to_add)
    
    # Update the group
    response = requests.put(url, data=json.dumps(group), headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

# Main script
if __name__ == "__main__":
    try:
        token, domain_uuid = get_token()

        # Names of objects and group
        group_name = "TestNetworkGroup"
        object_names = ["TestHost1", "TestHost2"]

        # Get the group details
        group = get_group_by_name(token, domain_uuid, group_name)
        group_id = group['id']

        # Get the object details
        objects_to_add = []
        for object_name in object_names:
            obj = get_object_by_name(token, domain_uuid, 'hosts', object_name)
            objects_to_add.append({"type": obj["type"], "id": obj["id"]})

        # Update the group with new objects
        updated_group = update_group(token, domain_uuid, group_id, objects_to_add)
        print(f"Updated Group: {updated_group}")
    except Exception as e:
        print(f"Error: {e}")
