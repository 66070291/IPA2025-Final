#######################################################################################
# Yourname: Prem Lekphon
# Your student ID: 66070291
# Your GitHub Repo: https://github.com/66070291/IPA2025-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
import netconf_final 
import netmiko_final
import ansible_final
import restconf_final
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.
load_dotenv()

ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN")
MY_STUDENT_ID = "66070291"

if not ACCESS_TOKEN:
    raise Exception("WEBEX_ACCESS_TOKEN environment variable not set.")
if MY_STUDENT_ID.startswith("<!!!"):
    raise Exception("Please set MY_STUDENT_ID variable in the script.")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# 3. Helper function to check for valid IP
def is_ip_address(s):
    parts = s.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

# Defines a variable that will hold the roomId
roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYmQwODczMTAtNmMyNi0xMWYwLWE1MWMtNzkzZDM2ZjZjM2Zm"
)

# --- BOT STATE VARIABLES ---
last_processed_message_id = None
current_method = None  
current_ip = None      
# ---------------------------

while True:
    try:
        time.sleep(0.1)
        getParameters = {"roomId": roomIdToGetMessages, "max": 1}
        getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    # 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
        r = requests.get(
            "https://webexapis.com/v1/messages",
            params=getParameters,
            headers=getHTTPHeader,
        )
        
        if not r.status_code == 200:
            print(f"Error getting message from Webex: {r.status_code}")
            continue 

        json_data = r.json()

        if len(json_data["items"]) == 0:
            print("No messages in the room. Waiting...")
            continue 

        messages = json_data["items"]
        
        current_message_id = messages[0]["id"]
        message = messages[0]["text"]
        
        if current_message_id == last_processed_message_id:

            continue
        print("Received message: " + message)
        
        last_processed_message_id = current_message_id


        if message.startswith(f"/{MY_STUDENT_ID} "):
            
            args = message.split()[1:] 
            command = None             
            responseMessage = ""       
            target_ip = current_ip 

            # --- A. PARSE COMMANDS ---
            if len(args) == 0:
                responseMessage = "Error: No command provided."
            
            elif len(args) == 1:
                # Format: /<id> <setting_or_cmd_using_current_ip>
                arg1 = args[0]
                if arg1 == "netconf": current_method = "netconf"; responseMessage = "Ok: Netconf"
                elif arg1 == "restconf": current_method = "restconf"; responseMessage = "Ok: Restconf"
                # --- Commands using remembered IP ---
                elif arg1 == "gigabit_status": command = "gigabit_status"; target_ip = current_ip # ใช้ IP ที่จำไว้
                elif arg1 == "showrun": command = "showrun"; target_ip = current_ip # ใช้ IP ที่จำไว้
                elif arg1 == "motd": command = "motd_get"; target_ip = current_ip # ใช้ IP ที่จำไว้
                # --- Config commands require IP later ---
                elif arg1 in ["create", "delete", "enable", "disable", "status"]:
                    if current_method is None: responseMessage = "Error: No method specified"
                    else: responseMessage = "Error: No IP specified"
                elif is_ip_address(arg1): responseMessage = "Error: No command found."
                else: responseMessage = f"Error: Unknown command or setting '{arg1}'."

            elif len(args) >= 2: 
                # Format: /<id> <ip> <cmd> [motd_msg...]
                arg1 = args[0]
                arg2 = args[1]
                
                if is_ip_address(arg1):
                    potential_ip = arg1
                    potential_cmd = arg2
                    
                    allowed_cmds_with_ip = ["create", "delete", "enable", "disable", "status", 
                                            "gigabit_status", "showrun", "motd"]
                                            
                    if potential_cmd in allowed_cmds_with_ip:
                        target_ip = potential_ip  
                        current_ip = potential_ip 

                        if potential_cmd == "motd":
                            if len(args) > 2: command = "motd_set"; motd_text = " ".join(args[2:])
                            else: command = "motd_get"
                        else: 
                            if len(args) > 2: responseMessage = f"Error: Too many arguments for command '{potential_cmd}'."
                            else: command = potential_cmd 
                    else: 
                        responseMessage = f"Error: Unknown command '{potential_cmd}' or command does not support IP."
                else: 
                    responseMessage = f"Error: Invalid command structure. Expected IP after /{MY_STUDENT_ID}."
            # --- B. EXECUTE COMMAN ---
            if command:
                student_id = MY_STUDENT_ID 

                # -- NETCONF / RESTCONF Commands --
                ip_required_commands = ["create", "delete", "enable", "disable", "status", 
                                       "gigabit_status", "showrun", "motd_get", "motd_set"]
                method_required_commands = ["create", "delete", "enable", "disable", "status"]

                if command in ip_required_commands and target_ip is None:
                    responseMessage = f"Error: No IP specified for command '{command}'."
                    command = None # Prevent execution
                        
                elif command in method_required_commands and current_method is None:
                    responseMessage = "Error: No method specified"
                    command = None 

                # --- Execute Logic ---
                if command == "create":
                    if current_method == "netconf":
                        print(f"Running 'create' on {target_ip} using NETCONF...")
                        current_status = netconf_final.status(target_ip, student_id)
                        if current_status == "not_exist":
                            last_three_digits=student_id[-3:]; ip_x=last_three_digits[0]; ip_y=last_three_digits[1:]
                            create_result = netconf_final.create(target_ip, student_id, ip_x, ip_y)
                            responseMessage = f"Interface loopback {student_id} is created successfully using Netconf" if create_result == "ok" else f"Error: {create_result} (using Netconf)"
                        else: responseMessage = f"Cannot create: Interface loopback {student_id} already exists (checked by Netconf)" 
                    elif current_method == "restconf":
                        print(f"Running 'create' on {target_ip} using RESTCONF...")
                        current_status = restconf_final.status(target_ip, student_id)
                        if current_status == "not_exist":
                            last_three_digits=student_id[-3:]; ip_x=last_three_digits[0]; ip_y=last_three_digits[1:]
                            create_result = restconf_final.create(target_ip, student_id, ip_x, ip_y)
                            responseMessage = f"Interface loopback {student_id} is created successfully using Restconf" if create_result == "ok" else f"Error: {create_result} (using Restconf)"
                        else: responseMessage = f"Cannot create: Interface loopback {student_id} already exists (checked by Restconf)" 

                elif command == "delete":
                    if current_method == "netconf":
                        print(f"Running 'delete' on {target_ip} using NETCONF...")
                        current_status = netconf_final.status(target_ip, student_id)
                        if current_status != "not_exist":
                            delete_result = netconf_final.delete(target_ip, student_id)
                            responseMessage = f"Interface loopback {student_id} is deleted successfully using Netconf" if delete_result == "ok" else f"Error: {delete_result} (using Netconf)"
                        else: responseMessage = f"Cannot delete: Interface loopback {student_id} does not exist (checked by Netconf)" 
                    elif current_method == "restconf":
                        print(f"Running 'delete' on {target_ip} using RESTCONF...")
                        current_status = restconf_final.status(target_ip, student_id)
                        if current_status != "not_exist":
                            delete_result = restconf_final.delete(target_ip, student_id)
                            responseMessage = f"Interface loopback {student_id} is deleted successfully using Restconf" if delete_result == "ok" else f"Error: {delete_result} (using Restconf)"
                        else: responseMessage = f"Cannot delete: Interface loopback {student_id} does not exist (checked by Restconf)" 

                elif command == "enable":
                     if current_method == "netconf":
                        print(f"Running 'enable' on {target_ip} using NETCONF...")
                        current_status = netconf_final.status(target_ip, student_id)
                        if current_status != "not_exist":
                            enable_result = netconf_final.enable(target_ip, student_id)
                            responseMessage = f"Interface loopback {student_id} is enabled successfully using Netconf" if enable_result == "ok" else f"Error: {enable_result} (using Netconf)"
                        else: responseMessage = f"Cannot enable: Interface loopback {student_id} does not exist (checked by Netconf)" 
                     elif current_method == "restconf":
                        print(f"Running 'enable' on {target_ip} using RESTCONF...")
                        current_status = restconf_final.status(target_ip, student_id)
                        if current_status != "not_exist":
                            enable_result = restconf_final.enable(target_ip, student_id)
                            responseMessage = f"Interface loopback {student_id} is enabled successfully using Restconf" if enable_result == "ok" else f"Error: {enable_result} (using Restconf)"
                        else: responseMessage = f"Cannot enable: Interface loopback {student_id} does not exist (checked by Restconf)" 

                elif command == "disable":
                    if current_method == "netconf":
                        print(f"Running 'disable' on {target_ip} using NETCONF...")
                        current_status = netconf_final.status(target_ip, student_id)
                        if current_status != "not_exist":
                            disable_result = netconf_final.disable(target_ip, student_id)
                            responseMessage = f"Interface loopback {student_id} is shutdowned successfully using Netconf" if disable_result == "ok" else f"Error: {disable_result} (using Netconf)"
                        else: responseMessage = f"Cannot shutdown: Interface loopback {student_id} does not exist (checked by Netconf)" 
                    elif current_method == "restconf":
                        print(f"Running 'disable' on {target_ip} using RESTCONF...")
                        current_status = restconf_final.status(target_ip, student_id)
                        if current_status != "not_exist":
                            disable_result = restconf_final.disable(target_ip, student_id)
                            responseMessage = f"Interface loopback {student_id} is shutdowned successfully using Restconf" if disable_result == "ok" else f"Error: {disable_result} (using Restconf)"
                        else: responseMessage = f"Cannot shutdown: Interface loopback {student_id} does not exist (checked by Restconf)" 

                elif command == "status":
                    if current_method == "netconf":
                        print(f"Running 'status' on {target_ip} using NETCONF...")
                        current_status = netconf_final.status(target_ip, student_id)
                        if current_status == "exists_up_up": responseMessage = f"Interface loopback {student_id} is enabled (checked by Netconf)"
                        elif current_status == "exists_down_down": responseMessage = f"Interface loopback {student_id} is disabled (checked by Netconf)"
                        elif current_status == "not_exist": responseMessage = f"No Interface loopback {student_id} (checked by Netconf)"
                        else: responseMessage = f"Interface loopback {student_id} state is: {current_status} (checked by Netconf)"
                    elif current_method == "restconf":
                        print(f"Running 'status' on {target_ip} using RESTCONF...")
                        current_status = restconf_final.status(target_ip, student_id)
                        if current_status == "exists_up_up": responseMessage = f"Interface loopback {student_id} is enabled (checked by Restconf)"
                        elif current_status == "exists_down_down": responseMessage = f"Interface loopback {student_id} is disabled (checked by Restconf)"
                        elif current_status == "not_exist": responseMessage = f"No Interface loopback {student_id} (checked by Restconf)"
                        else: responseMessage = f"Interface loopback {student_id} state is: {current_status} (checked by Restconf)"
                
                # --- MOTD Commands ---
                elif command == "motd_set":
                    print(f"Running 'motd_set' on {target_ip} using Ansible...")
                    set_result = ansible_final.set_motd(target_ip, motd_text)
                    if set_result.startswith("ok"): responseMessage = "Ok: success"
                    else: responseMessage = set_result # Return the error message from Ansible
                
                elif command == "motd_get":
                     print(f"Running 'motd_get' on {target_ip} using Netmiko...")
                     responseMessage = netmiko_final.get_motd(target_ip)

                # --- gigabit status Commands ---
                elif command == "gigabit_status":
                    print(f"Running 'gigabit_status' on {target_ip} using Netmiko...")
                    responseMessage = netmiko_final.gigabit_status(target_ip)

                # --- showrun ansible ---
                elif command == "showrun":
                    print(f"Running 'showrun' on {target_ip} using Ansible...")
                    ansible_result = ansible_final.showrun(target_ip) 
                    responseMessage = ansible_result # Store result ("ok" or "Error...")

            if responseMessage:
                HTTPHeaders = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

                if command == "showrun" and responseMessage == 'ok':

                    inventory_hostname = "CSR1KV" if target_ip == "192.168.1.101" else target_ip 
                    
                    filename = f"show_run_{MY_STUDENT_ID}_{inventory_hostname}.txt"
                    
                    try:
                        fileobject = open(filename, 'rb')
                        filetype = "text/plain"
                        postData_multipart = MultipartEncoder(fields={"roomId": roomIdToGetMessages, "text": "show running config", "files": (filename, fileobject, filetype)})
                        postData = postData_multipart
                        HTTPHeaders["Content-Type"] = postData_multipart.content_type
                        
                        actual_response_text = f"showrun file {filename} attached" 
                        
                    except Exception as e:
                        print(f"Error preparing file {filename} for upload: {e}")
                        responseMessage = f"Error: Ansible OK, but failed to read file {filename}."
                        postData = json.dumps({"roomId": roomIdToGetMessages, "text": responseMessage})
                        HTTPHeaders["Content-Type"] = "application/json"
                        actual_response_text = responseMessage 
                else:
                    postData = json.dumps({"roomId": roomIdToGetMessages, "text": responseMessage})
                    HTTPHeaders["Content-Type"] = "application/json"
                    actual_response_text = responseMessage 

                # --- Post the message ---
                r = requests.post("https://webexapis.com/v1/messages", data=postData, headers=HTTPHeaders)
                
                if not r.status_code == 200:
                    print(f"Error posting reply to Webex: {r.status_code}, {r.text}")
                else:
                    print(f"Successfully posted response: {actual_response_text}") 
                    response_json = r.json()
                    last_processed_message_id = response_json["id"]

    except Exception as e:
        print(f"An unexpected error occurred in the main loop: {e}")
        pass