// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title AuditContract
 * @dev Manages audit logs for healthcare data access
 */
contract AuditContract {
    // Struct to store access log details
    struct AccessLog {
        address patient;
        address accessor;
        string resourceId;
        string accessType;
        uint256 timestamp;
    }
    
    // Array of all access logs
    AccessLog[] private accessLogs;
    
    // Mapping from patient address => array of access log indices
    mapping(address => uint256[]) private patientAccessLogs;
    
    // Events
    event AccessLogged(address indexed patient, address indexed accessor, string resourceId, string accessType, uint256 timestamp);
    
    /**
     * @dev Log an access event
     * @param patient Address of the patient whose data was accessed
     * @param accessor Address of the entity accessing the data
     * @param resourceId Identifier for the accessed resource
     * @param accessType Type of access (view, download, etc.)
     * @param timestamp Unix timestamp when access occurred
     */
    function logAccess(
        address patient,
        address accessor,
        string memory resourceId,
        string memory accessType,
        uint256 timestamp
    ) public {
        // Validate inputs
        require(patient != address(0), "Invalid patient address");
        require(accessor != address(0), "Invalid accessor address");
        require(bytes(resourceId).length > 0, "Resource ID cannot be empty");
        require(bytes(accessType).length > 0, "Access type cannot be empty");
        
        // Create access log
        AccessLog memory log = AccessLog({
            patient: patient,
            accessor: accessor,
            resourceId: resourceId,
            accessType: accessType,
            timestamp: timestamp
        });
        
        // Store access log
        accessLogs.push(log);
        uint256 logIndex = accessLogs.length - 1;
        patientAccessLogs[patient].push(logIndex);
        
        // Emit event
        emit AccessLogged(patient, accessor, resourceId, accessType, timestamp);
    }
    
    /**
     * @dev Get the number of access logs for a patient
     * @param patient Address of the patient
     * @return Number of access logs
     */
    function getAccessLogCount(address patient) public view returns (uint256) {
        return patientAccessLogs[patient].length;
    }
    
    /**
     * @dev Get a specific access log for a patient
     * @param patient Address of the patient
     * @param index Index of the access log
     * @return patient Patient address
     * @return accessor Accessor address
     * @return resourceId Resource ID
     * @return accessType Access type
     * @return timestamp Timestamp
     */
    function getAccessLog(
        address patient,
        uint256 index
    ) public view returns (address, address, string memory, string memory, uint256) {
        require(index < patientAccessLogs[patient].length, "Index out of bounds");
        
        uint256 logIndex = patientAccessLogs[patient][index];
        AccessLog memory log = accessLogs[logIndex];
        
        return (
            log.patient,
            log.accessor,
            log.resourceId,
            log.accessType,
            log.timestamp
        );
    }
    
    /**
     * @dev Get access logs for a patient within a time range
     * @param patient Address of the patient
     * @param startTime Start of time range (Unix timestamp)
     * @param endTime End of time range (Unix timestamp)
     * @param maxResults Maximum number of results to return
     * @return Array of log indices that match the criteria
     */
    function getAccessLogsInTimeRange(
        address patient,
        uint256 startTime,
        uint256 endTime,
        uint256 maxResults
    ) public view returns (uint256[] memory) {
        require(startTime <= endTime, "Start time must be before end time");
        
        uint256[] memory patientLogs = patientAccessLogs[patient];
        uint256 count = 0;
        
        // First pass: count matching logs
        for (uint256 i = 0; i < patientLogs.length && count < maxResults; i++) {
            AccessLog memory log = accessLogs[patientLogs[i]];
            if (log.timestamp >= startTime && log.timestamp <= endTime) {
                count++;
            }
        }
        
        // Create result array
        uint256[] memory result = new uint256[](count);
        count = 0;
        
        // Second pass: fill result array
        for (uint256 i = 0; i < patientLogs.length && count < result.length; i++) {
            AccessLog memory log = accessLogs[patientLogs[i]];
            if (log.timestamp >= startTime && log.timestamp <= endTime) {
                result[count] = patientLogs[i];
                count++;
            }
        }
        
        return result;
    }
    
    /**
     * @dev Get access logs for a specific accessor
     * @param accessor Address of the accessor
     * @param maxResults Maximum number of results to return
     * @return Array of log indices that match the criteria
     */
    function getAccessLogsByAccessor(
        address accessor,
        uint256 maxResults
    ) public view returns (uint256[] memory) {
        uint256 count = 0;
        
        // First pass: count matching logs
        for (uint256 i = 0; i < accessLogs.length && count < maxResults; i++) {
            if (accessLogs[i].accessor == accessor) {
                count++;
            }
        }
        
        // Create result array
        uint256[] memory result = new uint256[](count);
        count = 0;
        
        // Second pass: fill result array
        for (uint256 i = 0; i < accessLogs.length && count < result.length; i++) {
            if (accessLogs[i].accessor == accessor) {
                result[count] = i;
                count++;
            }
        }
        
        return result;
    }
}