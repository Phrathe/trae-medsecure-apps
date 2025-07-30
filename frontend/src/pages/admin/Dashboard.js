import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../App';

// Admin Components
import Overview from './Overview';
import UserManagement from './UserManagement';
import SystemLogs from './SystemLogs';
import SecurityAlerts from './SecurityAlerts';
import Settings from './Settings';

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
  const [trustScore, setTrustScore] = useState(85); // Mock trust score
  
  // Mock security alerts
  const [securityAlerts, setSecurityAlerts] = useState([
    { id: 1, severity: 'high', message: 'Unusual login attempt detected', timestamp: new Date() },
    { id: 2, severity: 'medium', message: 'Multiple file access from new IP', timestamp: new Date(Date.now() - 3600000) },
  ]);
  
  useEffect(() => {
    // In a real app, you would fetch the trust score and alerts from your backend
    console.log('Admin dashboard mounted');
    
    // Simulate periodic trust score updates
    const interval = setInterval(() => {
      // Random fluctuation between -2 and +2
      const fluctuation = Math.floor(Math.random() * 5) - 2;
      setTrustScore(prevScore => {
        const newScore = prevScore + fluctuation;
        return Math.min(Math.max(newScore, 0), 100); // Keep between 0 and 100
      });
    }, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  // Navigation items
  const navItems = [
    { path: '', label: 'Overview', icon: 'chart-bar' },
    { path: 'users', label: 'User Management', icon: 'users' },
    { path: 'logs', label: 'System Logs', icon: 'document-text' },
    { path: 'alerts', label: 'Security Alerts', icon: 'shield-exclamation' },
    { path: 'settings', label: 'Settings', icon: 'cog' },
  ];
  
  // Helper function to render icon
  const renderIcon = (iconName) => {
    switch (iconName) {
      case 'chart-bar':
        return (
          <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
          </svg>
        );
      case 'users':
        return (
          <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
          </svg>
        );
      case 'document-text':
        return (
          <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
          </svg>
        );
      case 'shield-exclamation':
        return (
          <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2.001A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clipRule="evenodd" />
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
            
            {/* Trust Score */}
            <div className="px-4 mb-6">
              <div className="p-3 bg-gray-50 rounded-lg">
                <h3 className="text-sm font-medium text-gray-500">Trust Score</h3>
                <div className="mt-1 flex items-center">
                  <span className="text-2xl font-bold text-gray-900">{trustScore}</span>
                  <div className="ml-2 w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className={`h-2.5 rounded-full ${trustScore > 70 ? 'bg-success-500' : trustScore > 40 ? 'bg-warning-500' : 'bg-danger-500'}`} 
                      style={{ width: `${trustScore}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Navigation */}
            <nav className="mt-5 flex-1 px-2 space-y-1">
              {navItems.map((item) => {
                const isActive = location.pathname === `/admin/${item.path}`;
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
                  {user?.name?.charAt(0) || 'A'}
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-700">{user?.name || 'Admin User'}</p>
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
                const isActive = location.pathname === `/admin/${item.path}`;
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
                <Route path="" element={<Overview />} />
                <Route path="users" element={<UserManagement />} />
                <Route path="logs" element={<SystemLogs />} />
                <Route path="alerts" element={<SecurityAlerts />} />
                <Route path="settings" element={<Settings />} />
              </Routes>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

// Placeholder components for admin pages
const Overview = () => (
  <div className="p-4">
    <h2 className="text-xl font-semibold mb-4">Admin Overview</h2>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <div className="card bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-2">System Health</h3>
        <div className="text-3xl font-bold text-success-600">98%</div>
        <p className="text-gray-500 mt-1">All systems operational</p>
      </div>
      
      <div className="card bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Active Users</h3>
        <div className="text-3xl font-bold text-primary-600">247</div>
        <p className="text-gray-500 mt-1">+12% from last week</p>
      </div>
      
      <div className="card bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Security Alerts</h3>
        <div className="text-3xl font-bold text-warning-600">5</div>
        <p className="text-gray-500 mt-1">2 high priority</p>
      </div>
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="card bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          <div className="flex items-start">
            <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
              <svg className="h-5 w-5 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">Dr. Sarah Johnson uploaded a new patient record</p>
              <p className="text-xs text-gray-500">2 minutes ago</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="flex-shrink-0 h-8 w-8 rounded-full bg-success-100 flex items-center justify-center">
              <svg className="h-5 w-5 text-success-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">System backup completed successfully</p>
              <p className="text-xs text-gray-500">15 minutes ago</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="flex-shrink-0 h-8 w-8 rounded-full bg-warning-100 flex items-center justify-center">
              <svg className="h-5 w-5 text-warning-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">Unusual login attempt detected and blocked</p>
              <p className="text-xs text-gray-500">1 hour ago</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="card bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">User Distribution</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-medium text-gray-700">Patients</span>
              <span className="text-sm font-medium text-gray-700">65%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-primary-600 h-2.5 rounded-full" style={{ width: '65%' }}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-medium text-gray-700">Doctors</span>
              <span className="text-sm font-medium text-gray-700">20%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-secondary-600 h-2.5 rounded-full" style={{ width: '20%' }}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-medium text-gray-700">Nurses</span>
              <span className="text-sm font-medium text-gray-700">12%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-success-600 h-2.5 rounded-full" style={{ width: '12%' }}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-medium text-gray-700">Admins</span>
              <span className="text-sm font-medium text-gray-700">3%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div className="bg-danger-600 h-2.5 rounded-full" style={{ width: '3%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const UserManagement = () => (
  <PlaceholderComponent title="User Management" />
);

const SystemLogs = () => (
  <PlaceholderComponent title="System Logs" />
);

const SecurityAlerts = () => (
  <PlaceholderComponent title="Security Alerts" />
);

const Settings = () => (
  <PlaceholderComponent title="Settings" />
);

export default Dashboard;