import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { organizationsAPI } from '../../services/api';

const InviteAcceptPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [inviteData, setInviteData] = useState(null);
  
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      setError('Invalid invitation link. No token provided.');
      return;
    }
  }, [token]);

  const handleAcceptInvite = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      
      const response = await organizationsAPI.acceptInvite({ token });
      
      setSuccess(true);
      setInviteData(response.data);
      
      // Redirect to dashboard after 3 seconds
      setTimeout(() => {
        navigate('/dashboard');
      }, 3000);
      
    } catch (err) {
      console.error('Error accepting invite:', err);
      setError(
        err.response?.data?.detail || 
        err.response?.data?.token?.[0] || 
        'Failed to accept invitation. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  if (success && inviteData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-xl">
            <div className="text-center">
              <div className="mx-auto h-16 w-16 bg-green-500/20 rounded-full flex items-center justify-center mb-6">
                <svg className="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              
              <h1 className="text-2xl font-bold text-white mb-4">Welcome to the Team!</h1>
              <p className="text-slate-300 mb-6">
                You've successfully joined <span className="font-semibold text-indigo-400">
                  {inviteData.membership?.organization?.name || 'the organization'}
                </span> as a <span className="font-semibold text-yellow-400">
                  {inviteData.membership?.role || 'member'}
                </span>.
              </p>
              
              <div className="bg-slate-700/30 border border-slate-600/50 rounded-lg p-4 mb-6">
                <p className="text-sm text-slate-400">
                  You'll be redirected to your dashboard in a few seconds...
                </p>
              </div>
              
              <Link
                to="/dashboard"
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg shadow-indigo-500/25 block"
              >
                Go to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-xl">
          <div className="text-center">
            <div className="mx-auto h-16 w-16 bg-indigo-500/20 rounded-full flex items-center justify-center mb-6">
              <svg className="h-8 w-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
            
            <h1 className="text-2xl font-bold text-white mb-4">Organization Invitation</h1>
            <p className="text-slate-300 mb-8">
              You've been invited to join an organization on LinkNest. Click the button below to accept the invitation.
            </p>
            
            {error && (
              <div className="mb-6 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
            
            <button
              onClick={handleAcceptInvite}
              disabled={loading || !token}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg shadow-indigo-500/25"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Accepting...
                </div>
              ) : (
                'Accept Invitation'
              )}
            </button>
            
            <div className="mt-6 text-center">
              <Link
                to="/dashboard"
                className="text-slate-400 hover:text-white transition-colors text-sm"
              >
                Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InviteAcceptPage;
