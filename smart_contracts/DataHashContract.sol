// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DataHashContract
 * @dev Manages data integrity through hash verification
 */
contract DataHashContract {
    // Struct to store data hash details
    struct DataHashRecord {
        string dataHash;
        uint256 timestamp;
        string dataType;
        address owner;
        bool exists;
    }
    
    // Mapping from data ID => data hash record
    mapping(string => DataHashRecord) private dataHashes;
    
    // Mapping from owner address => array of data IDs
    mapping(address => string[]) private ownerDataIds;
    
    // Events
    event DataHashStored(string indexed dataId, string dataHash, string dataType, uint256 timestamp, address indexed owner);
    event DataHashUpdated(string indexed dataId, string oldHash, string newHash, uint256 timestamp, address indexed owner);
    
    /**
     * @dev Store a data hash for integrity verification
     * @param dataId Unique identifier for the data
     * @param dataHash SHA-256 hash of the data
     * @param dataType Type of data (medical record, prescription, etc.)
     * @param timestamp Unix timestamp when the data was created/modified
     */
    function storeDataHash(
        string memory dataId,
        string memory dataHash,
        string memory dataType,
        uint256 timestamp
    ) public {
        // Validate inputs
        require(bytes(dataId).length > 0, "Data ID cannot be empty");
        require(bytes(dataHash).length > 0, "Data hash cannot be empty");
        require(bytes(dataType).length > 0, "Data type cannot be empty");
        
        // Check if data hash already exists
        if (dataHashes[dataId].exists) {
            // Update existing hash
            string memory oldHash = dataHashes[dataId].dataHash;
            
            dataHashes[dataId].dataHash = dataHash;
            dataHashes[dataId].timestamp = timestamp;
            dataHashes[dataId].dataType = dataType;
            
            // Emit update event
            emit DataHashUpdated(dataId, oldHash, dataHash, timestamp, msg.sender);
        } else {
            // Store new hash
            dataHashes[dataId] = DataHashRecord({
                dataHash: dataHash,
                timestamp: timestamp,
                dataType: dataType,
                owner: msg.sender,
                exists: true
            });
            
            // Add data ID to owner's list
            ownerDataIds[msg.sender].push(dataId);
            
            // Emit store event
            emit DataHashStored(dataId, dataHash, dataType, timestamp, msg.sender);
        }
    }
    
    /**
     * @dev Verify a data hash against the stored hash
     * @param dataId Unique identifier for the data
     * @param dataHash SHA-256 hash to verify
     * @return isValid Whether the hash is valid
     * @return storedHash The stored hash
     * @return timestamp The timestamp of the stored hash
     * @return dataType The type of data
     */
    function verifyDataHash(
        string memory dataId,
        string memory dataHash
    ) public view returns (bool isValid, string memory storedHash, uint256 timestamp, string memory dataType) {
        // Get stored hash record
        DataHashRecord memory record = dataHashes[dataId];
        
        // Check if hash exists
        if (!record.exists) {
            return (false, "", 0, "");
        }
        
        // Compare hashes (using keccak256 for string comparison)
        isValid = keccak256(bytes(record.dataHash)) == keccak256(bytes(dataHash));
        
        return (isValid, record.dataHash, record.timestamp, record.dataType);
    }
    
    /**
     * @dev Get the number of data hashes owned by an address
     * @param owner Address of the owner
     * @return Number of data hashes
     */
    function getDataHashCount(address owner) public view returns (uint256) {
        return ownerDataIds[owner].length;
    }
    
    /**
     * @dev Get a data ID owned by an address
     * @param owner Address of the owner
     * @param index Index of the data ID
     * @return Data ID
     */
    function getDataId(address owner, uint256 index) public view returns (string memory) {
        require(index < ownerDataIds[owner].length, "Index out of bounds");
        return ownerDataIds[owner][index];
    }
    
    /**
     * @dev Get details of a data hash
     * @param dataId Unique identifier for the data
     * @return dataHash The stored hash
     * @return timestamp The timestamp of the stored hash
     * @return dataType The type of data
     * @return owner The owner of the data
     * @return exists Whether the hash exists
     */
    function getDataHashDetails(
        string memory dataId
    ) public view returns (string memory dataHash, uint256 timestamp, string memory dataType, address owner, bool exists) {
        DataHashRecord memory record = dataHashes[dataId];
        return (record.dataHash, record.timestamp, record.dataType, record.owner, record.exists);
    }
    
    /**
     * @dev Check if a data hash exists
     * @param dataId Unique identifier for the data
     * @return Whether the hash exists
     */
    function dataHashExists(string memory dataId) public view returns (bool) {
        return dataHashes[dataId].exists;
    }
}