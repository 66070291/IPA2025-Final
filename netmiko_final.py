from netmiko import ConnectHandler
from pprint import pprint

device_params_base = {
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "cisco",
    "ssh_config_file": "~/.ssh/config" 
}

def get_motd(host_ip):
    """
    Gets the MOTD banner from the specified host using Netmiko and a custom TextFSM template.
    Correctly handles the parsed output structure.
    """
    device_params = device_params_base.copy()
    device_params["host"] = host_ip

    motd_response = "Error: No MOTD Configured" 

    try:
        with ConnectHandler(**device_params) as ssh:
            command = "show banner motd"
            template_path = "show_banner_motd.textfsm"

            result = ssh.send_command(
                command,
                use_textfsm=True,
                textfsm_template=template_path,
                strip_command=False, 
                strip_prompt=False  
            )

            print(f"--- Netmiko Parsed Data (get_motd for {host_ip}) ---")
            pprint(result)
            print("--------------------------------------------------")

            if isinstance(result, list) and len(result) > 1: 

                banner_text = result[1].get('bannertext', '').strip() 

                if banner_text and "Error: No banner configured" not in banner_text:
                    motd_response = banner_text

    except Exception as e:
        print(f"Error connecting or running command with Netmiko (get_motd for {host_ip}): {e}")
        motd_response = f"Error connecting to router or getting MOTD: {e}"

    pprint(motd_response)
    return motd_response

def gigabit_status(host_ip):
    """
    Gets the status of GigabitEthernet interfaces on the specified host.
    """
    device_params = device_params_base.copy()
    device_params["host"] = host_ip 

    detail_list = [] 
    ans = f"Error: Could not retrieve status for {host_ip}" # Default error
    
    try:
        with ConnectHandler(**device_params) as ssh:
            up = 0
            down = 0
            admin_down = 0
            
            command = "show ip interface brief"
            result = ssh.send_command(command, use_textfsm=True)
            
            print(f"--- Netmiko Parsed Data (gigabit_status for {host_ip}) ---")
            pprint(result)
            print("---------------------------------------------------------")

            if not isinstance(result, list):
                 raise ValueError(f"TextFSM did not return a list for '{command}'")

            for iface_dict in result: 
                if iface_dict.get('interface','').startswith("GigabitEthernet"): # Use .get for safety
                    status = iface_dict.get('status', 'unknown') # Use .get for safety
                    
                    detail_list.append(f"{iface_dict['interface']} {status}")
                    
                    if status == "up": 
                        up += 1
                    elif status == "down": 
                        down += 1
                    elif status == "administratively down": 
                        admin_down += 1
            
            detail_string = ", ".join(detail_list)
            ans = f"{detail_string} -> {up} up, {down} down, {admin_down} administratively down"
            
    except Exception as e:
        print(f"Error connecting or running command with Netmiko (gigabit_status for {host_ip}): {e}")
        ans = f"Error retrieving status from {host_ip}: {e}" # Return specific error

    pprint(ans)
    return ans