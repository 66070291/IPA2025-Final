import subprocess

def showrun():

    command = ['ansible-playbook', 'showrun_playbook.yml'] 

    result = subprocess.run(command, capture_output=True, text=True)
    
    # (Optional) พิมพ์ผลลัพธ์เพื่อการดีบัก
    print("--- Ansible STDOUT ---")
    print(result.stdout)
    print("--- Ansible STDERR ---")
    print(result.stderr)
    print("----------------------")
    
    result_text = result.stdout

    if 'ok=2' in result_text and 'failed=0' in result_text:
        return "ok" 
    else:
        return 'Error' 

