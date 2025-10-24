from netmiko import ConnectHandler
from pprint import pprint

# --- 1. กรอก IP และ Device Type ---
device_ip = "10.0.15.61" 
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_xe", 
    "ip": device_ip,
    "username": username,
    "password": password,
    "ssh_config_file": "~/.ssh/config" 
}


def gigabit_status():
    # เราจะเก็บรายละเอียด list 
    detail_list = [] 
    
    try:
        with ConnectHandler(**device_params) as ssh:
            up = 0
            down = 0
            admin_down = 0
            
            # --- ใช้คำสั่ง 'show ip interface brief' ---
            result = ssh.send_command("show ip interface brief", use_textfsm=True)
            
            
            for iface_dict in result: # เปลี่ยนชื่อตัวแปร status เป็น iface_dict
                
                # --- ตรวจสอบเฉพาะ Interface 'GigabitEthernet' ---
                if iface_dict['interface'].startswith("GigabitEthernet"):
                    
                    # เพิ่ม "GigabitEthernetX [status]" เข้าไปใน list
                    detail_list.append(f"{iface_dict['interface']} {iface_dict['status']}")
                    
                    # --- ตรวจสอบสถานะและนับ ---
                    if iface_dict['status'] == "up": 
                        up += 1
                    elif iface_dict['status'] == "down": 
                        down += 1
                    elif iface_dict['status'] == "administratively down": 
                        admin_down += 1
            
            detail_string = ", ".join(detail_list)
            ans = f"{detail_string} -> {up} up, {down} down, {admin_down} administratively down"
            
            pprint(ans)
            return ans
            
    except Exception as e:
        print(f"Error connecting or running command with Netmiko: {e}")
        return f"Error connecting to router: {e}"

# --- (Optional) ส่วนสำหรับทดสอบ ---
# ถ้าคุณอยากทดสอบไฟล์นี้เดี่ยวๆ ให้ uncomment 2 บรรทัดล่าง
# if __name__ == "__main__":
#     gigabit_status()