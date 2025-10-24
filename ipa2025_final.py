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
current_method = None  # จะเก็บ 'netconf' หรือ 'restconf'
current_ip = None      # จะเก็บ IP ที่ผู้ใช้เลือก
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
            
            args = message.split()[1:] # แยกอาร์กิวเมนต์
            command = None             # ตัวแปรเก็บคำสั่งที่จะรัน
            responseMessage = ""       # ข้อความที่จะตอบกลับ

            # --- A. PARSE COMMANDS ---
            if len(args) == 0:
                responseMessage = "Error: No command provided."
            
            elif len(args) == 1:
                cmd_arg = args[0]
                if cmd_arg == "netconf":
                    current_method = "netconf"
                    responseMessage = "Ok: Netconf"
                elif cmd_arg == "restconf":
                    current_method = "restconf"
                    responseMessage = "Ok: Restconf"
                elif cmd_arg == "gigabit_status":
                    command = "gigabit_status" # รันคำสั่งนี้
                elif cmd_arg == "showrun":
                    command = "showrun" # รันคำสั่งนี้
                elif cmd_arg in ["create", "delete", "enable", "disable", "status"]:
                    # นี่คือคำสั่งที่ต้องมี IP
                    if current_method is None:
                        responseMessage = "Error: No method specified"
                    else:
                        responseMessage = "Error: No IP specified"
                elif is_ip_address(cmd_arg):
                    # พิมพ์ IP แต่ไม่พิมพ์คำสั่ง
                    responseMessage = "Error: No command found."
                else:
                    responseMessage = "Error: Unknown command."
            
            elif len(args) == 2:
                ip_arg = args[0]
                cmd_arg = args[1]
                
                if not is_ip_address(ip_arg):
                    responseMessage = f"Error: Invalid IP address '{ip_arg}'."
                elif cmd_arg not in ["create", "delete", "enable", "disable", "status"]:
                    responseMessage = f"Error: Command '{cmd_arg}' does not support an IP address."
                else:
                    # OK! เราได้ IP และ Command
                    command = cmd_arg
                    current_ip = ip_arg # บันทึก IP ที่เลือก
            
            else: # len(args) > 2
                responseMessage = "Error: Too many arguments."
                
            # --- B. EXECUTE COMMAND (ถ้ามี) ---
            if command:
                student_id = MY_STUDENT_ID # (student_id ยังคงใช้ MY_STUDENT_ID)

                # -- NETCONF / RESTCONF Commands --
                if command in ["create", "delete", "enable", "disable", "status"]:
                    
                    # Guard 1: เช็คว่าเลือก method หรือยัง
                    if current_method is None:
                        responseMessage = "Error: No method specified"
                    
                    # Guard 2: เช็คว่า IP (current_ip) ถูกตั้งค่าหรือยัง
                    elif current_ip is None:
                         # สภาวะนี้ไม่ควรเกิดถ้า parser ทำงานถูก แต่ดักไว้ก่อน
                        responseMessage = "Error: No IP specified"
                    
                    # ---  NETCONF LOGIC  ---
                    elif current_method == "netconf":
                        print(f"Running '{command}' on {current_ip} using NETCONF...")
                        
                        if command == "create":
                            current_status = netconf_final.status(current_ip, student_id)
                            if current_status == "not_exist":
                                last_three_digits = student_id[-3:] 
                                ip_x = last_three_digits[0]         
                                ip_y = last_three_digits[1:]        
                                create_result = netconf_final.create(current_ip, student_id, ip_x, ip_y)
                                if create_result == "ok":
                                    responseMessage = f"Interface loopback {student_id} is created successfully using Netconf"
                                else:
                                    responseMessage = f"Error: {create_result} (using Netconf)"
                            else:
                                responseMessage = f"Cannot create: Interface loopback {student_id} already created (checked by Netconf)"

                        elif command == "delete":
                            current_status = netconf_final.status(current_ip, student_id)
                            if current_status != "not_exist":
                                delete_result = netconf_final.delete(current_ip, student_id)
                                if delete_result == "ok":
                                    responseMessage = f"Interface loopback {student_id} is deleted successfully using Netconf"
                                else:
                                    responseMessage = f"Error: {delete_result} (using Netconf)"
                            else:
                                responseMessage = f"Cannot delete: Interface loopback {student_id} (checked by Netconf)"
                        
                        elif command == "enable":
                            current_status = netconf_final.status(current_ip, student_id)
                            if current_status != "not_exist":
                                enable_result = netconf_final.enable(current_ip, student_id)
                                if enable_result == "ok":
                                    responseMessage = f"Interface loopback {student_id} is enabled successfully using Netconf"
                                else:
                                    responseMessage = f"Error: {enable_result} (using Netconf)"
                            else:
                                responseMessage = f"Cannot enable: Interface loopback {student_id} (checked by Netconf)"

                        elif command == "disable":
                            current_status = netconf_final.status(current_ip, student_id)
                            if current_status != "not_exist":
                                disable_result = netconf_final.disable(current_ip, student_id)
                                if disable_result == "ok":
                                    responseMessage = f"Interface loopback {student_id} is shutdowned successfully using Netconf"
                                else:
                                    responseMessage = f"Error: {disable_result} (using Netconf)"
                            else:
                                responseMessage = f"Cannot shutdown: Interface loopback {student_id} (checked by Netconf)"
                        
                        elif command == "status":
                            current_status = netconf_final.status(current_ip, student_id)
                            if current_status == "exists_up_up":
                                responseMessage = f"Interface loopback {student_id} is enabled (checked by Netconf)"
                            elif current_status == "exists_down_down":
                                responseMessage = f"Interface loopback {student_id} is disabled (checked by Netconf)"
                            elif current_status == "not_exist":
                                responseMessage = f"No Interface loopback {student_id} (checked by Netconf)"
                            else:
                                responseMessage = f"Interface loopback {student_id} state is: {current_status} (checked by Netconf)"
                    # --- RESTCONF LOGIC ---
                    elif current_method == "restconf":
                        print(f"Running '{command}' on {current_ip} using RESTCONF...")
                        
                        if command == "create":
                            current_status = restconf_final.status(current_ip, student_id)
                            if current_status == "not_exist":
                                last_three_digits = student_id[-3:]
                                ip_x = last_three_digits[0]
                                ip_y = last_three_digits[1:]
                                create_result = restconf_final.create(current_ip, student_id, ip_x, ip_y)
                                if create_result == "ok":
                                    responseMessage = f"Interface loopback {student_id} is created successfully using Restconf"
                                else:
                                    responseMessage = f"Error: {create_result} (using Restconf)"
                            else:
                                responseMessage = f"Cannot create: Interface loopback {student_id} (checked by Restconf)"

                        elif command == "delete":
                            current_status = restconf_final.status(current_ip, student_id)
                            if current_status != "not_exist":
                                delete_result = restconf_final.delete(current_ip, student_id)
                                if delete_result == "ok":
                                    responseMessage = f"Interface loopback {student_id} is deleted successfully using Restconf"
                                else:
                                    responseMessage = f"Error: {delete_result} (using Restconf)"
                            else:
                                responseMessage = f"Cannot delete: Interface loopback {student_id} (checked by Restconf)"

                        elif command == "status":
                            current_status = restconf_final.status(current_ip, student_id)
                            if current_status == "exists_up_up":
                                responseMessage = f"Interface loopback {student_id} is enabled (checked by Restconf)"
                            elif current_status == "exists_down_down":
                                responseMessage = f"Interface loopback {student_id} is disabled (checked by Restconf)"
                            elif current_status == "not_exist":
                                responseMessage = f"No Interface loopback {student_id} (checked by Restconf)"
                            else:
                                responseMessage = f"Interface loopback {student_id} state is: {current_status} (checked by Restconf)"
            if responseMessage:
                HTTPHeaders = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

                postData = json.dumps({"roomId": roomIdToGetMessages, "text": responseMessage})
                HTTPHeaders["Content-Type"] = "application/json"
                
                # Post the call
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