from ncclient import manager
import xmltodict
import sys

def _get_connection(host_ip):
    
    return manager.connect(
        host=host_ip,
        port=830,
        username="admin",
        password="cisco",
        hostkey_verify=False,
        timeout=10
    )

def _netconf_edit_config(m, netconf_config):
    # Helper function for edit-config
    return m.edit_config(target="running", config=netconf_config, default_operation="merge")

def create(host_ip, student_id, ip_x, ip_y):
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
        with _get_connection(host_ip) as m:
            netconf_reply = _netconf_edit_config(m, netconf_config)
            if '<ok/>' in netconf_reply.xml:
                return "ok"
            else:
                return "Error: Reply did not contain <ok/>"
    except Exception as e:
        print(f"Error in create({host_ip}): {e}") 
        return f"Error: {e}"

def delete(host_ip, student_id):
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
        with _get_connection(host_ip) as m:
            netconf_reply = _netconf_edit_config(m, netconf_config)
            if '<ok/>' in netconf_reply.xml:
                return "ok"
            else:
                return "Error: Reply did not contain <ok/>"
    except Exception as e:
        print(f"Error in delete({host_ip}): {e}")
        return f"Error: {e}"

def enable(host_ip, student_id):
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
        with _get_connection(host_ip) as m:
            netconf_reply = _netconf_edit_config(m, netconf_config)
            if '<ok/>' in netconf_reply.xml:
                return "ok"
            else:
                return "Error: Reply did not contain <ok/>"
    except Exception as e:
        print(f"Error in enable({host_ip}): {e}")
        return f"Error: {e}"

def disable(host_ip, student_id):
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
        with _get_connection(host_ip) as m:
            netconf_reply = _netconf_edit_config(m, netconf_config)
            if '<ok/>' in netconf_reply.xml:
                return "ok"
            else:
                return "Error: Reply did not contain <ok/>"
    except Exception as e:
        print(f"Error in disable({host_ip}): {e}")
        return f"Error: {e}"

def status(host_ip, student_id):
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
        with _get_connection(host_ip) as m:
            netconf_reply = m.get(filter=netconf_filter)
            netconf_reply_dict = xmltodict.parse(netconf_reply.data_xml)

            if (netconf_reply_dict.get('data') and 
                netconf_reply_dict.get('data').get('interfaces-state') and 
                netconf_reply_dict.get('data').get('interfaces-state').get('interface')):
                

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
        print(f"Error in status({host_ip}): {e}")
        return "not_exist"