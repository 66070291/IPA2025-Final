from ncclient import manager
import xmltodict

m = manager.connect(
    host="10.0.15.61",
    port=830,
    username="admin",
    password="cisco",
    hostkey_verify=False
    )

def netconf_edit_config(netconf_config):
    return  m.edit_config(target="running", config=netconf_config, default_operation="merge")

def create(student_id, ip_x, ip_y):
    loopback_name = f"Loopback{student_id}"
    ip_address = f"172.{ip_x}.{ip_y}.1"
    netmask = "255.255.255.0"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{loopback_name}</name>
          <description>Created by NPA2024 Final Bot</description>
          <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
          <enabled>true</enabled>
          <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
            <address>
              <ip>{ip_address}</ip>
              <netmask>{netmask}</netmask>
            </address>
          </ipv4>
        </interface>
      </interfaces>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "ok"
    except:
        print(f"Error in create: {e}")
        print("Error!")


def delete(student_id):
    loopback_name = f"Loopback{student_id}"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface operation="delete">
          <name>{loopback_name}</name>
        </interface>
      </interfaces>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "ok"
    except:
        print(f"Error in delete: {e}")
        print("Error!")


def enable(student_id):
    loopback_name = f"Loopback{student_id}"
    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{loopback_name}</name>
          <enabled>true</enabled>
        </interface>
      </interfaces>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "ok"
    except:
        print(f"Error in enable: {e}")
        print("Error!")


def disable(student_id):
    loopback_name = f"Loopback{student_id}"

    netconf_config = f"""
    <config>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{loopback_name}</name>
          <enabled>false</enabled>
        </interface>
      </interfaces>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "ok"
    except:
        print(f"Error in disable: {e}")
        return "Error!"



def status(student_id):
    loopback_name = f"Loopback{student_id}"
    netconf_filter = f"""
    <filter>
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{loopback_name}</name>
        </interface>
      </interfaces-state>
    </filter>
    """
    try:
        netconf_reply = m.get(filter=netconf_filter)
        print(netconf_reply)
        netconf_reply_dict = xmltodict.parse(netconf_reply.data_xml)

        if netconf_reply_dict.get('data') and netconf_reply_dict.get('data').get('interfaces-state') and netconf_reply_dict.get('data').get('interfaces-state').get('interface'):

            interface_data = netconf_reply_dict['data']['interfaces-state']['interface']

            admin_status = interface_data.get('admin-status', 'unknown')
            oper_status = interface_data.get('oper-status', 'unknown')
            
            if admin_status == 'up' and oper_status == 'up':
                return "exists_up_up"
            elif admin_status == 'down' and oper_status == 'down':
                return "exists_down_down"
            else:
                return "exists_other" 
        else: 
            return "not_exist"
            
    except Exception as e:
        print(f"Error in status check: {e}")
        return "not_exist"
