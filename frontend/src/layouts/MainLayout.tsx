import React, { useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

// Icons
import { 
  HomeIcon, 
  DocumentTextIcon, 
  QuestionMarkCircleIcon, 
  ChartBarIcon, 
  UserIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';

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

// Navigation items
const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: HomeIcon },
  { name: 'Documents', path: '/documents', icon: DocumentTextIcon },
  { name: 'Query', path: '/query', icon: QuestionMarkCircleIcon },
  { name: 'Analytics', path: '/analytics', icon: ChartBarIcon },
  { name: 'Profile', path: '/profile', icon: UserIcon },
];

const MainLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Top navigation */}
      <div className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Logo />
          
          {/* Mobile menu button */}
          <button 
            type="button" 
            className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-900 hover:bg-gray-100 focus:outline-none"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
            ) : (
              <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
            )}
          </button>
          
          {/* Desktop navigation */}
          <div className="hidden md:flex md:items-center md:space-x-4">
            {user && (
              <div className="flex items-center">
                <span className="text-gray-700 mr-2">
                  {user.full_name || user.username}
                </span>
                <button
                  onClick={handleLogout}
                  className="flex items-center text-gray-600 hover:text-gray-900"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5 mr-1" />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-gray-200">
          <div className="container mx-auto px-4 py-3 space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  location.pathname === item.path
                    ? 'text-primary-700 bg-primary-50'
                    : 'text-gray-700 hover:text-primary-700 hover:bg-primary-50'
                }`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <div className="flex items-center">
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </div>
              </Link>
            ))}
            {user && (
              <button
                onClick={() => {
                  handleLogout();
                  setIsMobileMenuOpen(false);
                }}
                className="w-full text-left flex items-center px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-700 hover:bg-primary-50"
              >
                <ArrowRightOnRectangleIcon className="mr-3 h-5 w-5" />
                Logout
              </button>
            )}
          </div>
        </div>
      )}
      
      {/* Main content area */}
      <div className="flex flex-1">
        {/* Sidebar navigation - desktop */}
        <div className="hidden md:flex md:flex-shrink-0">
          <div className="w-64 bg-white shadow-md">
            <div className="h-full flex flex-col">
              <nav className="flex-1 p-4 space-y-1">
                {navItems.map((item) => (
                  <Link
                    key={item.name}
                    to={item.path}
                    className={`flex items-center px-3 py-3 rounded-md text-sm font-medium ${
                      location.pathname === item.path
                        ? 'text-primary-700 bg-primary-50'
                        : 'text-gray-700 hover:text-primary-700 hover:bg-primary-50'
                    }`}
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        </div>
        
        {/* Main content */}
        <div className="flex-1 overflow-auto p-6">
          <div className="container mx-auto">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainLayout;
