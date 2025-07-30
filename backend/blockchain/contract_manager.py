import json
import os
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import geth_poa_middleware
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractManager:
    """
    Manages interactions with Ethereum smart contracts for the MedSecure application.
    Handles consent management, audit logging, and data integrity verification.
    """
    
    def __init__(self, network: str = "development", private_key: Optional[str] = None):
        """
        Initialize the contract manager with network configuration.
        
        Args:
            network (str): Network to connect to (development, testnet, mainnet)
            private_key (str, optional): Private key for signing transactions
        """
        self.network = network
        self.private_key = private_key or os.environ.get("ETHEREUM_PRIVATE_KEY")
        self.account: Optional[LocalAccount] = None
        self.w3 = None
        self.contracts = {}
        
        # Initialize Web3 connection and account
        self._initialize_web3()
        if self.private_key:
            self._initialize_account()
    
    def _initialize_web3(self):
        """
        Initialize Web3 connection based on the selected network.
        """
        if self.network == "development":
            # Connect to local Ganache instance
            self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        elif self.network == "testnet":
            # Connect to Goerli testnet
            infura_key = os.environ.get("INFURA_API_KEY", "")
            self.w3 = Web3(Web3.HTTPProvider(f"https://goerli.infura.io/v3/{infura_key}"))
            # Add middleware for POA networks like Goerli
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        elif self.network == "polygon":
            # Connect to Polygon (Matic) network
            infura_key = os.environ.get("INFURA_API_KEY", "")
            self.w3 = Web3(Web3.HTTPProvider(f"https://polygon-mainnet.infura.io/v3/{infura_key}"))
        elif self.network == "mainnet":
            # Connect to Ethereum mainnet
            infura_key = os.environ.get("INFURA_API_KEY", "")
            self.w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{infura_key}"))
        else:
            raise ValueError(f"Unsupported network: {self.network}")
        
        # Check connection
        if not self.w3.is_connected():
            logger.warning(f"Failed to connect to {self.network}")
        else:
            logger.info(f"Connected to {self.network}")
            logger.info(f"Current block number: {self.w3.eth.block_number}")
    
    def _initialize_account(self):
        """
        Initialize account from private key for transaction signing.
        """
        if not self.private_key:
            logger.warning("No private key provided. Read-only mode enabled.")
            return
        
        try:
            self.account = Account.from_key(self.private_key)
            logger.info(f"Account initialized: {self.account.address}")
        except Exception as e:
            logger.error(f"Failed to initialize account: {str(e)}")
            self.account = None
    
    def load_contract(self, contract_name: str, contract_address: str, abi_path: str) -> bool:
        """
        Load a contract by name, address, and ABI.
        
        Args:
            contract_name (str): Name to reference the contract
            contract_address (str): Ethereum address of the deployed contract
            abi_path (str): Path to the contract's ABI JSON file
            
        Returns:
            bool: True if contract was loaded successfully
        """
        try:
            # Load ABI from file
            with open(abi_path, 'r') as f:
                contract_abi = json.load(f)
            
            # Create contract instance
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)
            self.contracts[contract_name] = contract
            logger.info(f"Contract '{contract_name}' loaded at {contract_address}")
            return True
        except Exception as e:
            logger.error(f"Failed to load contract '{contract_name}': {str(e)}")
            return False
    
    def _build_transaction(self, contract_function) -> Dict[str, Any]:
        """
        Build a transaction dictionary for a contract function call.
        
        Args:
            contract_function: Contract function to call
            
        Returns:
            dict: Transaction dictionary
        """
        if not self.account:
            raise ValueError("No account available for transaction signing")
        
        # Get gas price strategy based on network
        if self.network in ["mainnet", "polygon"]:
            gas_price = self.w3.eth.gas_price
            # Add 10% buffer for mainnet transactions
            gas_price = int(gas_price * 1.1)
        else:
            gas_price = self.w3.eth.gas_price
        
        # Build transaction
        tx = contract_function.build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 2000000,  # Gas limit
            'gasPrice': gas_price
        })
        
        return tx
    
    def _send_transaction(self, tx: Dict[str, Any]) -> str:
        """
        Sign and send a transaction.
        
        Args:
            tx (dict): Transaction dictionary
            
        Returns:
            str: Transaction hash
        """
        if not self.account:
            raise ValueError("No account available for transaction signing")
        
        # Sign transaction
        signed_tx = self.account.sign_transaction(tx)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Check status
        if tx_receipt['status'] == 1:
            logger.info(f"Transaction successful: {tx_hash.hex()}")
        else:
            logger.error(f"Transaction failed: {tx_hash.hex()}")
        
        return tx_hash.hex()
    
    # Consent Contract Methods
    def grant_consent(self, patient_address: str, provider_address: str, 
                     access_level: str, start_date: int, end_date: int, 
                     purpose: str) -> Dict[str, Any]:
        """
        Grant consent for a provider to access patient data.
        
        Args:
            patient_address (str): Ethereum address of the patient
            provider_address (str): Ethereum address of the healthcare provider
            access_level (str): Level of access (full, limited, temporary)
            start_date (int): Unix timestamp for consent start
            end_date (int): Unix timestamp for consent end
            purpose (str): Purpose for data access
            
        Returns:
            dict: Transaction details
        """
        if 'ConsentContract' not in self.contracts:
            raise ValueError("ConsentContract not loaded")
        
        contract = self.contracts['ConsentContract']
        
        # Prepare function call
        function_call = contract.functions.grantConsent(
            self.w3.to_checksum_address(provider_address),
            access_level,
            start_date,
            end_date,
            purpose
        )
        
        # Build and send transaction
        tx = self._build_transaction(function_call)
        tx_hash = self._send_transaction(tx)
        
        return {
            'transaction_hash': tx_hash,
            'patient_address': patient_address,
            'provider_address': provider_address,
            'access_level': access_level,
            'start_date': datetime.fromtimestamp(start_date).isoformat(),
            'end_date': datetime.fromtimestamp(end_date).isoformat(),
            'purpose': purpose,
            'timestamp': datetime.now().isoformat()
        }
    
    def revoke_consent(self, provider_address: str) -> Dict[str, Any]:
        """
        Revoke consent for a provider.
        
        Args:
            provider_address (str): Ethereum address of the healthcare provider
            
        Returns:
            dict: Transaction details
        """
        if 'ConsentContract' not in self.contracts:
            raise ValueError("ConsentContract not loaded")
        
        contract = self.contracts['ConsentContract']
        
        # Prepare function call
        function_call = contract.functions.revokeConsent(
            self.w3.to_checksum_address(provider_address)
        )
        
        # Build and send transaction
        tx = self._build_transaction(function_call)
        tx_hash = self._send_transaction(tx)
        
        return {
            'transaction_hash': tx_hash,
            'provider_address': provider_address,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_consent(self, patient_address: str, provider_address: str) -> Dict[str, Any]:
        """
        Check if consent exists and is valid.
        
        Args:
            patient_address (str): Ethereum address of the patient
            provider_address (str): Ethereum address of the healthcare provider
            
        Returns:
            dict: Consent details
        """
        if 'ConsentContract' not in self.contracts:
            raise ValueError("ConsentContract not loaded")
        
        contract = self.contracts['ConsentContract']
        
        # Call view function (no transaction needed)
        result = contract.functions.checkConsent(
            self.w3.to_checksum_address(patient_address),
            self.w3.to_checksum_address(provider_address)
        ).call()
        
        # Parse result based on contract return values
        # This will depend on your specific contract implementation
        has_consent, access_level, start_date, end_date, purpose = result
        
        return {
            'has_consent': has_consent,
            'access_level': access_level,
            'start_date': datetime.fromtimestamp(start_date).isoformat() if start_date > 0 else None,
            'end_date': datetime.fromtimestamp(end_date).isoformat() if end_date > 0 else None,
            'purpose': purpose,
            'is_valid': has_consent and (start_date <= datetime.now().timestamp() <= end_date)
        }
    
    # Audit Contract Methods
    def log_access(self, patient_address: str, accessor_address: str, 
                  resource_id: str, access_type: str) -> Dict[str, Any]:
        """
        Log an access event to the blockchain.
        
        Args:
            patient_address (str): Ethereum address of the patient
            accessor_address (str): Ethereum address of the accessor
            resource_id (str): ID of the accessed resource
            access_type (str): Type of access (view, download, etc.)
            
        Returns:
            dict: Transaction details
        """
        if 'AuditContract' not in self.contracts:
            raise ValueError("AuditContract not loaded")
        
        contract = self.contracts['AuditContract']
        
        # Prepare function call
        function_call = contract.functions.logAccess(
            self.w3.to_checksum_address(patient_address),
            self.w3.to_checksum_address(accessor_address),
            resource_id,
            access_type,
            int(datetime.now().timestamp())
        )
        
        # Build and send transaction
        tx = self._build_transaction(function_call)
        tx_hash = self._send_transaction(tx)
        
        return {
            'transaction_hash': tx_hash,
            'patient_address': patient_address,
            'accessor_address': accessor_address,
            'resource_id': resource_id,
            'access_type': access_type,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_access_logs(self, patient_address: str, start_time: int, end_time: int) -> List[Dict[str, Any]]:
        """
        Get access logs for a patient within a time range.
        
        Args:
            patient_address (str): Ethereum address of the patient
            start_time (int): Unix timestamp for start of range
            end_time (int): Unix timestamp for end of range
            
        Returns:
            list: Access log entries
        """
        if 'AuditContract' not in self.contracts:
            raise ValueError("AuditContract not loaded")
        
        contract = self.contracts['AuditContract']
        
        # Call view function (no transaction needed)
        # This implementation will depend on your specific contract
        # For demonstration, we'll return a mock result
        
        # In a real implementation, you would query events or a mapping
        # Example: logs = contract.events.AccessLogged.get_logs(fromBlock=0, toBlock='latest')
        
        # Mock result for demonstration
        logs = [
            {
                'patient_address': patient_address,
                'accessor_address': '0x1234567890123456789012345678901234567890',
                'resource_id': 'record_001',
                'access_type': 'view',
                'timestamp': datetime.fromtimestamp(start_time + 100).isoformat()
            },
            {
                'patient_address': patient_address,
                'accessor_address': '0x2345678901234567890123456789012345678901',
                'resource_id': 'record_002',
                'access_type': 'download',
                'timestamp': datetime.fromtimestamp(start_time + 200).isoformat()
            }
        ]
        
        return logs
    
    # Data Hash Contract Methods
    def store_data_hash(self, data_id: str, data_hash: str, data_type: str) -> Dict[str, Any]:
        """
        Store a data hash on the blockchain for integrity verification.
        
        Args:
            data_id (str): ID of the data
            data_hash (str): SHA-256 hash of the data
            data_type (str): Type of data (medical record, prescription, etc.)
            
        Returns:
            dict: Transaction details
        """
        if 'DataHashContract' not in self.contracts:
            raise ValueError("DataHashContract not loaded")
        
        contract = self.contracts['DataHashContract']
        
        # Prepare function call
        function_call = contract.functions.storeDataHash(
            data_id,
            data_hash,
            data_type,
            int(datetime.now().timestamp())
        )
        
        # Build and send transaction
        tx = self._build_transaction(function_call)
        tx_hash = self._send_transaction(tx)
        
        return {
            'transaction_hash': tx_hash,
            'data_id': data_id,
            'data_hash': data_hash,
            'data_type': data_type,
            'timestamp': datetime.now().isoformat()
        }
    
    def verify_data_hash(self, data_id: str, data_hash: str) -> Dict[str, Any]:
        """
        Verify a data hash against the stored hash on the blockchain.
        
        Args:
            data_id (str): ID of the data
            data_hash (str): SHA-256 hash to verify
            
        Returns:
            dict: Verification result
        """
        if 'DataHashContract' not in self.contracts:
            raise ValueError("DataHashContract not loaded")
        
        contract = self.contracts['DataHashContract']
        
        # Call view function (no transaction needed)
        result = contract.functions.verifyDataHash(data_id, data_hash).call()
        
        # Parse result
        is_valid, stored_hash, timestamp, data_type = result
        
        return {
            'is_valid': is_valid,
            'data_id': data_id,
            'stored_hash': stored_hash,
            'provided_hash': data_hash,
            'timestamp': datetime.fromtimestamp(timestamp).isoformat() if timestamp > 0 else None,
            'data_type': data_type
        }

# Example usage
def main():
    # Initialize contract manager
    manager = ContractManager(network="development")
    
    # Load contracts (in a real app, these would be deployed contracts)
    # For demonstration, we'll just print the initialization
    print(f"Contract manager initialized for network: {manager.network}")
    print(f"Web3 connection: {manager.w3.is_connected()}")
    
    if manager.account:
        print(f"Account address: {manager.account.address}")
        print(f"Current balance: {manager.w3.eth.get_balance(manager.account.address)} wei")
    else:
        print("No account initialized (read-only mode)")

if __name__ == "__main__":
    main()