from pyVim import connect
from pyVmomi import vim
from pyVmomi.vim import CustomizationSpec

# Define vCenter server connection details
vcenter_host = 'vcenter-hostname-or-ip'
vcenter_user = 'your-username'
vcenter_password = 'your-password'

# Define VM details
vm_name = 'NewVM'
vm_template = 'Your-VM-Template-Name'
datastore_name = 'Your-Datastore-Name'
cluster_name = 'Your-Cluster-Name'
resource_pool_name = 'Your-Resource-Pool-Name'
vm_network = 'Your-Network-Name'

# Define cloud-init user data (replace with your cloud-init configuration)
cloud_init_user_data = """\
#cloud-config
users:
  - name: your-username
    ssh-authorized-keys:
      - your-ssh-public-key
    sudo: ALL=(ALL) NOPASSWD:ALL
"""

# Connect to vCenter
try:
    service_instance = connect.SmartConnectNoSSL(
        host=vcenter_host,
        user=vcenter_user,
        pwd=vcenter_password
    )

    # Get the content of the service instance
    content = service_instance.RetrieveContent()

    # Find the VM template
    vm_template_obj = None
    for obj in content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True
    ).view:
        if obj.name == vm_template:
            vm_template_obj = obj
            break

    if vm_template_obj is None:
        raise Exception(f"VM template '{vm_template}' not found")

    # Specify the placement of the new VM
    placement_spec = vim.vm.RelocateSpec(
        pool=content.rootFolder.find_entity([vim.ResourcePool], resource_pool_name),
        datastore=content.rootFolder.find_entity([vim.Datastore], datastore_name)
    )

    # Create VM configuration
    vm_config_spec = vim.vm.ConfigSpec()
    vm_config_spec.name = vm_name
    vm_config_spec.numCPUs = 2
    vm_config_spec.memoryMB = 2048

    # Create the VM clone specification
    clone_spec = vim.vm.CloneSpec(
        location=placement_spec,
        config=vm_config_spec,
        customization=CustomizationSpec(
            cloudConfig=cloud_init_user_data
        ),
        powerOn=False
    )

    # Clone the VM
    task = vm_template_obj.Clone(
        folder=vm_template_obj.parent,
        name=vm_name,
        spec=clone_spec
    )

    # Wait for the clone task to complete
    while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
        pass

    if task.info.state == vim.TaskInfo.State.success:
        print(f"VM '{vm_name}' has been successfully provisioned with cloud-init.")
    else:
        print("Error provisioning the VM:", task.info.error)
except Exception as e:
    print("Error:", str(e))
finally:
    # Disconnect from vCenter
    connect.Disconnect(service_instance)
