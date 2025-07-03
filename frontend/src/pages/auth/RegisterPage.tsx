import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuthStore } from '../../store/authStore';

type RegisterFormData = {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  fullName?: string;
};

const RegisterPage: React.FC = () => {
  const { register: registerUser, error, clearError } = useAuthStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { 
    register, 
    handleSubmit, 
    watch,
    formState: { errors } 
  } = useForm<RegisterFormData>();
  
  const onSubmit = async (data: RegisterFormData) => {
    try {
      setIsSubmitting(true);
      clearError();
      await registerUser(data.username, data.email, data.password, data.fullName);
    } catch (error) {
      console.error('Registration error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="card">
      <h2 className="text-center text-2xl mb-6">Create an Account</h2>
      
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="mb-4">
          <label htmlFor="username" className="label">Username</label>
          <input
            id="username"
            type="text"
            className={`input ${errors.username ? 'border-red-500' : ''}`}
            {...register('username', { 
              required: 'Username is required',
              minLength: { value: 3, message: 'Username must be at least 3 characters' }
            })}
          />
          {errors.username && (
            <p className="text-red-500 text-sm mt-1">{errors.username.message}</p>
          )}
        </div>
        
        <div className="mb-4">
          <label htmlFor="email" className="label">Email</label>
          <input
            id="email"
            type="email"
            className={`input ${errors.email ? 'border-red-500' : ''}`}
            {...register('email', { 
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address'
              }
            })}
          />
          {errors.email && (
            <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
          )}
        </div>
        
        <div className="mb-4">
          <label htmlFor="fullName" className="label">Full Name (Optional)</label>
          <input
            id="fullName"
            type="text"
            className="input"
            {...register('fullName')}
          />
        </div>
        
        <div className="mb-4">
          <label htmlFor="password" className="label">Password</label>
          <input
            id="password"
            type="password"
            className={`input ${errors.password ? 'border-red-500' : ''}`}
            {...register('password', { 
              required: 'Password is required',
              minLength: { value: 8, message: 'Password must be at least 8 characters' }
            })}
          />
          {errors.password && (
            <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>
          )}
        </div>
        
        <div className="mb-6">
          <label htmlFor="confirmPassword" className="label">Confirm Password</label>
          <input
            id="confirmPassword"
            type="password"
            className={`input ${errors.confirmPassword ? 'border-red-500' : ''}`}
            {...register('confirmPassword', { 
              required: 'Please confirm your password',
              validate: value => value === watch('password') || 'Passwords do not match'
            })}
          />
          {errors.confirmPassword && (
            <p className="text-red-500 text-sm mt-1">{errors.confirmPassword.message}</p>
          )}
        </div>
        
        <button 
          type="submit" 
          className="btn-primary w-full"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating account...' : 'Create Account'}
        </button>
      </form>
      
      <div className="mt-4 text-center">
        <p className="text-gray-600">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-600 hover:text-primary-800">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
