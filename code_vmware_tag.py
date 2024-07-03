from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import requests
import atexit
import ssl

# Disable warnings for self-signed certificates
requests.packages.urllib3.disable_warnings()

# Replace with your vCenter details
vcenter_server = 'vcenter_server_ip_or_hostname'
vcenter_username = 'your_username'
vcenter_password = 'your_password'
vm_name = 'your_vm_name'
tag_name = 'MyTag'
category_name = 'MyCategory'

# Connect to vCenter
context = ssl._create_unverified_context()
si = SmartConnect(host=vcenter_server, user=vcenter_username, pwd=vcenter_password, sslContext=context)
atexit.register(Disconnect, si)

# Get the VM object
content = si.RetrieveContent()
vm = None
for datacenter in content.rootFolder.childEntity:
    if hasattr(datacenter.vmFolder, 'childEntity'):
        vmFolder = datacenter.vmFolder
        vmList = vmFolder.childEntity
        for v in vmList:
            if v.name == vm_name:
                vm = v
                break
    if vm:
        break

if not vm:
    print(f"VM {vm_name} not found")
    exit(1)

# REST API details
session = requests.session()
session.verify = False
rest_url = f"https://{vcenter_server}/rest"
auth = (vcenter_username, vcenter_password)

# Authenticate and create a session
resp = session.post(f"{rest_url}/com/vmware/cis/session", auth=auth)
session_id = resp.json()['value']
headers = {'vmware-api-session-id': session_id}

# Get or create the category
category_id = None
resp = session.get(f"{rest_url}/com/vmware/cis/tagging/category", headers=headers)
categories = resp.json()['value']
for cat in categories:
    resp = session.get(f"{rest_url}/com/vmware/cis/tagging/category/id:{cat}", headers=headers)
    category = resp.json()['value']
    if category['name'] == category_name:
        category_id = cat
        break

if not category_id:
    category_spec = {
        "create_spec": {
            "name": category_name,
            "description": "Category for my tags",
            "cardinality": "MULTIPLE",
            "associable_types": ["VirtualMachine"]
        }
    }
    resp = session.post(f"{rest_url}/com/vmware/cis/tagging/category", json=category_spec, headers=headers)
    category_id = resp.json()['value']

# Get or create the tag
tag_id = None
resp = session.get(f"{rest_url}/com/vmware/cis/tagging/tag", headers=headers)
tags = resp.json()['value']
for t in tags:
    resp = session.get(f"{rest_url}/com/vmware/cis/tagging/tag/id:{t}", headers=headers)
    tag = resp.json()['value']
    if tag['name'] == tag_name:
        tag_id = t
        break

if not tag_id:
    tag_spec = {
        "create_spec": {
            "name": tag_name,
            "description": "My tag description",
            "category_id": category_id
        }
    }
    resp = session.post(f"{rest_url}/com/vmware/cis/tagging/tag", json=tag_spec, headers=headers)
    tag_id = resp.json()['value']

# Attach the tag to the VM
tag_association_spec = {
    "object_id": {
        "id": vm._moId,
        "type": "VirtualMachine"
    },
    "tag_id": tag_id
}
resp = session.post(f"{rest_url}/com/vmware/cis/tagging/tag-association", json=tag_association_spec, headers=headers)

if resp.status_code == 204:
    print(f'Tag "{tag_name}" assigned to VM "{vm_name}".')
else:
    print(f'Failed to assign tag: {resp.content}')
