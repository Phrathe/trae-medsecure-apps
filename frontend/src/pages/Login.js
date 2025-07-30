import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../App';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [step, setStep] = useState('email'); // email, otp, device
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  
  // Validation schemas for each step
  const emailSchema = Yup.object().shape({
    email: Yup.string().email('Invalid email').required('Email is required'),
    password: Yup.string().required('Password is required'),
  });
  
  const otpSchema = Yup.object().shape({
    otp: Yup.string().required('OTP is required').length(6, 'OTP must be 6 digits'),
  });
  
  // Handle email/password submission
  const handleEmailSubmit = async (values, { setSubmitting }) => {
    try {
      setError('');
      // In a real app, this would be an API call to your backend
      // const response = await axios.post('/api/login', { email: values.email, password: values.password });
      
      // For demo purposes, we'll simulate a successful response
      // In production, you would verify credentials with your backend
      setEmail(values.email);
      setStep('otp');
      
      // Simulate sending OTP to user's email
      console.log(`OTP sent to ${values.email}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };
  
  // Handle OTP verification
  const handleOtpSubmit = async (values, { setSubmitting }) => {
    try {
      setError('');
      // In a real app, this would be an API call to verify the OTP
      // const response = await axios.post('/api/verify-otp', { email, otp: values.otp });
      
      // For demo purposes, we'll simulate a successful response
      // In production, you would verify the OTP with your backend
      setStep('device');
    } catch (err) {
      setError(err.response?.data?.message || 'Invalid OTP. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };
  
  // Handle device posture check
  const handleDeviceCheck = async () => {
    try {
      setError('');
      // In a real app, this would check device security posture
      // const response = await axios.post('/api/check-device');
      
      // For demo purposes, we'll simulate a successful login
      // In production, you would get a real token from your backend
      const mockUser = {
        id: '123',
        name: 'Demo User',
        email,
        role: 'admin', // This would come from your backend based on the user
      };
      
      const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyMyIsImVtYWlsIjoiYWRtaW5AZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE2MjUxMjM0NTZ9.XYZ';
      
      // Set user in auth context
      login(mockUser, mockToken);
      
      // Redirect based on role
      navigate(`/${mockUser.role}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Device verification failed. Please try again.');
    }
  };
  
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="auth-card">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">MedSecure</h1>
          <p className="text-gray-600 mt-2">Secure Healthcare Platform</p>
        </div>
        
        {error && (
          <div className="alert-danger mb-4">
            {error}
          </div>
        )}
        
        {step === 'email' && (
          <Formik
            initialValues={{ email: '', password: '' }}
            validationSchema={emailSchema}
            onSubmit={handleEmailSubmit}
          >
            {({ isSubmitting }) => (
              <Form>
                <div className="mb-4">
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <Field type="email" name="email" className="form-input" />
                  <ErrorMessage name="email" component="div" className="text-danger-600 text-sm mt-1" />
                </div>
                
                <div className="mb-6">
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                  <Field type="password" name="password" className="form-input" />
                  <ErrorMessage name="password" component="div" className="text-danger-600 text-sm mt-1" />
                </div>
                
                <button type="submit" className="btn-primary" disabled={isSubmitting}>
                  {isSubmitting ? 'Logging in...' : 'Continue'}
                </button>
                
                <div className="mt-4 text-center text-sm">
                  <p>Don't have an account? <Link to="/register" className="text-primary-600 hover:text-primary-800">Register</Link></p>
                </div>
              </Form>
            )}
          </Formik>
        )}
        
        {step === 'otp' && (
          <div>
            <p className="mb-4 text-gray-600">We've sent a verification code to {email}</p>
            
            <Formik
              initialValues={{ otp: '' }}
              validationSchema={otpSchema}
              onSubmit={handleOtpSubmit}
            >
              {({ isSubmitting }) => (
                <Form>
                  <div className="mb-6">
                    <label htmlFor="otp" className="block text-sm font-medium text-gray-700 mb-1">Verification Code</label>
                    <Field type="text" name="otp" className="form-input" />
                    <ErrorMessage name="otp" component="div" className="text-danger-600 text-sm mt-1" />
                  </div>
                  
                  <button type="submit" className="btn-primary" disabled={isSubmitting}>
                    {isSubmitting ? 'Verifying...' : 'Verify'}
                  </button>
                  
                  <div className="mt-4 text-center text-sm">
                    <button 
                      type="button" 
                      className="text-primary-600 hover:text-primary-800"
                      onClick={() => setStep('email')}
                    >
                      Back to login
                    </button>
                  </div>
                </Form>
              )}
            </Formik>
          </div>
        )}
        
        {step === 'device' && (
          <div>
            <p className="mb-4 text-gray-600">Checking device security...</p>
            
            <div className="mb-6">
              <div className="bg-primary-50 p-4 rounded-md">
                <p className="text-primary-800 font-medium">Device Security Check</p>
                <ul className="mt-2 space-y-1 text-sm">
                  <li className="flex items-center">
                    <svg className="h-5 w-5 text-success-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Operating System: Windows 10
                  </li>
                  <li className="flex items-center">
                    <svg className="h-5 w-5 text-success-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Firewall: Active
                  </li>
                  <li className="flex items-center">
                    <svg className="h-5 w-5 text-success-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Antivirus: Up to date
                  </li>
                  <li className="flex items-center">
                    <svg className="h-5 w-5 text-success-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Browser: Secure version
                  </li>
                </ul>
              </div>
            </div>
            
            <button type="button" className="btn-primary" onClick={handleDeviceCheck}>
              Complete Login
            </button>
            
            <div className="mt-4 text-center text-sm">
              <button 
                type="button" 
                className="text-primary-600 hover:text-primary-800"
                onClick={() => setStep('otp')}
              >
                Back to verification
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;