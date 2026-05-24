#%%
from netmiko import ConnectHandler
#%%
def execute_command(device, command):
    try:
        connection = ConnectHandler(
            device_type=device["device_type"],
            ip=device["ip"],
            username= device["username"],
            password = device["password"],
            secret = device["secret"]
        )
        connection.enable()

        output = connection.send_command(command)
        connection.disconnect()
        return output
    except Exception as e:
        return str(e)

#%%
