import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

// Logo component
const Logo: React.FC = () => (
  <div className="flex items-center space-x-2">
    <div className="bg-primary-600 text-white p-2 rounded-md">
      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
      </svg>
    </div>
    <span className="text-xl font-bold text-gray-800">AskMyDocs</span>
  </div>
);

const AuthLayout: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  // Redirect to dashboard if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);
  
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center">
      <div className="py-6 px-4 sm:px-6 lg:px-8 mx-auto">
        <div className="flex justify-center mb-8">
          <Logo />
        </div>
        <div className="max-w-md w-full mx-auto">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
