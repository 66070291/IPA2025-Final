import subprocess
import shlex # Import shlex for safe command argument quoting

# --- แก้ไข showrun ให้รับ host_ip ---
def showrun(host_ip):
    """
    Runs the showrun playbook, limited to the specified host_ip.
    NOTE: Filename saving logic currently relies on inventory_hostname matching.
    """
    playbook = 'showrun_playbook.yml'
    # Limit the playbook run to the specified host_ip
    command = ['ansible-playbook', '-l', host_ip, playbook] 
    
    print(f"Running Ansible command: {' '.join(command)}") # For debugging

    result = subprocess.run(command, capture_output=True, text=True)
    
    print("--- Ansible STDOUT (showrun) ---")
    print(result.stdout)
    print("--- Ansible STDERR (showrun) ---")
    print(result.stderr)
    print("----------------------------------")
    
    result_text = result.stdout
    
    # Check for success (2 tasks: ok=2)
    if 'ok=2' in result_text and 'failed=0' in result_text:
        return "ok" 
    else:
        error_msg = result.stderr or result.stdout.splitlines()[-1]
        return f'Error: Ansible failed - {error_msg}'

