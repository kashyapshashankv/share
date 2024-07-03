import requests
import json

# Check Point Gaia API credentials and URL
GAIA_URL = "https://<CHECKPOINT_IP>/web_api"
USERNAME = "<your_username>"
PASSWORD = "<your_password>"

# Function to authenticate and obtain a session ID
def get_session_id():
    url = f"{GAIA_URL}/login"
    payload = {
        "user": USERNAME,
        "password": PASSWORD
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    response.raise_for_status()
    return response.json().get('sid')

# Function to execute a command
def execute_command(session_id, command):
    url = f"{GAIA_URL}/run-script"
    payload = {
        "script-name": "custom_script",
        "script": command
    }
    headers = {
        'Content-Type': 'application/json',
        'X-chkp-sid': session_id
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

# Function to logout and invalidate the session
def logout(session_id):
    url = f"{GAIA_URL}/logout"
    headers = {
        'Content-Type': 'application/json',
        'X-chkp-sid': session_id
    }
    response = requests.post(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

# Main script
if __name__ == "__main__":
    try:
        # Authenticate and get session ID
        session_id = get_session_id()
        print(f"Session ID: {session_id}")

        # Command to be executed
        command = "show version"  # Example command

        # Execute the command
        command_output = execute_command(session_id, command)
        print(f"Command Output: {command_output}")

        # Logout and invalidate the session
        logout_response = logout(session_id)
        print(f"Logout Response: {logout_response}")

    except Exception as e:
        print(f"Error: {e}")
