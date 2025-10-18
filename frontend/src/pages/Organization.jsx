import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { organizationsAPI, namespacesAPI } from '../services/api';

const Organization = () => {
  const { id } = useParams();
  const [organization, setOrganization] = useState(null);
  const [namespaces, setNamespaces] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('namespaces');
  const [showCreateNamespace, setShowCreateNamespace] = useState(false);
  const [newNamespaceName, setNewNamespaceName] = useState('');
  const [newNamespaceDescription, setNewNamespaceDescription] = useState('');

  useEffect(() => {
    if (id) {
      fetchOrganizationData();
    }
  }, [id]);

  const fetchOrganizationData = async () => {
    try {
      setLoading(true);
      const [orgResponse, namespacesResponse, membersResponse] = await Promise.all([
        organizationsAPI.get(id),
        namespacesAPI.list(),
        organizationsAPI.getMembers(id)
      ]);
      
      setOrganization(orgResponse.data);
      setNamespaces(namespacesResponse.data.results || namespacesResponse.data);
      setMembers(membersResponse.data);
    } catch (err) {
      setError('Failed to fetch organization data');
      console.error('Error fetching organization data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNamespace = async (e) => {
    e.preventDefault();
    if (!newNamespaceName.trim()) return;

    try {
      const response = await namespacesAPI.create({
        name: newNamespaceName,
        description: newNamespaceDescription,
        organization: id
      });
      setNamespaces([...namespaces, response.data]);
      setNewNamespaceName('');
      setNewNamespaceDescription('');
      setShowCreateNamespace(false);
    } catch (err) {
      setError('Failed to create namespace');
      console.error('Error creating namespace:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
          <p className="mt-4 text-slate-400">Loading organization...</p>
        </div>
      </div>
    );
  }

  if (error || !organization) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="h-16 w-16 text-red-400 mx-auto mb-4">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Error</h3>
          <p className="text-slate-400 mb-6">{error || 'Organization not found'}</p>
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
                to="/dashboard"
                className="text-slate-400 hover:text-white transition-colors"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/50">
                  <span className="text-white font-bold text-lg">
                    {organization.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">{organization.name}</h1>
                  <p className="text-sm text-slate-400">Organization</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8 px-4">
        {/* Organization Header */}
        <div className="bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 rounded-2xl p-8 mb-8 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">{organization.name}</h2>
              <p className="text-slate-300">
                Owner: {organization.owner_full_name || organization.owner_email}
              </p>
              <p className="text-slate-400 text-sm mt-1">
                {organization.member_count} member{organization.member_count !== 1 ? 's' : ''}
              </p>
            </div>
            <div className="text-right">
              <p className="text-slate-400 text-sm">Created</p>
              <p className="text-white font-medium">
                {new Date(organization.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-xl">
          <div className="flex space-x-1 mb-8">
            <button
              onClick={() => setActiveTab('namespaces')}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                activeTab === 'namespaces'
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/25'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              Namespaces
            </button>
            <button
              onClick={() => setActiveTab('members')}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                activeTab === 'members'
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/25'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              Members
            </button>
            <button
              onClick={() => setActiveTab('invites')}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                activeTab === 'invites'
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/25'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              Invites
            </button>
          </div>

          {error && (
            <div className="mb-6 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Namespaces Tab */}
          {activeTab === 'namespaces' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-white">Namespaces</h3>
                <button
                  onClick={() => setShowCreateNamespace(true)}
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 shadow-lg shadow-indigo-500/25"
                >
                  <svg className="h-5 w-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Create Namespace
                </button>
              </div>

              {showCreateNamespace && (
                <div className="mb-8 bg-slate-700/50 border border-slate-600/50 p-6 rounded-xl">
                  <h4 className="text-lg font-semibold text-white mb-4">Create New Namespace</h4>
                  <form onSubmit={handleCreateNamespace} className="space-y-4">
                    <div>
                      <input
                        type="text"
                        value={newNamespaceName}
                        onChange={(e) => setNewNamespaceName(e.target.value)}
                        placeholder="Namespace name (globally unique)"
                        className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        required
                      />
                    </div>
                    <div>
                      <textarea
                        value={newNamespaceDescription}
                        onChange={(e) => setNewNamespaceDescription(e.target.value)}
                        placeholder="Description (optional)"
                        rows={3}
                        className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                    <div className="flex gap-4">
                      <button
                        type="submit"
                        className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                      >
                        Create
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setShowCreateNamespace(false);
                          setNewNamespaceName('');
                          setNewNamespaceDescription('');
                        }}
                        className="bg-slate-600 hover:bg-slate-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              )}

              {namespaces.length === 0 ? (
                <div className="text-center py-12">
                  <div className="mx-auto h-16 w-16 text-slate-400 mb-4">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">No namespaces yet</h3>
                  <p className="text-slate-400">Create your first namespace to start organizing your short URLs.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {namespaces.map((namespace) => (
                    <div key={namespace.id} className="bg-slate-700/30 border border-slate-600/50 rounded-xl p-6 hover:border-indigo-500/50 transition-all duration-300">
                      <div className="flex items-start gap-4">
                        <div className="h-12 w-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center shadow-lg shadow-purple-500/50">
                          <span className="text-white font-bold text-lg">
                            {namespace.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="flex-1">
                          <h4 className="text-lg font-semibold text-white mb-1">{namespace.name}</h4>
                          {namespace.description && (
                            <p className="text-sm text-slate-400 mb-2">{namespace.description}</p>
                          )}
                          <p className="text-xs text-slate-500">
                            {namespace.short_url_count || 0} short URL{(namespace.short_url_count || 0) !== 1 ? 's' : ''}
                          </p>
                        </div>
                      </div>
                      <div className="mt-6">
                        <Link
                          to={`/namespaces/${namespace.id}`}
                          className="w-full bg-gradient-to-r from-purple-600/20 to-pink-600/20 hover:from-purple-600/30 hover:to-pink-600/30 border border-purple-500/30 hover:border-purple-500/50 text-purple-400 hover:text-purple-300 text-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 block"
                        >
                          View Namespace
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Members Tab */}
          {activeTab === 'members' && (
            <div>
              <h3 className="text-xl font-semibold text-white mb-6">Members</h3>
              {members.length === 0 ? (
                <div className="text-center py-12">
                  <div className="mx-auto h-16 w-16 text-slate-400 mb-4">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">No members</h3>
                  <p className="text-slate-400">This organization has no members yet.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {members.map((member) => (
                    <div key={member.id} className="bg-slate-700/30 border border-slate-600/50 rounded-xl p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="h-12 w-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg shadow-indigo-500/50">
                            <span className="text-white font-bold text-lg">
                              {member.user_full_name?.charAt(0) || member.user_email?.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <div>
                            <h4 className="text-lg font-semibold text-white">
                              {member.user_full_name || member.user_email}
                            </h4>
                            <p className="text-sm text-slate-400">{member.user_email}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                            member.role === 'admin'
                              ? 'bg-red-500/10 border border-red-500/30 text-red-400'
                              : member.role === 'editor'
                              ? 'bg-yellow-500/10 border border-yellow-500/30 text-yellow-400'
                              : 'bg-blue-500/10 border border-blue-500/30 text-blue-400'
                          }`}>
                            {member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Invites Tab */}
          {activeTab === 'invites' && (
            <div>
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-white">Invitations</h3>
                <Link
                  to={`/organizations/${id}/invites`}
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 shadow-lg shadow-indigo-500/25"
                >
                  <svg className="h-5 w-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                  </svg>
                  Manage Invitations
                </Link>
              </div>
              
              <div className="text-center py-12">
                <div className="mx-auto h-16 w-16 text-slate-400 mb-4">
                  <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">Invite Management</h3>
                <p className="text-slate-400 mb-6">Send invitations to new members and manage pending invites.</p>
                <Link
                  to={`/organizations/${id}/invites`}
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg shadow-indigo-500/25"
                >
                  Go to Invite Management
                </Link>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Organization;
