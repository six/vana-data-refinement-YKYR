import json
import logging
import os
import requests
from refiner.config import settings

def upload_json_to_ipfs(data):
    """
    Uploads JSON data to the private IPFS server.
    :param data: JSON data to upload (dictionary or list)
    :return: IPFS hash
    """
    try:
        # Prepare the API endpoint for file adding
        add_endpoint = f"{settings.IPFS_API_URL}/add"
        
        # Convert data to JSON string
        json_str = json.dumps(data)
        
        # Use requests to upload directly
        files = {
            'file': ('file.json', json_str, 'application/json')
        }
        
        response = requests.post(add_endpoint, files=files)
        response.raise_for_status()
        
        result = response.json()
        hash_value = result['Hash']
        logging.info(f"Successfully uploaded JSON to IPFS with hash: {hash_value}")
        return hash_value

    except Exception as e:
        logging.error(f"An error occurred while uploading JSON to IPFS: {e}")
        raise e

def upload_file_to_ipfs(file_path=None):
    """
    Uploads a file to the private IPFS server.
    :param file_path: Path to the file to upload (defaults to encrypted database)
    :return: IPFS hash
    """
    if file_path is None:
        # Default to the encrypted database file
        file_path = os.path.join(settings.OUTPUT_DIR, "db.libsql.pgp")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        # Prepare the API endpoint for file adding
        add_endpoint = f"{settings.IPFS_API_URL}/add"
        
        with open(file_path, 'rb') as file:
            files = {
                'file': file
            }
            response = requests.post(add_endpoint, files=files)
        
        response.raise_for_status()
        result = response.json()
        hash_value = result['Hash']
        logging.info(f"Successfully uploaded file to IPFS with hash: {hash_value}")
        return hash_value

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while uploading file to IPFS: {e}")
        raise e

# Test with: python -m refiner.utils.ipfs
if __name__ == "__main__":
    ipfs_hash = upload_file_to_ipfs()
    print(f"File uploaded to IPFS with hash: {ipfs_hash}")
    print(f"Access at: https://ipfs.vana.org/ipfs/{ipfs_hash}")
    
    ipfs_hash = upload_json_to_ipfs()
    print(f"JSON uploaded to IPFS with hash: {ipfs_hash}")
    print(f"Access at: https://ipfs.vana.org/ipfs/{ipfs_hash}")
