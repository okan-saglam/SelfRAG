import React, { useEffect, useState } from 'react';
import { documentService } from '../../services/documentService';
import { useAuthStore } from '../../store/authStore';
import { useNavigate } from 'react-router-dom';

const AdminRequestsPage: React.FC = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [requests, setRequests] = useState<{ username: string; requested_at: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionStatus, setActionStatus] = useState<{ [username: string]: string }>({});

  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/dashboard');
      return;
    }
    const fetchRequests = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await documentService.getAdminRequests();
        setRequests(data);
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to fetch requests.');
      } finally {
        setLoading(false);
      }
    };
    fetchRequests();
  }, [user, navigate]);

  const handleApprove = async (username: string) => {
    setActionStatus((prev) => ({ ...prev, [username]: 'loading' }));
    try {
      await documentService.approveAdmin(username);
      setActionStatus((prev) => ({ ...prev, [username]: 'success' }));
      setRequests((prev) => prev.filter((req) => req.username !== username));
    } catch (e: any) {
      setActionStatus((prev) => ({ ...prev, [username]: 'error' }));
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4">Admin Access Requests</h1>
      {loading ? (
        <div>Yükleniyor...</div>
      ) : error ? (
        <div className="text-red-600">{error}</div>
      ) : requests.length === 0 ? (
        <div className="text-gray-600">No pending admin access requests.</div>
      ) : (
        <ul className="divide-y divide-gray-200 bg-white rounded shadow">
          {requests.map((req) => (
            <li key={req.username} className="flex items-center justify-between px-4 py-3">
              <div>
                <span className="font-medium">{req.username}</span>
                <span className="ml-2 text-xs text-gray-500">{new Date(req.requested_at).toLocaleString()}</span>
              </div>
              <div>
                <button
                  className="inline-flex items-center justify-center px-5 py-2.5 border border-transparent text-sm font-semibold rounded-lg shadow-sm transition bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={() => handleApprove(req.username)}
                  disabled={actionStatus[req.username] === 'loading'}
                >
                  {actionStatus[req.username] === 'loading' ? 'Approving...' : 'Approve'}
                </button>
                {actionStatus[req.username] === 'success' && (
                  <span className="ml-2 text-green-600">Approved</span>
                )}
                {actionStatus[req.username] === 'error' && (
                  <span className="ml-2 text-red-600">Error!</span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AdminRequestsPage; 