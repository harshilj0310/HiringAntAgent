import os

# Construct the correct path to credentials.json
script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of current script
credentials_path = os.path.join(script_dir, "..", "tools", "credentials.json")  # Move up one level to 'tools'

# Debugging: Check if the file exists
if not os.path.exists(credentials_path):
    raise FileNotFoundError(f"Credentials file NOT found at: {credentials_path}")

print("Credentials file found successfully:", credentials_path)
