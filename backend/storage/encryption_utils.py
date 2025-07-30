import os
import base64
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EncryptionUtils:
    """
    Utility class for encryption and decryption operations in the MedSecure application.
    Provides methods for symmetric (AES) and asymmetric (RSA) encryption.
    """
    
    @staticmethod
    def generate_key_from_password(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Generate a symmetric encryption key from a password using PBKDF2.
        
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
    
    @staticmethod
    def encrypt_with_fernet(data: bytes, key: bytes) -> bytes:
        """
        Encrypt data using Fernet symmetric encryption (AES-128-CBC).
        
        Args:
            data (bytes): Data to encrypt
            key (bytes): Fernet key (must be URL-safe base64-encoded)
            
        Returns:
            bytes: Encrypted data
        """
        cipher = Fernet(key)
        return cipher.encrypt(data)
    
    @staticmethod
    def decrypt_with_fernet(encrypted_data: bytes, key: bytes) -> bytes:
        """
        Decrypt data using Fernet symmetric encryption (AES-128-CBC).
        
        Args:
            encrypted_data (bytes): Data to decrypt
            key (bytes): Fernet key (must be URL-safe base64-encoded)
            
        Returns:
            bytes: Decrypted data
        """
        cipher = Fernet(key)
        return cipher.decrypt(encrypted_data)
    
    @staticmethod
    def encrypt_aes_gcm(data: bytes, key: bytes, associated_data: Optional[bytes] = None) -> Dict[str, bytes]:
        """
        Encrypt data using AES-256-GCM with authentication.
        
        Args:
            data (bytes): Data to encrypt
            key (bytes): 32-byte key for AES-256
            associated_data (bytes, optional): Additional authenticated data
            
        Returns:
            dict: Encrypted data, nonce, and tag
        """
        # Generate a random 96-bit IV (nonce)
        nonce = os.urandom(12)
        
        # Create an encryptor object
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce)
        )
        encryptor = cipher.encryptor()
        
        # Update with associated data if provided
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)
        
        # Encrypt the data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return {
            "ciphertext": ciphertext,
            "nonce": nonce,
            "tag": encryptor.tag
        }
    
    @staticmethod
    def decrypt_aes_gcm(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes, 
                       associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt data using AES-256-GCM with authentication.
        
        Args:
            ciphertext (bytes): Data to decrypt
            key (bytes): 32-byte key for AES-256
            nonce (bytes): 12-byte nonce used for encryption
            tag (bytes): Authentication tag
            associated_data (bytes, optional): Additional authenticated data
            
        Returns:
            bytes: Decrypted data
        """
        # Create a decryptor object
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag)
        )
        decryptor = cipher.decryptor()
        
        # Update with associated data if provided
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)
        
        # Decrypt the data
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    @staticmethod
    def generate_rsa_key_pair(key_size: int = 2048) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """
        Generate an RSA key pair for asymmetric encryption.
        
        Args:
            key_size (int): Size of the RSA key in bits
            
        Returns:
            tuple: (private_key, public_key)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        public_key = private_key.public_key()
        
        return private_key, public_key
    
    @staticmethod
    def serialize_rsa_private_key(private_key: rsa.RSAPrivateKey) -> bytes:
        """
        Serialize an RSA private key to PEM format.
        
        Args:
            private_key (RSAPrivateKey): RSA private key
            
        Returns:
            bytes: PEM-encoded private key
        """
        return private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        )
    
    @staticmethod
    def serialize_rsa_public_key(public_key: rsa.RSAPublicKey) -> bytes:
        """
        Serialize an RSA public key to PEM format.
        
        Args:
            public_key (RSAPublicKey): RSA public key
            
        Returns:
            bytes: PEM-encoded public key
        """
        return public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )
    
    @staticmethod
    def load_rsa_private_key(pem_data: bytes, password: Optional[bytes] = None) -> rsa.RSAPrivateKey:
        """
        Load an RSA private key from PEM format.
        
        Args:
            pem_data (bytes): PEM-encoded private key
            password (bytes, optional): Password if the key is encrypted
            
        Returns:
            RSAPrivateKey: RSA private key
        """
        return load_pem_private_key(pem_data, password)
    
    @staticmethod
    def load_rsa_public_key(pem_data: bytes) -> rsa.RSAPublicKey:
        """
        Load an RSA public key from PEM format.
        
        Args:
            pem_data (bytes): PEM-encoded public key
            
        Returns:
            RSAPublicKey: RSA public key
        """
        return load_pem_public_key(pem_data)
    
    @staticmethod
    def encrypt_with_rsa(data: bytes, public_key: rsa.RSAPublicKey) -> bytes:
        """
        Encrypt data using RSA with OAEP padding.
        
        Args:
            data (bytes): Data to encrypt (must be smaller than key size - padding)
            public_key (RSAPublicKey): RSA public key
            
        Returns:
            bytes: Encrypted data
        """
        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    @staticmethod
    def decrypt_with_rsa(encrypted_data: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
        """
        Decrypt data using RSA with OAEP padding.
        
        Args:
            encrypted_data (bytes): Data to decrypt
            private_key (RSAPrivateKey): RSA private key
            
        Returns:
            bytes: Decrypted data
        """
        return private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    @staticmethod
    def hybrid_encrypt(data: bytes, public_key: rsa.RSAPublicKey) -> Dict[str, bytes]:
        """
        Encrypt data using a hybrid approach (AES + RSA).
        Generates a random AES key, encrypts the data with AES, then encrypts the AES key with RSA.
        
        Args:
            data (bytes): Data to encrypt
            public_key (RSAPublicKey): RSA public key
            
        Returns:
            dict: Encrypted data, encrypted key, and metadata
        """
        # Generate a random AES key
        aes_key = os.urandom(32)  # 256 bits
        
        # Encrypt the data with AES-GCM
        aes_result = EncryptionUtils.encrypt_aes_gcm(data, aes_key)
        
        # Encrypt the AES key with RSA
        encrypted_key = EncryptionUtils.encrypt_with_rsa(aes_key, public_key)
        
        return {
            "ciphertext": aes_result["ciphertext"],
            "nonce": aes_result["nonce"],
            "tag": aes_result["tag"],
            "encrypted_key": encrypted_key
        }
    
    @staticmethod
    def hybrid_decrypt(ciphertext: bytes, encrypted_key: bytes, nonce: bytes, tag: bytes, 
                      private_key: rsa.RSAPrivateKey) -> bytes:
        """
        Decrypt data using a hybrid approach (AES + RSA).
        Decrypts the AES key with RSA, then decrypts the data with AES.
        
        Args:
            ciphertext (bytes): Data to decrypt
            encrypted_key (bytes): Encrypted AES key
            nonce (bytes): AES nonce
            tag (bytes): AES authentication tag
            private_key (RSAPrivateKey): RSA private key
            
        Returns:
            bytes: Decrypted data
        """
        # Decrypt the AES key with RSA
        aes_key = EncryptionUtils.decrypt_with_rsa(encrypted_key, private_key)
        
        # Decrypt the data with AES-GCM
        return EncryptionUtils.decrypt_aes_gcm(ciphertext, aes_key, nonce, tag)
    
    @staticmethod
    def compute_hash(data: bytes, algorithm: str = 'sha256') -> str:
        """
        Compute a hash of the data.
        
        Args:
            data (bytes): Data to hash
            algorithm (str): Hash algorithm to use
            
        Returns:
            str: Hexadecimal hash digest
        """
        if algorithm.lower() == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm.lower() == 'sha512':
            return hashlib.sha512(data).hexdigest()
        elif algorithm.lower() == 'md5':
            return hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

# Example usage
def main():
    # For demonstration purposes
    try:
        # Test symmetric encryption with Fernet
        test_data = b"This is a test message for encryption."
        password = "secure_password123"
        
        # Generate key from password
        key, salt = EncryptionUtils.generate_key_from_password(password)
        print(f"Generated key from password. Salt: {base64.b64encode(salt).decode()}")
        
        # Encrypt with Fernet
        encrypted = EncryptionUtils.encrypt_with_fernet(test_data, key)
        print(f"Encrypted data (Fernet): {base64.b64encode(encrypted).decode()[:30]}...")
        
        # Decrypt with Fernet
        decrypted = EncryptionUtils.decrypt_with_fernet(encrypted, key)
        print(f"Decrypted data (Fernet): {decrypted.decode()}")
        
        # Test AES-GCM encryption
        aes_key = os.urandom(32)  # 256 bits
        aes_result = EncryptionUtils.encrypt_aes_gcm(test_data, aes_key)
        print(f"Encrypted data (AES-GCM): {base64.b64encode(aes_result['ciphertext']).decode()[:30]}...")
        
        # Decrypt with AES-GCM
        decrypted_aes = EncryptionUtils.decrypt_aes_gcm(
            aes_result['ciphertext'], aes_key, aes_result['nonce'], aes_result['tag']
        )
        print(f"Decrypted data (AES-GCM): {decrypted_aes.decode()}")
        
        # Test RSA key generation
        private_key, public_key = EncryptionUtils.generate_rsa_key_pair()
        print("Generated RSA key pair")
        
        # Test hybrid encryption
        hybrid_result = EncryptionUtils.hybrid_encrypt(test_data, public_key)
        print(f"Encrypted data (Hybrid): {base64.b64encode(hybrid_result['ciphertext']).decode()[:30]}...")
        
        # Decrypt with hybrid approach
        decrypted_hybrid = EncryptionUtils.hybrid_decrypt(
            hybrid_result['ciphertext'],
            hybrid_result['encrypted_key'],
            hybrid_result['nonce'],
            hybrid_result['tag'],
            private_key
        )
        print(f"Decrypted data (Hybrid): {decrypted_hybrid.decode()}")
        
        # Test hash computation
        hash_value = EncryptionUtils.compute_hash(test_data)
        print(f"SHA-256 hash: {hash_value}")
        
    except Exception as e:
        print(f"Error in demonstration: {str(e)}")

if __name__ == "__main__":
    main()