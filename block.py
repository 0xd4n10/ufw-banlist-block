import subprocess
import os
import ipaddress
import requests
from typing import List

# Path to the saved rules file
saved_rules_file = '/home/user/ufw_rules.txt'  # CHANGEME

def ip_list_to_subnets(ip_list: List[str]) -> List[str]:
    # Convert IP addresses to IPv4Address objects and sort them
    ips = sorted(ipaddress.IPv4Address(ip) for ip in ip_list)

    subnets = []

    # Initialize start and end of range
    start_ip = ips[0]
    end_ip = ips[0]

    # Iterate over sorted IPs to find contiguous ranges
    for ip in ips[1:]:
        if ip == end_ip + 1:  # Check if the IP is contiguous to the previous one
            end_ip = ip
        else:  # If not contiguous, add the range to subnets list and start a new range
            subnets.append(ipaddress.summarize_address_range(start_ip, end_ip))
            start_ip = ip
            end_ip = ip

    # Add the last range to subnets list
    subnets.append(ipaddress.summarize_address_range(start_ip, end_ip))

    # Convert summarized ranges to CIDR notation and flatten the list
    return [str(subnet) for subnet_range in subnets for subnet in subnet_range]


# Function to block IP address for both incoming and outgoing traffic
def block_ip(ip_address):
    # Block incoming traffic from the IP address
    subprocess.run(["sudo", "ufw", "deny", "in", "from", ip_address], check=True)
    # Block outgoing traffic to the IP address
    subprocess.run(["sudo", "ufw", "deny", "out", "to", ip_address], check=True)
    print(f"Blocked IP address: {ip_address}")

def save_ufw():
    with open(saved_rules_file, 'w') as outfile:
        subprocess.run(["sudo", "ufw", "status"], stdout=outfile, stderr=subprocess.PIPE)

def reset_ufw():
    # Reset UFW
    subprocess.run(["sudo", "ufw", "--force", "reset"], check=True)
    subprocess.run(["sudo", "ufw", "enable"], check=True)

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

def block_malcore():
    api_url = "https://api.malcore.io/api/feed"
    api_key = "API-KEY"  # CHANGEME
    headers = {"apiKey": api_key}
    data = {"feed_type": "ip"}

    # Make the POST request to the API
    response = requests.post(api_url, headers=headers, data=data)

    if response.status_code == 200:
        response_data = response.json()['data']['data']
        try:
            if 'list' in response_data:
                ip_list = response_data['list']
                print(f"Blocking {len(ip_list)} IPs")

                # Convert to subnets to cut down on operations
                subnets = ip_list_to_subnets(ip_list)
                print(f"Blocking {len(subnets)} subnets")

                # Iterate over each subnet and block
                for subnet in subnets:
                    block_ip(subnet)
            else:
                print("No IP addresses found in the response.")
        except:
            print("Malcore API request failed. Reached API limit?")
    else:
        print(f"Failed to retrieve data from API. Status code: {response.status_code}. Did you supply API key?")

def block_bindefense():
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

        ip_list = []
        # Iterate over each line, skipping comments and empty lines
        for line in lines:
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith("#"):
                ip_list.append(stripped_line)

        print(f"Blocking {len(ip_list)} IPs")

        # Convert to subnets to cut down on operations
        subnets = ip_list_to_subnets(ip_list)
        print(f"Blocking {len(subnets)} subnets")

        # Iterate over each subnet and block
        for subnet in subnets:
            block_ip(subnet)

    else:
        print(f"Failed to retrieve data from the URL. Status code: {response.status_code}")

def main():
    # check if ufw backup exists
    if not os.path.exists(saved_rules_file):
        print("Creating ufw backup")
        save_ufw()
    else:
        reset_ufw()
        restore_rules()

    print("Blocking IPs supplied by Malcore api")
    block_malcore()
    print("Blocking IPs from BinDefence blocklist")
    block_bindefense()

if __name__ == "__main__":
    main()
