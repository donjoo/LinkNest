import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { organizationsAPI } from '../../services/api';

const InviteManagementPage = () => {
  const { id } = useParams();
  const [organization, setOrganization] = useState(null);
  const [invites, setInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newInvite, setNewInvite] = useState({
    email: '',
    role: 'viewer'
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (id) {
      fetchData();
    }
  }, [id]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [orgResponse, invitesResponse] = await Promise.all([
        organizationsAPI.get(id),
        organizationsAPI.getInvites(id)
      ]);
      
      setOrganization(orgResponse.data);
      setInvites(invitesResponse.data);
    } catch (err) {
      setError('Failed to fetch organization data');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInvite = async (e) => {
    e.preventDefault();
    if (!newInvite.email.trim()) return;

    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);
      
      const response = await organizationsAPI.createInvite(id, newInvite);
      
      // Debug logging
      console.log('Invite creation response:', response.data);
      console.log('Email sent status:', response.data.email_sent);
      
      // Check if email was sent successfully
      if (response.data.email_sent === false) {
        setError(
          `Invitation created but email failed to send: ${response.data.email_error || 'Unknown error'}. ` +
          'The invitation is still valid and can be shared manually.'
        );
      } else {
        setError(null); // Clear any previous errors
        setSuccess(`✅ Invitation sent successfully to ${newInvite.email}!`);
        // Show success message
        console.log('✅ Invite created and email sent successfully!');
      }
      
      setInvites([response.data, ...invites]);
      setNewInvite({ email: '', role: 'viewer' });
      setShowCreateForm(false);
    } catch (err) {
      console.error('Error creating invite:', err);
      
      // Handle different types of error responses
      let errorMessage = 'Failed to create invitation. Please try again.';
      
      if (err.response?.data) {
        if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response.data.non_field_errors && err.response.data.non_field_errors.length > 0) {
          errorMessage = err.response.data.non_field_errors[0];
        } else if (err.response.data.email && err.response.data.email.length > 0) {
          errorMessage = err.response.data.email[0];
        }
      }
      
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRevokeInvite = async (inviteId) => {
    if (!window.confirm('Are you sure you want to revoke this invitation?')) {
      return;
    }

    try {
      await organizationsAPI.revokeInvite(id, { invite_id: inviteId });
      setInvites(invites.filter(invite => invite.id !== inviteId));
    } catch (err) {
      console.error('Error revoking invite:', err);
      setError('Failed to revoke invitation. Please try again.');
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin':
        return 'bg-red-500/10 border-red-500/30 text-red-400';
      case 'editor':
        return 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400';
      case 'viewer':
        return 'bg-blue-500/10 border-blue-500/30 text-blue-400';
      default:
        return 'bg-slate-500/10 border-slate-500/30 text-slate-400';
    }
  };

  const getStatusColor = (invite) => {
    if (invite.accepted) {
      return 'bg-green-500/10 border-green-500/30 text-green-400';
    } else if (invite.is_expired) {
      return 'bg-red-500/10 border-red-500/30 text-red-400';
    } else if (invite.used) {
      return 'bg-orange-500/10 border-orange-500/30 text-orange-400';
    } else {
      return 'bg-blue-500/10 border-blue-500/30 text-blue-400';
    }
  };

  const getStatusText = (invite) => {
    if (invite.accepted) {
      return 'Accepted';
    } else if (invite.is_expired) {
      return 'Expired';
    } else if (invite.used) {
      return 'Used';
    } else {
      return 'Pending';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-slate-400">Loading invitations...</p>
        </div>
      </div>
    );
  }

  if (error && !organization) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="h-16 w-16 text-red-400 mx-auto mb-4">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Error</h3>
          <p className="text-slate-400 mb-6">{error}</p>
          <Link
            to="/dashboard"
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="bg-slate-800/50 backdrop-blur-xl border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <Link
                to={`/organizations/${id}`}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/50">
                  <span className="text-white font-bold text-lg">
                    {organization?.name?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">Invite Management</h1>
                  <p className="text-sm text-slate-400">{organization?.name}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8 px-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 rounded-2xl p-8 mb-8 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Invite Management</h2>
              <p className="text-slate-300">
                Manage invitations for {organization?.name}
              </p>
            </div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg shadow-indigo-500/25"
            >
              <svg className="h-5 w-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Send Invitation
            </button>
          </div>
        </div>

        {/* Create Invite Form */}
        {showCreateForm && (
          <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 mb-8 shadow-xl">
            <h3 className="text-xl font-semibold text-white mb-6">Send New Invitation</h3>
            
            {error && (
              <div className="mb-6 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
            
            {success && (
              <div className="mb-6 bg-green-500/10 border border-green-500/30 text-green-400 px-4 py-3 rounded-lg">
                {success}
              </div>
            )}
            
            <form onSubmit={handleCreateInvite} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  value={newInvite.email}
                  onChange={(e) => setNewInvite({ ...newInvite, email: e.target.value })}
                  placeholder="Enter email address"
                  className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Role
                </label>
                <select
                  value={newInvite.role}
                  onChange={(e) => setNewInvite({ ...newInvite, role: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="viewer">Viewer - Can view content</option>
                  <option value="editor">Editor - Can create and edit content</option>
                  <option value="admin">Admin - Full access</option>
                </select>
              </div>
              
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={submitting}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  {submitting ? 'Sending...' : 'Send Invitation'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false);
                    setNewInvite({ email: '', role: 'viewer' });
                    setError(null);
                  }}
                  className="bg-slate-600 hover:bg-slate-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Invites List */}
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-xl">
          <h3 className="text-xl font-semibold text-white mb-6">Invitations</h3>
          
          {invites.length === 0 ? (
            <div className="text-center py-12">
              <div className="mx-auto h-16 w-16 text-slate-400 mb-4">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">No invitations yet</h3>
              <p className="text-slate-400">Send your first invitation to get started.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {invites.map((invite) => (
                <div key={invite.id} className="bg-slate-700/30 border border-slate-600/50 rounded-xl p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-indigo-500/50">
                        <span className="text-white font-bold text-lg">
                          {invite.email.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h4 className="text-lg font-semibold text-white">{invite.email}</h4>
                        <p className="text-sm text-slate-400">
                          Invited by {invite.invited_by_name || invite.invited_by_email}
                        </p>
                        <p className="text-xs text-slate-500">
                          {new Date(invite.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getRoleColor(invite.role)}`}>
                        {invite.role.charAt(0).toUpperCase() + invite.role.slice(1)}
                      </span>
                      
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(invite)}`}>
                        {getStatusText(invite)}
                      </span>
                      
                      {!invite.accepted && !invite.used && !invite.is_expired && (
                        <button
                          onClick={() => handleRevokeInvite(invite.id)}
                          className="bg-red-600/20 hover:bg-red-600/30 border border-red-500/30 hover:border-red-500/50 text-red-400 hover:text-red-300 px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200"
                        >
                          Revoke
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default InviteManagementPage;
