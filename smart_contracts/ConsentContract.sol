// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ConsentContract
 * @dev Manages patient consent for healthcare data access
 */
contract ConsentContract {
    // Struct to store consent details
    struct Consent {
        bool exists;
        string accessLevel; // "full", "limited", or "temporary"
        uint256 startDate;
        uint256 endDate;
        string purpose;
    }
    
    // Mapping from patient address => provider address => consent details
    mapping(address => mapping(address => Consent)) private consents;
    
    // Events
    event ConsentGranted(address indexed patient, address indexed provider, string accessLevel, uint256 startDate, uint256 endDate, string purpose);
    event ConsentRevoked(address indexed patient, address indexed provider);
    
    /**
     * @dev Grant consent to a healthcare provider
     * @param provider Address of the healthcare provider
     * @param accessLevel Level of access ("full", "limited", "temporary")
     * @param startDate Unix timestamp for when consent begins
     * @param endDate Unix timestamp for when consent expires
     * @param purpose Purpose for data access
     */
    function grantConsent(
        address provider,
        string memory accessLevel,
        uint256 startDate,
        uint256 endDate,
        string memory purpose
    ) public {
        // Validate inputs
        require(provider != address(0), "Invalid provider address");
        require(startDate < endDate, "End date must be after start date");
        require(endDate > block.timestamp, "End date must be in the future");
        
        // Store consent
        consents[msg.sender][provider] = Consent({
            exists: true,
            accessLevel: accessLevel,
            startDate: startDate,
            endDate: endDate,
            purpose: purpose
        });
        
        // Emit event
        emit ConsentGranted(msg.sender, provider, accessLevel, startDate, endDate, purpose);
    }
    
    /**
     * @dev Revoke consent from a healthcare provider
     * @param provider Address of the healthcare provider
     */
    function revokeConsent(address provider) public {
        // Validate inputs
        require(provider != address(0), "Invalid provider address");
        require(consents[msg.sender][provider].exists, "Consent does not exist");
        
        // Delete consent
        delete consents[msg.sender][provider];
        
        // Emit event
        emit ConsentRevoked(msg.sender, provider);
    }
    
    /**
     * @dev Check if consent exists and is valid
     * @param patient Address of the patient
     * @param provider Address of the healthcare provider
     * @return exists Whether consent exists
     * @return accessLevel Level of access
     * @return startDate Start date of consent
     * @return endDate End date of consent
     * @return purpose Purpose for data access
     */
    function checkConsent(
        address patient,
        address provider
    ) public view returns (bool, string memory, uint256, uint256, string memory) {
        // Get consent
        Consent memory consent = consents[patient][provider];
        
        // Return consent details
        return (
            consent.exists && block.timestamp >= consent.startDate && block.timestamp <= consent.endDate,
            consent.accessLevel,
            consent.startDate,
            consent.endDate,
            consent.purpose
        );
    }
    
    /**
     * @dev Check if a provider has valid consent to access patient data
     * @param patient Address of the patient
     * @param provider Address of the healthcare provider
     * @return Whether the provider has valid consent
     */
    function hasValidConsent(address patient, address provider) public view returns (bool) {
        Consent memory consent = consents[patient][provider];
        
        return (
            consent.exists &&
            block.timestamp >= consent.startDate &&
            block.timestamp <= consent.endDate
        );
    }
}