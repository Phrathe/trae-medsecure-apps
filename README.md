# TRAE-MEDSECURE APP

A secure healthcare application with zero-trust architecture, blockchain-based consent management, and ML-powered security features.

## Core Features

### User Roles and Dashboards
- **Admin**: Manage users, view system logs, modify policies
- **Doctor**: Access and upload patient data, view assigned patient files
- **Nurse**: Read-only access to patient history, add medical notes
- **Patient**: Upload/download own health records, view activity

### Security Features
- Zero Trust Gateway Layer with ML-powered anomaly detection
- Blockchain-based consent and audit management
- AES-256 encryption for all medical records
- IPFS/Filecoin for secure, distributed storage

## Technology Stack

### Frontend
- React.js with Tailwind CSS
- Role-based routing and access controls
- Multi-factor authentication (email + OTP + device posture)

### Backend
- FastAPI for backend API services
- Python ML Model Integration (Autoencoder, Random Forest, BERT)
- SQLite/PostgreSQL for data storage
- Web3.py/ethers.js for blockchain integration
- IPFS/Filecoin SDK for file handling

## Getting Started

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- Ethereum development environment (Ganache, Truffle/Hardhat)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/trae-medsecure-app.git
cd trae-medsecure-app
```

2. Install frontend dependencies
```bash
cd frontend
npm install
```

3. Install backend dependencies
```bash
cd ../backend
pip install -r requirements.txt
```

4. Start the development servers
```bash
# Terminal 1 - Frontend
cd frontend
npm start

# Terminal 2 - Backend
cd backend
python main.py
```

## Project Structure

```
├── frontend/                # React.js frontend application
│   ├── public/              # Static files
│   ├── src/                 # Source code
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components for each role
│   │   ├── services/        # API services
│   │   ├── utils/           # Utility functions
│   │   └── App.js           # Main application component
│   └── package.json         # Frontend dependencies
│
├── backend/                 # FastAPI backend application
│   ├── api/                 # API endpoints
│   ├── blockchain/          # Blockchain integration
│   ├── ml/                  # Machine learning models
│   │   ├── autoencoder/     # Anomaly detection model
│   │   ├── random_forest/   # Trust scoring model
│   │   └── bert/            # Data leakage detection model
│   ├── storage/             # IPFS/Filecoin integration
│   ├── database/            # Database models and connections
│   └── main.py              # Main application entry point
│
├── smart_contracts/         # Ethereum smart contracts
│   ├── contracts/           # Solidity contract files
│   ├── migrations/          # Deployment scripts
│   └── truffle-config.js    # Truffle configuration
│
└── README.md                # Project documentation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.