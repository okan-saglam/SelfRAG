import React, { useEffect, useState, useRef } from 'react';
import { useDocumentStore } from '../../store/documentStore';
import { useAuthStore } from '../../store/authStore';
import { documentService } from '../../services/documentService';

// File Upload Component
const DocumentUpload: React.FC = () => {
  const { uploadDocuments, isLoading } = useDocumentStore();
  const { user } = useAuthStore();
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isAdmin = user?.is_admin;
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
    }
  };
  
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };
  
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(Array.from(e.dataTransfer.files));
    }
  };
  
  const handleUpload = async () => {
    if (files.length > 0) {
      await uploadDocuments(files);
      setFiles([]);
    }
  };
  
  return (
    <div className="mb-6">
      <div 
        className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center ${
          isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-500'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        
        <p className="mb-2 text-sm text-gray-700">
          <span className="font-semibold">Click to upload</span> or drag and drop
        </p>
        <p className="text-xs text-gray-500">
          PDF documents only
        </p>
        
        <input
          type="file"
          multiple
          accept=".pdf"
          className="hidden"
          ref={fileInputRef}
          onChange={handleFileChange}
          disabled={!isAdmin}
        />
        
        <button
          type="button"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none mt-2"
          onClick={() => isAdmin && fileInputRef.current?.click()}
          disabled={!isAdmin}
        >
          Select Files
        </button>
      </div>
      
      {files.length > 0 && (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Selected Files</h3>
          <ul className="divide-y divide-gray-200 border rounded-md">
            {files.map((file, index) => (
              <li key={index} className="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                <div className="w-0 flex-1 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="flex-shrink-0 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <span className="ml-2 flex-1 w-0 truncate">
                    {file.name}
                  </span>
                </div>
                <div className="ml-4 flex-shrink-0">
                  <span className="font-medium text-gray-500">
                    {(file.size / 1024).toFixed(2)} KB
                  </span>
                </div>
              </li>
            ))}
          </ul>
          
          <div className="mt-4 flex justify-end">
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none mr-3"
              onClick={() => setFiles([])}
              disabled={!isAdmin}
            >
              Cancel
            </button>
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none"
              onClick={handleUpload}
              disabled={isLoading || !isAdmin}
            >
              {isLoading ? 'Uploading...' : 'Upload Files'}
            </button>
          </div>
        </div>
      )}
      {!isAdmin && (
        <div className="mt-4">
          <RequestAdminButton />
        </div>
      )}
    </div>
  );
};

// Admin olma isteği butonu
const RequestAdminButton: React.FC = () => {
  const [status, setStatus] = useState<'idle'|'loading'|'success'|'error'>("idle");
  const [message, setMessage] = useState<string>("");
  const handleRequest = async () => {
    setStatus("loading");
    setMessage("");
    try {
      await documentService.requestAdmin();
      setStatus("success");
      setMessage("Your admin request has been received. Your account will be updated once approved by an admin.");
    } catch (e: any) {
      setStatus("error");
      setMessage(e?.response?.data?.detail || "An error occurred during the request.");
    }
  };
  return (
    <div>
      <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none" onClick={handleRequest} disabled={status==='loading'}>
        {status==='loading' ? 'Sending...' : 'Request admin access'}
      </button>
      {message && <div className={`mt-2 text-sm ${status==='success' ? 'text-green-600' : 'text-red-600'}`}>{message}</div>}
    </div>
  );
};

// Document List Component
const DocumentList: React.FC = () => {
  const { documents, fetchDocuments, deleteDocument, isLoading, error } = useDocumentStore();
  const { user } = useAuthStore();
  const isAdmin = user?.is_admin;
  
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);
  
  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };
  
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };
  
  if (isLoading && documents.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading documents...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded mb-4">
        {error}
        <button 
          onClick={() => fetchDocuments()} 
          className="ml-2 underline"
        >
          Try again
        </button>
      </div>
    );
  }
  
  if (documents.length === 0) {
    return (
      <div className="bg-gray-50 p-8 text-center rounded-lg border border-gray-200">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="text-lg font-medium text-gray-900 mb-1">No documents found</h3>
        <p className="text-gray-500">Upload some documents to get started</p>
      </div>
    );
  }
  
  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200">
        {documents.map((doc) => (
          <li key={doc.filename}>
            <div className="px-4 py-4 flex items-center sm:px-6">
              <div className="min-w-0 flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <div className="flex text-sm">
                    <p className="font-medium text-primary-600 truncate">{doc.filename}</p>
                  </div>
                  <div className="mt-2 flex">
                    <div className="flex items-center text-sm text-gray-500">
                      <svg xmlns="http://www.w3.org/2000/svg" className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p>
                        Uploaded on <time dateTime={new Date(doc.uploaded_at * 1000).toISOString()}>{formatDate(doc.uploaded_at)}</time>
                      </p>
                    </div>
                  </div>
                </div>
                <div className="mt-4 flex-shrink-0 sm:mt-0 sm:ml-5">
                  <div className="flex overflow-hidden">
                    <div className="text-sm text-gray-500 mr-6">
                      {formatFileSize(doc.size)}
                    </div>
                    <button
                      onClick={() => isAdmin && deleteDocument(doc.filename)}
                      disabled={isLoading || !isAdmin}
                      className={`text-red-600 hover:text-red-900 ${!isAdmin ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

const DocumentsPage: React.FC = () => {
  const { error, clearError } = useDocumentStore();
  
  useEffect(() => {
    // Clear any errors when component mounts
    clearError();
  }, [clearError]);
  
  return (
    <div>
      <div className="mb-6">
        <h1>Documents</h1>
        <p className="text-gray-600 mt-1">
          Upload, manage, and delete your documents
        </p>
      </div>
      
      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded mb-4">
          {error}
          <button 
            onClick={clearError} 
            className="ml-2 underline"
          >
            Dismiss
          </button>
        </div>
      )}
      
      <DocumentUpload />
      
      <h2 className="text-xl font-semibold mb-4">Your Documents</h2>
      <DocumentList />
    </div>
  );
};

export default DocumentsPage;
