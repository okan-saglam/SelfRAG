import React, { useEffect, useState } from 'react';
import { documentService } from '../../services/documentService';
import { useNavigate } from 'react-router-dom';

const styles = {
  container: 'max-w-5xl mx-auto p-6',
  message: 'text-center text-gray-500 my-8',
  title: 'text-xl font-bold mb-4',
  pdfBox: 'w-full h-[80vh] border rounded shadow bg-white flex items-center justify-center',
  pdfFrame: 'w-full h-full',
  backButton: 'mt-6 px-4 py-2 rounded bg-primary-600 text-white hover:bg-primary-700 transition',
};

const ExploreDocumentPage: React.FC = () => {
  const [documents, setDocuments] = useState<{ filename: string }[]>([]);
  const [selectedPdf, setSelectedPdf] = useState<string | null>(null);
  const [pdfData, setPdfData] = useState<{ filename: string; content: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setError(null);
        const docs = await documentService.getDocuments();
        setDocuments(docs);
      } catch (e: any) {
        setError('Failed to fetch documents');
      }
    };
    fetchDocuments();
  }, []);

  useEffect(() => {
    if (!selectedPdf) return;
    setLoading(true);
    setError(null);
    setPdfData(null);
    documentService.getPdfBase64(selectedPdf)
      .then(setPdfData)
      .catch(() => setError('Failed to load PDF'))
      .finally(() => setLoading(false));
  }, [selectedPdf]);

  const handleAskQuestion = (text: string) => {
    // Query sayfasına yönlendir ve query parametresi olarak text'i gönder
    navigate('/query', { state: { prefill: text } });
  };

  return (
    <div className={styles.container}>
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Explore Documents</h1>
        <p className="text-gray-600 mt-1">Browse uploaded PDFs and view them directly.</p>
      </div>
      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded mb-4">{error}</div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* PDF List */}
        <div>
          <h2 className="text-lg font-semibold mb-2">PDF Files</h2>
          <ul className="divide-y divide-gray-200 border rounded-md bg-white">
            {documents.map((doc) => (
              <li key={doc.filename}>
                <button
                  className={`w-full text-left px-4 py-3 hover:bg-primary-50 focus:outline-none ${selectedPdf === doc.filename ? 'bg-primary-100 font-semibold' : ''}`}
                  onClick={() => setSelectedPdf(doc.filename)}
                >
                  {doc.filename}
                </button>
              </li>
            ))}
          </ul>
        </div>
        {/* PDF Viewer */}
        <div className="md:col-span-2">
          {error ? (
            <div className={styles.message}>Failed to load PDF.</div>
          ) : loading ? (
            <div className={styles.message}>Loading PDF...</div>
          ) : pdfData ? (
            <>
              <h1 className={styles.title}>{pdfData.filename}</h1>
              <div className={styles.pdfBox}>
                <iframe
                  title={pdfData.filename}
                  src={`data:application/pdf;base64,${pdfData.content}#toolbar=1&view=FitH&zoom=page-fit`}
                  className={styles.pdfFrame}
                  allowFullScreen
                />
              </div>
              <button className={styles.backButton} onClick={() => setSelectedPdf(null)}>
                Go Back
              </button>
            </>
          ) : (
            <div className={styles.message}>Select a PDF to view it.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExploreDocumentPage; 