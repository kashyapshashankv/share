import requests
import json

# Replace these variables with your actual F5 device details
f5_host = "https://your-f5-device"
username = "your-username"
password = "your-password"
vcmp_guest_name = "your-vcmp-guest-name"
vlan_name = "your-new-vlan-name"
vlan_tag = 100  # VLAN ID (tag)

# Disable SSL warnings for self-signed certificates (not recommended for production)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Authenticate and get a token
auth_url = f"{f5_host}/mgmt/shared/authn/login"
auth_payload = {
    "username": username,
    "password": password,
    "loginProviderName": "tmos"
}
response = requests.post(auth_url, json=auth_payload, verify=False)
response.raise_for_status()
token = response.json()['token']['token']

headers = {
    "Content-Type": "application/json",
    "X-F5-Auth-Token": token
}

# Create a new VLAN
vlan_url = f"{f5_host}/mgmt/tm/net/vlan"
vlan_payload = {
    "name": vlan_name,
    "tag": vlan_tag
}
response = requests.post(vlan_url, headers=headers, json=vlan_payload, verify=False)
response.raise_for_status()
print(f"VLAN {vlan_name} created successfully.")

# Add the VLAN to the vCMP guest
vcmp_url = f"{f5_host}/mgmt/tm/vcmp/guest/{vcmp_guest_name}"
vcmp_response = requests.get(vcmp_url, headers=headers, verify=False)
vcmp_response.raise_for_status()
vcmp_config = vcmp_response.json()

# Update the VLANs list
if 'vlans' in vcmp_config:
    vcmp_config['vlans'].append(f"/Common/{vlan_name}")
else:
    vcmp_config['vlans'] = [f"/Common/{vlan_name}"]

update_response = requests.put(vcmp_url, headers=headers, json=vcmp_config, verify=False)
update_response.raise_for_status()
print(f"VLAN {vlan_name} added to vCMP guest {vcmp_guest_name} successfully.")
