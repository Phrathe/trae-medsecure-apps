import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';

const Register = () => {
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  const validationSchema = Yup.object().shape({
    name: Yup.string().required('Full name is required'),
    email: Yup.string().email('Invalid email').required('Email is required'),
    password: Yup.string()
      .min(8, 'Password must be at least 8 characters')
      .matches(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
        'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
      )
      .required('Password is required'),
    confirmPassword: Yup.string()
      .oneOf([Yup.ref('password'), null], 'Passwords must match')
      .required('Confirm password is required'),
    role: Yup.string().required('Role is required'),
  });
  
  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    try {
      setError('');
      // In a real app, this would be an API call to your backend
      // const response = await axios.post('/api/register', values);
      
      // For demo purposes, we'll simulate a successful response
      console.log('Registration values:', values);
      
      setSuccess(true);
      resetForm();
      
      // Redirect to login after a short delay
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="auth-card">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create Account</h1>
          <p className="text-gray-600 mt-2">Join MedSecure's secure healthcare platform</p>
        </div>
        
        {error && (
          <div className="alert-danger mb-4">
            {error}
          </div>
        )}
        
        {success && (
          <div className="alert-success mb-4">
            Registration successful! Redirecting to login...
          </div>
        )}
        
        <Formik
          initialValues={{
            name: '',
            email: '',
            password: '',
            confirmPassword: '',
            role: '',
          }}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
        >
          {({ isSubmitting }) => (
            <Form>
              <div className="mb-4">
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <Field type="text" name="name" className="form-input" />
                <ErrorMessage name="name" component="div" className="text-danger-600 text-sm mt-1" />
              </div>
              
              <div className="mb-4">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <Field type="email" name="email" className="form-input" />
                <ErrorMessage name="email" component="div" className="text-danger-600 text-sm mt-1" />
              </div>
              
              <div className="mb-4">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <Field type="password" name="password" className="form-input" />
                <ErrorMessage name="password" component="div" className="text-danger-600 text-sm mt-1" />
              </div>
              
              <div className="mb-4">
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
                <Field type="password" name="confirmPassword" className="form-input" />
                <ErrorMessage name="confirmPassword" component="div" className="text-danger-600 text-sm mt-1" />
              </div>
              
              <div className="mb-6">
                <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <Field as="select" name="role" className="form-input">
                  <option value="">Select a role</option>
                  <option value="patient">Patient</option>
                  <option value="doctor">Doctor</option>
                  <option value="nurse">Nurse</option>
                  <option value="admin">Admin</option>
                </Field>
                <ErrorMessage name="role" component="div" className="text-danger-600 text-sm mt-1" />
              </div>
              
              <button type="submit" className="btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Registering...' : 'Register'}
              </button>
              
              <div className="mt-4 text-center text-sm">
                <p>Already have an account? <Link to="/login" className="text-primary-600 hover:text-primary-800">Login</Link></p>
              </div>
            </Form>
          )}
        </Formik>
      </div>
    </div>
  );
};

export default Register;