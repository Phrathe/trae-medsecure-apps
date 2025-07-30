import os
import json
import hashlib
import base64
import requests
from typing import Dict, List, Any, Optional, Union, BinaryIO
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPFSManager:
    """
    Manages interactions with IPFS/Filecoin for secure file storage.
    Handles encryption, decryption, and IPFS operations.
    """
    
    def __init__(self, ipfs_api_url: str = "http://localhost:5001/api/v0", 
                 web3_storage_token: Optional[str] = None,
                 infura_ipfs_project_id: Optional[str] = None,
                 infura_ipfs_project_secret: Optional[str] = None):
        """
        Initialize the IPFS manager with API configuration.
        
        Args:
            ipfs_api_url (str): URL for local IPFS API
            web3_storage_token (str, optional): API token for Web3.Storage
            infura_ipfs_project_id (str, optional): Infura IPFS project ID
            infura_ipfs_project_secret (str, optional): Infura IPFS project secret
        """
        self.ipfs_api_url = ipfs_api_url
        self.web3_storage_token = web3_storage_token or os.environ.get("WEB3_STORAGE_TOKEN")
        self.infura_ipfs_project_id = infura_ipfs_project_id or os.environ.get("INFURA_IPFS_PROJECT_ID")
        self.infura_ipfs_project_secret = infura_ipfs_project_secret or os.environ.get("INFURA_IPFS_PROJECT_SECRET")
        
        # Determine which IPFS service to use
        if self.web3_storage_token:
            self.ipfs_service = "web3.storage"
            logger.info("Using Web3.Storage for IPFS")
        elif self.infura_ipfs_project_id and self.infura_ipfs_project_secret:
            self.ipfs_service = "infura"
            logger.info("Using Infura for IPFS")
        else:
            self.ipfs_service = "local"
            logger.info("Using local IPFS node")
    
    def _generate_key(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Generate a Fernet encryption key from a password.
        
        Args:
            password (str): Password to derive key from
            salt (bytes, optional): Salt for key derivation
            
        Returns:
            tuple: (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt_file(self, file_data: bytes, password: str) -> Dict[str, Any]:
        """
        Encrypt file data with AES-256 using a password-derived key.
        
        Args:
            file_data (bytes): Raw file data to encrypt
            password (str): Password for encryption
            
        Returns:
            dict: Encrypted data and metadata
        """
        try:
            # Generate key and salt
            key, salt = self._generate_key(password)
            
            # Create Fernet cipher
            cipher = Fernet(key)
            
            # Encrypt data
            encrypted_data = cipher.encrypt(file_data)
            
            # Calculate hash of original data for integrity verification
            original_hash = hashlib.sha256(file_data).hexdigest()
            
            return {
                "encrypted_data": encrypted_data,
                "salt": base64.b64encode(salt).decode(),
                "original_hash": original_hash,
                "encryption_method": "AES-256-Fernet"
            }
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_file(self, encrypted_data: bytes, password: str, salt: str) -> bytes:
        """
        Decrypt file data using the provided password and salt.
        
        Args:
            encrypted_data (bytes): Encrypted file data
            password (str): Password for decryption
            salt (str): Base64-encoded salt used for encryption
            
        Returns:
            bytes: Decrypted file data
        """
        try:
            # Decode salt
            salt_bytes = base64.b64decode(salt)
            
            # Regenerate key using password and salt
            key, _ = self._generate_key(password, salt_bytes)
            
            # Create Fernet cipher
            cipher = Fernet(key)
            
            # Decrypt data
            decrypted_data = cipher.decrypt(encrypted_data)
            
            return decrypted_data
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def _upload_to_local_ipfs(self, data: bytes) -> str:
        """
        Upload data to a local IPFS node.
        
        Args:
            data (bytes): Data to upload
            
        Returns:
            str: IPFS CID (Content Identifier)
        """
        try:
            # Add data to IPFS
            files = {'file': data}
            response = requests.post(f"{self.ipfs_api_url}/add", files=files)
            
            if response.status_code != 200:
                raise Exception(f"IPFS upload failed with status code {response.status_code}: {response.text}")
            
            # Parse response to get CID
            result = response.json()
            return result['Hash']
        except Exception as e:
            logger.error(f"Local IPFS upload failed: {str(e)}")
            raise
    
    def _upload_to_web3_storage(self, data: bytes, filename: str = "encrypted_file") -> str:
        """
        Upload data to Web3.Storage.
        
        Args:
            data (bytes): Data to upload
            filename (str): Name for the file
            
        Returns:
            str: IPFS CID (Content Identifier)
        """
        try:
            if not self.web3_storage_token:
                raise ValueError("Web3.Storage token not provided")
            
            # Prepare headers with authorization
            headers = {
                "Authorization": f"Bearer {self.web3_storage_token}"
            }
            
            # Prepare files
            files = {
                'file': (filename, data)
            }
            
            # Upload to Web3.Storage
            response = requests.post(
                "https://api.web3.storage/upload",
                headers=headers,
                files=files
            )
            
            if response.status_code != 200:
                raise Exception(f"Web3.Storage upload failed with status code {response.status_code}: {response.text}")
            
            # Parse response to get CID
            result = response.json()
            return result['cid']
        except Exception as e:
            logger.error(f"Web3.Storage upload failed: {str(e)}")
            raise
    
    def _upload_to_infura_ipfs(self, data: bytes) -> str:
        """
        Upload data to Infura IPFS.
        
        Args:
            data (bytes): Data to upload
            
        Returns:
            str: IPFS CID (Content Identifier)
        """
        try:
            if not self.infura_ipfs_project_id or not self.infura_ipfs_project_secret:
                raise ValueError("Infura IPFS credentials not provided")
            
            # Prepare auth
            auth = (self.infura_ipfs_project_id, self.infura_ipfs_project_secret)
            
            # Prepare files
            files = {
                'file': data
            }
            
            # Upload to Infura IPFS
            response = requests.post(
                "https://ipfs.infura.io:5001/api/v0/add",
                auth=auth,
                files=files
            )
            
            if response.status_code != 200:
                raise Exception(f"Infura IPFS upload failed with status code {response.status_code}: {response.text}")
            
            # Parse response to get CID
            result = response.json()
            return result['Hash']
        except Exception as e:
            logger.error(f"Infura IPFS upload failed: {str(e)}")
            raise
    
    def upload_encrypted_file(self, file_data: bytes, password: str, filename: str = "encrypted_file") -> Dict[str, Any]:
        """
        Encrypt and upload a file to IPFS.
        
        Args:
            file_data (bytes): Raw file data to encrypt and upload
            password (str): Password for encryption
            filename (str): Name for the file
            
        Returns:
            dict: Upload result with CID and metadata
        """
        try:
            # Encrypt file
            encryption_result = self.encrypt_file(file_data, password)
            encrypted_data = encryption_result["encrypted_data"]
            
            # Upload to IPFS based on configured service
            if self.ipfs_service == "web3.storage":
                cid = self._upload_to_web3_storage(encrypted_data, filename)
            elif self.ipfs_service == "infura":
                cid = self._upload_to_infura_ipfs(encrypted_data)
            else:  # local
                cid = self._upload_to_local_ipfs(encrypted_data)
            
            # Return result
            return {
                "cid": cid,
                "filename": filename,
                "size": len(file_data),
                "encrypted_size": len(encrypted_data),
                "salt": encryption_result["salt"],
                "original_hash": encryption_result["original_hash"],
                "encryption_method": encryption_result["encryption_method"]
            }
        except Exception as e:
            logger.error(f"Upload encrypted file failed: {str(e)}")
            raise
    
    def _download_from_local_ipfs(self, cid: str) -> bytes:
        """
        Download data from a local IPFS node.
        
        Args:
            cid (str): IPFS CID (Content Identifier)
            
        Returns:
            bytes: Downloaded data
        """
        try:
            # Get data from IPFS
            response = requests.post(f"{self.ipfs_api_url}/cat?arg={cid}")
            
            if response.status_code != 200:
                raise Exception(f"IPFS download failed with status code {response.status_code}: {response.text}")
            
            return response.content
        except Exception as e:
            logger.error(f"Local IPFS download failed: {str(e)}")
            raise
    
    def _download_from_web3_storage(self, cid: str) -> bytes:
        """
        Download data from Web3.Storage.
        
        Args:
            cid (str): IPFS CID (Content Identifier)
            
        Returns:
            bytes: Downloaded data
        """
        try:
            # Get data from Web3.Storage gateway
            response = requests.get(f"https://{cid}.ipfs.w3s.link")
            
            if response.status_code != 200:
                raise Exception(f"Web3.Storage download failed with status code {response.status_code}: {response.text}")
            
            return response.content
        except Exception as e:
            logger.error(f"Web3.Storage download failed: {str(e)}")
            raise
    
    def _download_from_infura_ipfs(self, cid: str) -> bytes:
        """
        Download data from Infura IPFS.
        
        Args:
            cid (str): IPFS CID (Content Identifier)
            
        Returns:
            bytes: Downloaded data
        """
        try:
            if not self.infura_ipfs_project_id or not self.infura_ipfs_project_secret:
                raise ValueError("Infura IPFS credentials not provided")
            
            # Prepare auth
            auth = (self.infura_ipfs_project_id, self.infura_ipfs_project_secret)
            
            # Get data from Infura IPFS
            response = requests.post(
                f"https://ipfs.infura.io:5001/api/v0/cat?arg={cid}",
                auth=auth
            )
            
            if response.status_code != 200:
                raise Exception(f"Infura IPFS download failed with status code {response.status_code}: {response.text}")
            
            return response.content
        except Exception as e:
            logger.error(f"Infura IPFS download failed: {str(e)}")
            raise
    
    def download_and_decrypt_file(self, cid: str, password: str, salt: str) -> Dict[str, Any]:
        """
        Download and decrypt a file from IPFS.
        
        Args:
            cid (str): IPFS CID (Content Identifier)
            password (str): Password for decryption
            salt (str): Base64-encoded salt used for encryption
            
        Returns:
            dict: Decryption result with file data and metadata
        """
        try:
            # Download from IPFS based on configured service
            if self.ipfs_service == "web3.storage":
                encrypted_data = self._download_from_web3_storage(cid)
            elif self.ipfs_service == "infura":
                encrypted_data = self._download_from_infura_ipfs(cid)
            else:  # local
                encrypted_data = self._download_from_local_ipfs(cid)
            
            # Decrypt data
            decrypted_data = self.decrypt_file(encrypted_data, password, salt)
            
            # Calculate hash for integrity verification
            decrypted_hash = hashlib.sha256(decrypted_data).hexdigest()
            
            return {
                "decrypted_data": decrypted_data,
                "decrypted_hash": decrypted_hash,
                "size": len(decrypted_data),
                "encrypted_size": len(encrypted_data)
            }
        except Exception as e:
            logger.error(f"Download and decrypt file failed: {str(e)}")
            raise
    
    def verify_file_integrity(self, file_data: bytes, original_hash: str) -> bool:
        """
        Verify the integrity of a file by comparing its hash.
        
        Args:
            file_data (bytes): File data to verify
            original_hash (str): Original SHA-256 hash to compare against
            
        Returns:
            bool: True if the file is intact, False otherwise
        """
        try:
            # Calculate hash of file data
            file_hash = hashlib.sha256(file_data).hexdigest()
            
            # Compare hashes
            return file_hash == original_hash
        except Exception as e:
            logger.error(f"File integrity verification failed: {str(e)}")
            return False
    
    def get_ipfs_gateway_url(self, cid: str) -> str:
        """
        Get a public gateway URL for an IPFS CID.
        
        Args:
            cid (str): IPFS CID (Content Identifier)
            
        Returns:
            str: Public gateway URL
        """
        if self.ipfs_service == "web3.storage":
            return f"https://{cid}.ipfs.w3s.link"
        elif self.ipfs_service == "infura":
            return f"https://ipfs.infura.io/ipfs/{cid}"
        else:
            return f"https://ipfs.io/ipfs/{cid}"

# Example usage
def main():
    # Initialize IPFS manager
    ipfs_manager = IPFSManager()
    
    # For demonstration, we'll just print the initialization
    print(f"IPFS manager initialized with service: {ipfs_manager.ipfs_service}")
    
    # Example encryption (without actual upload)
    try:
        test_data = b"This is a test file for encryption and IPFS."
        test_password = "secure_password123"
        
        encryption_result = ipfs_manager.encrypt_file(test_data, test_password)
        print(f"Encryption successful. Original hash: {encryption_result['original_hash']}")
        
        # Example decryption
        decrypted_data = ipfs_manager.decrypt_file(
            encryption_result['encrypted_data'],
            test_password,
            encryption_result['salt']
        )
        
        # Verify integrity
        is_intact = ipfs_manager.verify_file_integrity(decrypted_data, encryption_result['original_hash'])
        print(f"Decryption successful. Integrity check: {is_intact}")
        print(f"Decrypted content: {decrypted_data.decode()}")
    except Exception as e:
        print(f"Error in demonstration: {str(e)}")

if __name__ == "__main__":
    main()