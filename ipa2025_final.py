#######################################################################################
# Yourname: Prem Lekphon
# Your student ID: 66070291
# Your GitHub Repo: https://github.com/66070291/IPA2024-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
import netconf_final 
import netmiko_final
import ansible_final
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

# Defines a variable that will hold the roomId
roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYmQwODczMTAtNmMyNi0xMWYwLWE1MWMtNzkzZDM2ZjZjM2Zm"
)

last_processed_message_id = None

while True:
    try:
        time.sleep(0.5)
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

            try:
                command = message.split()[1]
                student_id = MY_STUDENT_ID
                print(f"Processing command: {command} for {student_id}")
            except IndexError:
                print("Message format error. Skipping.")
                continue

            
            # 5. Complete the logic for each command
            if command == "create":
                print(f"Checking status for Loopback{student_id}...")
                current_status = netconf_final.status(student_id)
                
                if current_status == "not_exist":
                    print(f"Interface does not exist. Attempting to create...")
                    
                    last_three_digits = student_id[-3:] 
                    ip_x = last_three_digits[0]         
                    ip_y = last_three_digits[1:]        
                    
                    create_result = netconf_final.create(student_id, ip_x, ip_y)
                    
                    if create_result == "ok":
                        responseMessage = f"Interface loopback {student_id} is created successfully"
                    else:
                        responseMessage = f"Error: Failed to create interface loopback {student_id}. Result: {create_result}"
                else:
                    print(f"Interface already exists (Status: {current_status}).")
                    responseMessage = f"Cannot create: Interface loopback {student_id}"    
            
            elif command == "delete":
                print(f"Checking status for Loopback{student_id}...")
                current_status = netconf_final.status(student_id)
                
                if current_status != "not_exist":
                    print(f"Interface exists (Status: {current_status}). Attempting to delete...")
                    
                    delete_result = netconf_final.delete(student_id)
                    
                    if delete_result == "ok":
                        responseMessage = f"Interface loopback {student_id} is deleted successfully"
                    else:
                        responseMessage = f"Error: Failed to delete interface loopback {student_id}. Result: {delete_result}"
                else:
                    print(f"Interface Loopback{student_id} does not exist.")
                    responseMessage = f"Cannot delete: Interface loopback {student_id}"
            
            elif command == "enable":
                print(f"Checking status for Loopback{student_id}...")
                current_status = netconf_final.status(student_id)
                
                if current_status != "not_exist":
                    print(f"Interface exists (Status: {current_status}). Attempting to enable...")
                    
                    enable_result = netconf_final.enable(student_id)
                    
                    if enable_result == "ok":
                        responseMessage = f"Interface loopback {student_id} is enabled successfully"
                    else:
                        responseMessage = f"Error: Failed to enable interface loopback {student_id}. Result: {enable_result}"
                else:
                    print(f"Interface Loopback{student_id} does not exist.")
                    responseMessage = f"Cannot enable: Interface loopback {student_id}"
            
            elif command == "disable":
                print(f"Checking status for Loopback{student_id}...")
                current_status = netconf_final.status(student_id)
                
                if current_status != "not_exist":
                    print(f"Interface exists (Status: {current_status}). Attempting to disable...")
                    
                    disable_result = netconf_final.disable(student_id)
                    
                    if disable_result == "ok":
                        responseMessage = f"Interface loopback {student_id} is shutdowned successfully"
                    else:
                        responseMessage = f"Error: Failed to shutdown interface loopback {student_id}. Result: {disable_result}"
                else:
                    # 3. Interface does not exist
                    print(f"Interface Loopback{student_id} does not exist.")
                    responseMessage = f"Cannot shutdown: Interface loopback {student_id}"
            
            elif command == "status":
                print(f"Checking status for Loopback{student_id}...")
                current_status = netconf_final.status(student_id)
                
                if current_status == "exists_up_up":
                    responseMessage = f"Interface loopback {student_id} is enabled"
                
                elif current_status == "exists_down_down":
                    responseMessage = f"Interface loopback {student_id} is disabled"
                
                elif current_status == "not_exist":
                    responseMessage = f"No Interface loopback {student_id}"
                
                else:
                    responseMessage = f"Interface loopback {student_id} state is: {current_status}"
            
            elif command == "gigabit_status":
                print("Processing gigabit_status command...")
                responseMessage = netmiko_final.gigabit_status()
            elif command == "showrun":
                print("Processing showrun command...")
                responseMessage = ansible_final.showrun()
            else:
                responseMessage = "Error: No command or unknown command"
            
            HTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}"
            }
            
            # --- แก้ไขตรรกะตรงนี้ ---
            if command == "showrun" and responseMessage == 'ok':

                filename = f"show_run_{MY_STUDENT_ID}_CSR1kv.txt"
                
                try:
                    fileobject = open(filename, 'rb') 
                    filetype = "text/plain" 
                    
                    postData_multipart = MultipartEncoder(
                        fields={
                            "roomId": roomIdToGetMessages,
                            "text": "show running config", 
                            "files": (filename, fileobject, filetype)
                        }
                    )
                    
                    postData = postData_multipart
                    HTTPHeaders["Content-Type"] = postData_multipart.content_type

                except Exception as e:
                    print(f"Error preparing file {filename} for upload: {e}")

                    responseMessage = f"Error: Ansible OK, but failed to read file {filename}."

                    postData = json.dumps({
                        "roomId": roomIdToGetMessages,
                        "text": responseMessage
                    })
                    HTTPHeaders["Content-Type"] = "application/json"

            else:
                postData = json.dumps({
                    "roomId": roomIdToGetMessages,
                    "text": responseMessage
                })
                HTTPHeaders["Content-Type"] = "application/json"

            # Post the call to the Webex Teams message API.
            r = requests.post(
                "https://webexapis.com/v1/messages",
                data=postData,
                headers=HTTPHeaders,
            )
            
            if not r.status_code == 200:
                print(f"Error posting reply to Webex: {r.status_code}, {r.text}")
                continue
            
            print(f"Successfully posted response: {responseMessage}")
            
            response_json = r.json()
            last_processed_message_id = response_json["id"]

    except Exception as e:
        print(f"An unexpected error occurred in the main loop: {e}")
        pass