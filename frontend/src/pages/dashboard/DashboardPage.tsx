import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useDocumentStore } from '../../store/documentStore';

// Stats card component
interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: React.ReactNode;
}

const StatsCard: React.FC<StatsCardProps> = ({ title, value, description, icon }) => (
  <div className="bg-white overflow-hidden shadow rounded-lg">
    <div className="p-5">
      <div className="flex items-center">
        <div className="flex-shrink-0 bg-primary-100 rounded-md p-3">
          {icon}
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd>
              <div className="text-lg font-medium text-gray-900">{value}</div>
            </dd>
          </dl>
        </div>
      </div>
    </div>
    {description && (
      <div className="bg-gray-50 px-5 py-3">
        <div className="text-sm">
          <span className="text-gray-500">{description}</span>
        </div>
      </div>
    )}
  </div>
);

const DashboardPage: React.FC = () => {
  const { 
    fetchSystemStatus, 
    systemStatus, 
    isLoading, 
    error 
  } = useDocumentStore();
  
  useEffect(() => {
    fetchSystemStatus();
  }, [fetchSystemStatus]);
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading system status...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded mb-4">
        {error}
        <button 
          onClick={() => fetchSystemStatus()} 
          className="ml-2 underline"
        >
          Try again
        </button>
      </div>
    );
  }
  
  return (
    <div>
      <div className="mb-6">
        <h1>Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Overview of your document system
        </p>
      </div>
      
      {systemStatus && (
        <>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 mb-8">
            <StatsCard
              title="Documents"
              value={systemStatus.vectorstore.document_count}
              description={`${systemStatus.vectorstore.has_documents ? 'Index ready' : 'No documents indexed'}`}
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              }
            />
            
            <StatsCard
              title="PDF Files"
              value={systemStatus.data_directory.pdf_count}
              description="Available for upload"
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              }
            />
            
            <StatsCard
              title="System Status"
              value={systemStatus.status}
              description="All components are operational"
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            />
          </div>
          
          <div className="bg-white shadow rounded-lg p-6 mb-8">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Link
                to="/documents"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none"
              >
                Upload Documents
              </Link>
              <Link
                to="/query"
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
              >
                Ask Questions
              </Link>
            </div>
          </div>
          
          {systemStatus.data_directory.pdf_files.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Available PDF Files</h2>
              <div className="overflow-x-auto">
                <ul className="divide-y divide-gray-200">
                  {systemStatus.data_directory.pdf_files.map((file) => (
                    <li key={file} className="py-3 flex justify-between">
                      <span className="text-sm text-gray-700">{file}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default DashboardPage;
