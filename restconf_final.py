import json
import requests
requests.packages.urllib3.disable_warnings() # ปิดคำเตือน SSL

# --- 1. Headers และ Auth (ใช้ร่วมกัน) ---
# ระบุว่าเราจะส่งและรับข้อมูล JSON ที่เป็นมาตรฐาน YANG
headers_post_put_patch = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
headers_get = {
    "Accept": "application/yang-data+json"
}
basicauth = ("admin", "cisco")


# --- 2. Helper Functions (สร้าง URL แบบไดนามิก) ---
def _get_config_url(host_ip, student_id):
    """
    คืนค่า URL สำหรับ Config (PUT, PATCH, DELETE)
    ชี้ไปที่ interface=Loopback<ID>
    """
    return f"https://{host_ip}/restconf/data/ietf-interfaces:interfaces/interface=Loopback{student_id}"

def _get_operational_url(host_ip, student_id):
    """
    คืนค่า URL สำหรับ Operational Data (GET status)
    ชี้ไปที่ interface=Loopback<ID> ใน operational datastore
    """
    return f"https://{host_ip}/restconf/data/ietf-interfaces:interfaces-state/interface=Loopback{student_id}"

# --- 3. ฟังก์ชันหลัก (Create, Delete, Enable, Disable, Status) ---

def create(host_ip, student_id, ip_x, ip_y):
    """
    สร้าง Interface Loopback (ใช้ HTTP PUT)
    """
    api_url = _get_config_url(host_ip, student_id)
    loopback_name = f"Loopback{student_id}"
    ip_address = f"172.{ip_x}.{ip_y}.1"

    # RESTCONF YANG-JSON Payload
    yangConfig = {
      "ietf-interfaces:interface": {
        "name": loopback_name,
        "description": "Created by NPA2024 Final Bot (RESTCONF)",
        "type": "iana-if-type:softwareLoopback",
        "enabled": True,
        "ietf-ip:ipv4": {
          "address": [
            {
              "ip": ip_address,
              "netmask": "255.255.255.0"
            }
          ]
        }
      }
    }

    resp = requests.put(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers_post_put_patch, 
        verify=False
    )

    if(resp.status_code == 201 or resp.status_code == 204):
        # 201 = Created, 204 = No Content (อัปเดตทับ)
        print("STATUS OK: {}".format(resp.status_code))
        return "ok"
    else:
        print(f"Error in create({host_ip}). Status Code: {resp.status_code}, Text: {resp.text}")
        return f"Error: {resp.status_code}, {resp.text}"


def delete(host_ip, student_id):
    """
    ลบ Interface Loopback (ใช้ HTTP DELETE)
    """
    api_url = _get_config_url(host_ip, student_id)

    resp = requests.delete(
        api_url, 
        auth=basicauth, 
        headers=headers_get, # DELETE ไม่ต้องมี Content-Type
        verify=False
    )

    if(resp.status_code == 204):
        # 204 = No Content (ลบสำเร็จ)
        print("STATUS OK: {}".format(resp.status_code))
        return "ok"
    else:
        print(f"Error in delete({host_ip}). Status Code: {resp.status_code}, Text: {resp.text}")
        return f"Error: {resp.status_code}, {resp.text}"

def enable(host_ip, student_id):
    """
    Enable Interface (ใช้ HTTP PATCH)
    """
    api_url = _get_config_url(host_ip, student_id)
    loopback_name = f"Loopback{student_id}"
    
    # PATCH payload จะส่งแค่ส่วนที่ต้องการเปลี่ยน
    yangConfig = {
      "ietf-interfaces:interface": {
        "name": loopback_name,
        "enabled": True
      }
    }

    resp = requests.patch(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers_post_put_patch, 
        verify=False
    )

    if(resp.status_code == 200 or resp.status_code == 204):
        # 200 = OK, 204 = No Content
        print("STATUS OK: {}".format(resp.status_code))
        return "ok"
    else:
        print(f"Error in enable({host_ip}). Status Code: {resp.status_code}, Text: {resp.text}")
        return f"Error: {resp.status_code}, {resp.text}"


def disable(host_ip, student_id):
    """
    Disable Interface (ใช้ HTTP PATCH)
    """
    api_url = _get_config_url(host_ip, student_id)
    loopback_name = f"Loopback{student_id}"

    yangConfig = {
      "ietf-interfaces:interface": {
        "name": loopback_name,
        "enabled": False
      }
    }

    resp = requests.patch(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers_post_put_patch, 
        verify=False
    )

    if(resp.status_code == 200 or resp.status_code == 204):
        print("STATUS OK: {}".format(resp.status_code))
        return "ok"
    else:
        print(f"Error in disable({host_ip}). Status Code: {resp.status_code}, Text: {resp.text}")
        return f"Error: {resp.status_code}, {resp.text}"

def status(host_ip, student_id):
    """
    ตรวจสอบสถานะ Interface (ใช้ HTTP GET จาก operational datastore)
    """
    api_url_status = _get_operational_url(host_ip, student_id)

    resp = requests.get(
        api_url_status, 
        auth=basicauth, 
        headers=headers_get, # GET ใช้แค่ Accept
        verify=False
    )

    if(resp.status_code == 200):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        
        # ดึงข้อมูล status จาก JSON ที่ตอบกลับมา
        iface_data = response_json.get("ietf-interfaces:interface", {})
        admin_status = iface_data.get("admin-status", "unknown")
        oper_status = iface_data.get("oper-status", "unknown")
        
        if admin_status == 'up' and oper_status == 'up':
            return "exists_up_up"
        elif admin_status == 'down' and oper_status == 'down':
            return "exists_down_down"
        else:
            return "exists_other"
            
    elif(resp.status_code == 404):
        # 404 = Not Found (ไม่เจอ Interface)
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return "not_exist"
    else:
        print(f"Error in status({host_ip}). Status Code: {resp.status_code}, Text: {resp.text}")
        # ถ้า Error อื่นๆ ให้ถือว่าไม่เจอ
        return "not_exist"
