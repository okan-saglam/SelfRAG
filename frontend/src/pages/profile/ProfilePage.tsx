import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuthStore } from '../../store/authStore';
import { authService } from '../../services/authService';
import type { UserUpdate } from '../../types/api';

const ProfilePage: React.FC = () => {
  const { user, loadUser } = useAuthStore();
  const [updateSuccess, setUpdateSuccess] = useState(false);
  const [updateError, setUpdateError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { 
    register, 
    handleSubmit, 
    formState: { errors } 
  } = useForm<UserUpdate>({
    defaultValues: {
      email: user?.email,
      full_name: user?.full_name || '',
    }
  });
  
  const onSubmit = async (data: UserUpdate) => {
    try {
      setIsSubmitting(true);
      setUpdateSuccess(false);
      setUpdateError(null);
      
      await authService.updateUser(data);
      await loadUser(); // Refresh user data
      
      setUpdateSuccess(true);
    } catch (error: any) {
      setUpdateError(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  if (!user) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading profile...</div>
      </div>
    );
  }
  
  return (
    <div>
      <div className="mb-6">
        <h1>Your Profile</h1>
        <p className="text-gray-600 mt-1">
          View and update your account information
        </p>
      </div>
      
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          {updateSuccess && (
            <div className="bg-green-50 text-green-800 p-4 rounded mb-6">
              Profile updated successfully!
            </div>
          )}
          
          {updateError && (
            <div className="bg-red-50 text-red-600 p-4 rounded mb-6">
              {updateError}
            </div>
          )}
          
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900">Account Information</h3>
            <div className="mt-4 grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <span className="block text-sm font-medium text-gray-500">Username</span>
                <span className="mt-1 block text-sm text-gray-900">{user.username}</span>
              </div>
              <div>
                <span className="block text-sm font-medium text-gray-500">Account Created</span>
                <span className="mt-1 block text-sm text-gray-900">
                  {new Date(user.created_at).toLocaleString()}
                </span>
              </div>
              {user.last_login && (
                <div>
                  <span className="block text-sm font-medium text-gray-500">Last Login</span>
                  <span className="mt-1 block text-sm text-gray-900">
                    {new Date(user.last_login).toLocaleString()}
                  </span>
                </div>
              )}
              <div>
                <span className="block text-sm font-medium text-gray-500">Account Type</span>
                <span className="mt-1 block text-sm text-gray-900">
                  {user.is_admin ? 'Administrator' : 'Standard User'}
                </span>
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-200 pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Update Profile</h3>
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label htmlFor="email" className="label">Email Address</label>
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
                <div>
                  <label htmlFor="full_name" className="label">Full Name</label>
                  <input
                    id="full_name"
                    type="text"
                    className="input"
                    {...register('full_name')}
                  />
                </div>
              </div>
              
              <div className="mt-6 flex justify-end">
                <button 
                  type="submit" 
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
