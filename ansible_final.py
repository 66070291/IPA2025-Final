import subprocess
import shlex 

def set_motd(host_ip, message):
    """
    Sets the MOTD banner on the specified host using Ansible.
    """
    playbook = 'motd_playbook.yml'
    extra_vars = f"motd_message={shlex.quote(message)}"
    
    command = ['ansible-playbook', '-l', host_ip, playbook, '-e', extra_vars]
    
    print(f"Running Ansible command: {' '.join(command)}") 
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    print("--- Ansible STDOUT (set_motd) ---")
    print(result.stdout)
    print("--- Ansible STDERR (set_motd) ---")
    print(result.stderr)
    print("---------------------------------")
    
    result_text = result.stdout
    
    if 'ok=1' in result_text and 'changed=1' in result_text and 'failed=0' in result_text:
        return "ok" 
    elif 'ok=1' in result_text and 'changed=0' in result_text and 'failed=0' in result_text:
         return "ok (no change)" 
    else:
        error_msg = result.stderr or result.stdout.splitlines()[-1] 
        return f'Error: Ansible failed - {error_msg}'

def showrun(host_ip):
    """
    Runs the showrun playbook, limited to the specified host_ip.
    NOTE: Filename saving logic currently relies on inventory_hostname matching.
    """
    playbook = 'showrun_playbook.yml'
    command = ['ansible-playbook', '-l', host_ip, playbook] 
    
    print(f"Running Ansible command: {' '.join(command)}") 

    result = subprocess.run(command, capture_output=True, text=True)
    
    print("--- Ansible STDOUT (showrun) ---")
    print(result.stdout)
    print("--- Ansible STDERR (showrun) ---")
    print(result.stderr)
    print("----------------------------------")
    
    result_text = result.stdout
    
    if 'ok=2' in result_text and 'failed=0' in result_text:
        return "ok" 
    else:
        error_msg = result.stderr or result.stdout.splitlines()[-1]
        return f'Error: Ansible failed - {error_msg}'

