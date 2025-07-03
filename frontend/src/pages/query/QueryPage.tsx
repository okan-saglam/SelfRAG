import React, { useState } from 'react';
import { useDocumentStore } from '../../store/documentStore';

const QueryPage: React.FC = () => {
  const { 
    queryDocuments, 
    queryResult, 
    isQuerying, 
    clearQueryResult, 
    error, 
    clearError 
  } = useDocumentStore();
  
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [useSelfRAG, setUseSelfRAG] = useState(true);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    clearError();
    await queryDocuments(query, topK, useSelfRAG);
  };
  
  const handleReset = () => {
    setQuery('');
    clearQueryResult();
    clearError();
  };
  
  // Format date for human readability
  const formatTime = (ms: number): string => {
    if (ms < 1000) return `${ms} ms`;
    return `${(ms / 1000).toFixed(2)} seconds`;
  };
  
  return (
    <div>
      <div className="mb-6">
        <h1>Ask Documents</h1>
        <p className="text-gray-600 mt-1">
          Ask questions about your uploaded documents
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
      
      <div className="bg-white shadow-sm rounded-lg p-6 mb-8">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="query" className="label">Your Question</label>
            <textarea
              id="query"
              className="input h-24 resize-none"
              placeholder="What would you like to know about your documents?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label htmlFor="topK" className="label">Number of chunks to retrieve</label>
              <input
                id="topK"
                type="number"
                min="1"
                max="20"
                className="input"
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value))}
              />
            </div>
            
            <div className="flex items-center">
              <label className="flex items-center cursor-pointer">
                <div className="relative">
                  <input
                    type="checkbox"
                    className="sr-only"
                    checked={useSelfRAG}
                    onChange={(e) => setUseSelfRAG(e.target.checked)}
                  />
                  <div className={`block w-14 h-8 rounded-full ${useSelfRAG ? 'bg-primary-600' : 'bg-gray-300'}`}></div>
                  <div className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition ${useSelfRAG ? 'transform translate-x-6' : ''}`}></div>
                </div>
                <div className="ml-3 text-gray-700 font-medium">
                  Use Self-RAG
                </div>
              </label>
            </div>
          </div>
          
          <div className="flex justify-end">
            <button
              type="button"
              onClick={handleReset}
              className="btn-outline mr-3"
            >
              Reset
            </button>
            
            <button
              type="submit"
              className="btn-primary"
              disabled={isQuerying || !query.trim()}
            >
              {isQuerying ? 'Processing...' : 'Ask Question'}
            </button>
          </div>
        </form>
      </div>
      
      {queryResult && (
        <div className="bg-white shadow-sm rounded-lg p-6">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-xl font-semibold">Answer</h2>
            <div className="text-sm text-gray-500">
              Processed in {formatTime(queryResult.processing_time)}
            </div>
          </div>
          
          <div className="prose max-w-none mb-8">
            <p className="text-gray-800 whitespace-pre-line">
              {queryResult.answer}
            </p>
          </div>
          
          {queryResult.self_rag_info && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-2">Self-RAG Information</h3>
              <div className="bg-gray-50 p-4 rounded-md">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <span className="block text-sm text-gray-500">Retrieval Confidence</span>
                    <span className="text-lg font-medium">{(queryResult.self_rag_info.retrieval_confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="block text-sm text-gray-500">Generation Confidence</span>
                    <span className="text-lg font-medium">{(queryResult.self_rag_info.generation_confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="block text-sm text-gray-500">Final Score</span>
                    <span className="text-lg font-medium">{(queryResult.self_rag_info.final_score * 100).toFixed(1)}%</span>
                  </div>
                </div>
                
                {queryResult.self_rag_info.reflection_notes.length > 0 && (
                  <div>
                    <h4 className="text-md font-medium mb-2">Reflection Notes</h4>
                    <ul className="list-disc pl-5 space-y-1">
                      {queryResult.self_rag_info.reflection_notes.map((note, index) => (
                        <li key={index} className="text-sm text-gray-600">{note}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
          
          <div>
            <h3 className="text-lg font-semibold mb-3">Source Chunks</h3>
            <div className="space-y-4">
              {queryResult.chunks.map((chunk, index) => (
                <div key={index} className="border border-gray-200 rounded-md p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="text-sm font-medium text-primary-600">
                      {chunk.source_file} {chunk.page > 0 ? `(Page ${chunk.page})` : ''}
                    </div>
                    <div className="text-xs text-gray-500">
                      Relevance: {(chunk.score * 100).toFixed(1)}%
                    </div>
                  </div>
                  <p className="text-sm text-gray-700 whitespace-pre-line">
                    {chunk.text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryPage;
