import requests
import json
import warnings
import logging
import configparser
import os
from datetime import datetime

# Suppress InsecureRequestWarning to avoid warnings related to unverified HTTPS requests
warnings.simplefilter('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Setup logging to display messages with timestamps and severity levels
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load credentials and URL from a configuration file named 'config.ini'
config = configparser.ConfigParser()
config.read('config.ini')
username = config['vCenter']['username']
password = config['vCenter']['password']
vcenter_url = config['vCenter']['url']

# Define headers for API requests
headersAPI1 = {
    'Accept': 'application/json',
    'Connection': 'keep-alive',
    'User-Agent': 'Python',
}


def authenticate():
    """Authenticate with the vCenter server and return the headers with the session token."""
    try:
        response = requests.post(f'{vcenter_url}/rest/com/vmware/cis/session', auth=(username, password), verify=False)
        response.raise_for_status()
        j = response.json()
        cookie = response.cookies
        headersAPI = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + j['value'],
            'Cookie': 'vmware-api-session-id=' + cookie.values()[0]
        }
        return headersAPI
    except requests.RequestException as e:
        logging.error(f"Authentication error: {e}")
        exit(1)


def fetch_esxi_hosts(headersAPI):
    """Fetch the list of ESXi hosts from the vCenter server."""
    try:
        response = requests.get(f'{vcenter_url}/api/vcenter/host', headers=headersAPI, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching ESXi hosts: {e}")
        exit(1)


def main():
    """Main function to authenticate, fetch ESXi hosts, and write the list to a JSON file."""
    headersAPI = authenticate()
    api_response = fetch_esxi_hosts(headersAPI)
    logging.info(json.dumps(api_response, indent=4))

    # Add timestamp and number of ESXi hosts to the beginning of the JSON data
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    number_of_hosts = len(api_response)
    output_data = {
        'timestamp': timestamp,
        'number_of_hosts': number_of_hosts,
        'hosts': api_response
    }

    # Write the modified JSON data to a file
    with open('nfv_esxi_host_list.json', 'w') as file:
        json.dump(output_data, file, indent=4)


if __name__ == '__main__':
    main()
