import requests
import subprocess
import os 

# Path to the saved rules file
saved_rules_file = '/home/user/ufw_rules.txt' # CHANGEME

# Function to block IP address for both incoming and outgoing traffic
def block_ip(ip_address):
    # Block incoming traffic from the IP address
    subprocess.run(["sudo", "ufw", "deny", "in", "from", ip_address], check=True)
    # Block outgoing traffic to the IP address
    subprocess.run(["sudo", "ufw", "deny", "out", "to", ip_address], check=True)
    print(f"Blocked IP address: {ip_address}")


def save_ufw():
    #Make sure its enabled before saving
    subprocess.run(["sudo", "ufw", "--force", "enable"], check=True)
    with open(saved_rules_file, 'w') as outfile:
        subprocess.run(["sudo", "ufw", "status"], stdout=outfile, stderr=subprocess.PIPE)

def reset_ufw():
    subprocess.run(["sudo", "ufw", "--force", "reset"], check=True)
    subprocess.run(["sudo", "ufw", "--force", "enable"], check=True)

def restore_rules():
    with open(saved_rules_file, 'r') as file:
        rules = file.readlines()
        for line in rules:
            line = line.strip()
            if line and not line.startswith('Status:') and not line.startswith('--') and not line.startswith('To'):
                print(line)
                if "v6" in line:
                    continue
                parts = line.split()
                action = parts[1].lower()
                direction = parts[0]
                rule = f"sudo ufw {action} {direction}".strip()
                subprocess.run(rule.split(), check=True)
                print(f"Restored rule: {rule}")
    

def main():
    
    # check if ufw backup exists and restore rules if it does
    if not os.path.exists(saved_rules_file):
        print("Creating ufw backup")
        save_ufw()
    else:
        reset_ufw()
        restore_rules()

    url = "https://www.binarydefense.com/banlist.txt"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Make the GET request to the URL with custom headers
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        response_text = response.text
        
        # Split the response text into lines
        lines = response_text.splitlines()

        # Iterate over each line, skipping comments and empty lines
        for line in lines:
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith("#"):
                block_ip(stripped_line)
    else:
        print(f"Failed to retrieve data from the URL. Status code: {response.status_code}")

if __name__ == "__main__":
    main()
