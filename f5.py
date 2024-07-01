import requests
import json

# Replace with your F5 BIG-IP device details
f5_host = 'https://<F5_HOST>'
username = '<USERNAME>'
password = '<PASSWORD>'

# Disable warnings for self-signed certificates (optional)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Function to create a VLAN
def create_vlan(vlan_name, vlan_id, interfaces):
    url = f'{f5_host}/mgmt/tm/net/vlan'

    headers = {
        'Content-Type': 'application/json'
    }

    vlan_payload = {
        'name': vlan_name,
        'tag': vlan_id,
        'interfaces': interfaces
    }

    response = requests.post(url, auth=(username, password), headers=headers, json=vlan_payload, verify=False)

    if response.status_code == 200:
        print(f'VLAN {vlan_name} created successfully.')
    else:
        print(f'Failed to create VLAN {vlan_name}. Status code: {response.status_code}, Response: {response.text}')

# Example usage
vlan_name = 'exampleVLAN'
vlan_id = 100
interfaces = [{'name': '1.1'}]

create_vlan(vlan_name, vlan_id, interfaces)
