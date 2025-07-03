import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuthStore } from '../../store/authStore';

type LoginFormData = {
  username: string;
  password: string;
};

const LoginPage: React.FC = () => {
  const { login, error, clearError } = useAuthStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { 
    register, 
    handleSubmit, 
    formState: { errors } 
  } = useForm<LoginFormData>();
  
  const onSubmit = async (data: LoginFormData) => {
    try {
      setIsSubmitting(true);
      clearError();
      await login(data.username, data.password);
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="card">
      <h2 className="text-center text-2xl mb-6">Sign In</h2>
      
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
            {...register('username', { required: 'Username is required' })}
          />
          {errors.username && (
            <p className="text-red-500 text-sm mt-1">{errors.username.message}</p>
          )}
        </div>
        
        <div className="mb-6">
          <label htmlFor="password" className="label">Password</label>
          <input
            id="password"
            type="password"
            className={`input ${errors.password ? 'border-red-500' : ''}`}
            {...register('password', { required: 'Password is required' })}
          />
          {errors.password && (
            <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>
          )}
        </div>
        
        <button 
          type="submit" 
          className="btn-primary w-full"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
      
      <div className="mt-4 text-center">
        <p className="text-gray-600">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary-600 hover:text-primary-800">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
