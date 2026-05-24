#%%
import yaml
#%%
def load_inventory():
    with open("inventory.yml", 'r') as inventory_file:
        inventory = yaml.safe_load(inventory_file)
        return inventory
#%%
def get_device_by_name(device_name):
    inventory = load_inventory()
    for device in inventory['devices']:
        if device['name'] == device_name:
            return device
    return None
#%%
def get_devices_by_location(location):
    inventory = load_inventory()
    result = []
    for device in inventory['devices']:
        if device['location'] == location:
            result.append(device)
            break
    return result
#%%
