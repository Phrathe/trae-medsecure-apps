import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../App';

// Doctor Components
const PatientList = () => (
  <div className="p-4">
    <h2 className="text-xl font-semibold mb-4">My Patients</h2>
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Search patients..."
            className="form-input pl-10 pr-4 py-2"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
            </svg>
          </div>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Visit
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {/* Sample patient data */}
            <tr>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600">
                    MP
                  </div>
                  <div className="ml-4">
                    <div className="text-sm font-medium text-gray-900">Michael Peterson</div>
                    <div className="text-sm text-gray-500">42 years old</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">PT-12345</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">2023-07-15</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="badge badge-success">Active</span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button className="text-primary-600 hover:text-primary-900 mr-3">View Records</button>
                <button className="text-secondary-600 hover:text-secondary-900">Add Note</button>
              </td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600">
                    JD
                  </div>
                  <div className="ml-4">
                    <div className="text-sm font-medium text-gray-900">Jane Doe</div>
                    <div className="text-sm text-gray-500">35 years old</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">PT-12346</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">2023-07-20</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="badge badge-warning">Follow-up Required</span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button className="text-primary-600 hover:text-primary-900 mr-3">View Records</button>
                <button className="text-secondary-600 hover:text-secondary-900">Add Note</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

const UploadRecords = () => (
  <div className="p-4">
    <h2 className="text-xl font-semibold mb-4">Upload Medical Records</h2>
    <div className="card">
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Patient</label>
        <select className="form-input py-2 w-full">
          <option value="">Select a patient</option>
          <option value="PT-12345">Michael Peterson (PT-12345)</option>
          <option value="PT-12346">Jane Doe (PT-12346)</option>
        </select>
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Record Type</label>
        <select className="form-input py-2 w-full">
          <option value="">Select record type</option>
          <option value="lab_result">Lab Result</option>
          <option value="prescription">Prescription</option>
          <option value="imaging">Imaging</option>
          <option value="clinical_note">Clinical Note</option>
        </select>
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
        <input type="text" className="form-input py-2 w-full" placeholder="Brief description of the record" />
      </div>
      
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">File</label>
        <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
          <div className="space-y-1 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <div className="flex text-sm text-gray-600">
              <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500">
                <span>Upload a file</span>
                <input id="file-upload" name="file-upload" type="file" className="sr-only" />
              </label>
              <p className="pl-1">or drag and drop</p>
            </div>
            <p className="text-xs text-gray-500">
              PDF, JPG, PNG up to 10MB
            </p>
          </div>
        </div>
      </div>
      
      <div className="flex items-center mb-4">
        <input id="consent" name="consent" type="checkbox" className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded" />
        <label htmlFor="consent" className="ml-2 block text-sm text-gray-900">
          I confirm that I have patient consent to upload this record
        </label>
      </div>
      
      <div className="flex justify-end">
        <button className="btn-secondary py-2 px-4 w-auto mr-2">
          Cancel
        </button>
        <button className="btn-primary py-2 px-4 w-auto">
          Upload Record
        </button>
      </div>
    </div>
  </div>
);

const AddNotes = () => (
  <div className="p-4">
    <h2 className="text-xl font-semibold mb-4">Add Medical Notes</h2>
    <div className="card">
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Patient</label>
        <select className="form-input py-2 w-full">
          <option value="">Select a patient</option>
          <option value="PT-12345">Michael Peterson (PT-12345)</option>
          <option value="PT-12346">Jane Doe (PT-12346)</option>
        </select>
      </div>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Note Type</label>
        <select className="form-input py-2 w-full">
          <option value="">Select note type</option>
          <option value="progress">Progress Note</option>
          <option value="consultation">Consultation</option>
          <option value="procedure">Procedure Note</option>
          <option value="discharge">Discharge Summary</option>
        </select>
      </div>
      
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Note Content</label>
        <textarea 
          className="form-input py-2 w-full h-40" 
          placeholder="Enter detailed medical notes here..."
        ></textarea>
        <p className="mt-2 text-sm text-gray-500">
          Note: This content will be scanned for PHI leakage using our BERT model.
        </p>
      </div>
      
      <div className="flex justify-end">
        <button className="btn-secondary py-2 px-4 w-auto mr-2">
          Save as Draft
        </button>
        <button className="btn-primary py-2 px-4 w-auto">
          Submit Note
        </button>
      </div>
    </div>
  </div>
);

const ActivityLogs = () => (
  <div className="p-4">
    <h2 className="text-xl font-semibold mb-4">My Activity Logs</h2>
    <div className="card">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Action
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Patient
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Record Type
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                IP Address
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                2023-07-30 14:25:12
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="badge badge-info">Viewed Record</span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Michael Peterson
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Lab Result
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                192.168.1.105
              </td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                2023-07-30 13:10:45
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="badge badge-success">Added Note</span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Jane Doe
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Progress Note
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                192.168.1.105
              </td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                2023-07-30 10:45:22
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className="badge badge-primary">Uploaded Record</span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Michael Peterson
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                Prescription
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                192.168.1.105
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

// Placeholder for components that haven't been created yet
const PlaceholderComponent = ({ title }) => (
  <div className="p-4">
    <h2 className="text-xl font-semibold mb-4">{title}</h2>
    <div className="card">
      <p>This is a placeholder for the {title} component.</p>
    </div>
  </div>
);

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  // Navigation items
  const navItems = [
    { path: '', label: 'My Patients', icon: 'users' },
    { path: 'upload', label: 'Upload Records', icon: 'upload' },
    { path: 'notes', label: 'Add Notes', icon: 'pencil' },
    { path: 'activity', label: 'Activity Logs', icon: 'document-text' },
    { path: 'settings', label: 'Settings', icon: 'cog' },
  ];
  
  // Helper function to render icon
  const renderIcon = (iconName) => {
    switch (iconName) {
      case 'users':
        return (
          <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
          </svg>
        );
      case 'upload':
        return (
          <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        );
      case 'pencil':
        return (
          <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
          </svg>
        );
      case 'document-text':
        return (
          <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
          </svg>
        );
      case 'cog':
        return (
          <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
          </svg>
        );
      default:
        return null;
    }
  };
  
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64 border-r border-gray-200 bg-white">
          <div className="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4 mb-5">
              <h1 className="text-xl font-bold text-primary-600">MedSecure</h1>
            </div>
            
            {/* Navigation */}
            <nav className="mt-5 flex-1 px-2 space-y-1">
              {navItems.map((item) => {
                const isActive = location.pathname === `/doctor/${item.path}`;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`sidebar-link ${isActive ? 'active' : ''}`}
                  >
                    {renderIcon(item.icon)}
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
          
          {/* User info */}
          <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
            <div className="flex-shrink-0 w-full group block">
              <div className="flex items-center">
                <div className="inline-block h-9 w-9 rounded-full bg-gray-300 text-center text-gray-600 flex items-center justify-center">
                  {user?.name?.charAt(0) || 'D'}
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-700">{user?.name || 'Dr. Smith'}</p>
                  <button 
                    onClick={handleLogout}
                    className="text-xs font-medium text-gray-500 hover:text-gray-700"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div className="md:hidden fixed top-0 inset-x-0 z-40 p-2">
        <div className="rounded-lg shadow-md bg-white ring-1 ring-black ring-opacity-5 overflow-hidden">
          <div className="px-5 pt-4 flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-primary-600">MedSecure</h1>
            </div>
            <div className="-mr-2">
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="bg-white rounded-md p-2 inline-flex items-center justify-center text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
              >
                <span className="sr-only">Open menu</span>
                <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {isMobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>
          
          {isMobileMenuOpen && (
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navItems.map((item) => {
                const isActive = location.pathname === `/doctor/${item.path}`;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`block px-3 py-2 rounded-md text-base font-medium ${isActive ? 'bg-primary-50 text-primary-700' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'}`}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {item.label}
                  </Link>
                );
              })}
              <button 
                onClick={handleLogout}
                className="block w-full text-left px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        <main className="flex-1 relative overflow-y-auto focus:outline-none pt-16 md:pt-0">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              <Routes>
                <Route path="" element={<PatientList />} />
                <Route path="upload" element={<UploadRecords />} />
                <Route path="notes" element={<AddNotes />} />
                <Route path="activity" element={<ActivityLogs />} />
                <Route path="settings" element={<PlaceholderComponent title="Settings" />} />
              </Routes>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;