import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { namespacesAPI, shortUrlsAPI, organizationsAPI } from '../services/api';

const Namespace = () => {
  const { id } = useParams();
  const [namespace, setNamespace] = useState(null);
  const [shortUrls, setShortUrls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newShortUrl, setNewShortUrl] = useState({
    original_url: '',
    short_code: '',
    title: '',
    description: '',
    expiry_date: ''
  });
  const [editingShortUrl, setEditingShortUrl] = useState(null);
  const [editShortUrl, setEditShortUrl] = useState({
    original_url: '',
    short_code: '',
    title: '',
    description: '',
    expiry_date: ''
  });
  const [userRole, setUserRole] = useState(null);

  useEffect(() => {
    if (id) {
      fetchNamespaceData();
    }
  }, [id]);

  // Helper functions for role-based UI visibility
  const isAdmin = userRole === 'admin';
  const isEditor = userRole === 'editor';
  const isViewer = userRole === 'viewer';
  const canCreateShortUrls = isAdmin || isEditor;
  const canEditShortUrls = isAdmin || isEditor;

  const fetchNamespaceData = async () => {
    try {
      setLoading(true);
      const [namespaceResponse, shortUrlsResponse] = await Promise.all([
        namespacesAPI.get(id),
        shortUrlsAPI.getByNamespace(id)
      ]);
      
      setNamespace(namespaceResponse.data);
      setShortUrls(shortUrlsResponse.data);
      
      // Get user role from the organization
      if (namespaceResponse.data.organization) {
        try {
          const orgResponse = await organizationsAPI.get(namespaceResponse.data.organization);
          setUserRole(orgResponse.data.current_user_role);
        } catch (orgErr) {
          console.log('Could not fetch organization data for role:', orgErr);
        }
      }
    } catch (err) {
      setError('Failed to fetch namespace data');
      console.error('Error fetching namespace data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateShortUrl = async (e) => {
    e.preventDefault();
    if (!newShortUrl.original_url.trim()) return;

    try {
      // Prepare data, removing empty strings
      const urlData = {
        namespace: id,
        original_url: newShortUrl.original_url.trim(),
        title: newShortUrl.title.trim() || undefined,
        description: newShortUrl.description.trim() || undefined,
        expiry_date: newShortUrl.expiry_date || undefined
      };

      // Only include short_code if it's not empty
      if (newShortUrl.short_code.trim()) {
        urlData.short_code = newShortUrl.short_code.trim();
      }

      const response = await shortUrlsAPI.create(urlData);
      setShortUrls([...shortUrls, response.data]);
      setNewShortUrl({
        original_url: '',
        short_code: '',
        title: '',
        description: '',
        expiry_date: ''
      });
      setShowCreateForm(false);
      setError(null); // Clear any previous errors
    } catch (err) {
      console.error('Error creating short URL:', err);
      if (err.response?.status === 403) {
        setError('You do not have permission to create short URLs. Only organization admins and editors can create short URLs.');
      } else if (err.response?.data) {
        // Show specific error messages from the backend
        const errorMessages = [];
        if (err.response.data.non_field_errors) {
          errorMessages.push(...err.response.data.non_field_errors);
        }
        Object.keys(err.response.data).forEach(key => {
          if (key !== 'non_field_errors' && Array.isArray(err.response.data[key])) {
            errorMessages.push(`${key}: ${err.response.data[key].join(', ')}`);
          }
        });
        setError(errorMessages.length > 0 ? errorMessages.join('; ') : 'Failed to create short URL');
      } else {
        setError('Failed to create short URL');
      }
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  const handleEditShortUrl = (shortUrl) => {
    setEditingShortUrl(shortUrl);
    setEditShortUrl({
      original_url: shortUrl.original_url,
      short_code: shortUrl.short_code || '',
      title: shortUrl.title || '',
      description: shortUrl.description || '',
      expiry_date: shortUrl.expiry_date ? shortUrl.expiry_date.split('T')[0] + 'T' + shortUrl.expiry_date.split('T')[1].split('.')[0] : ''
    });
  };

  const handleUpdateShortUrl = async (e) => {
    e.preventDefault();
    if (!editShortUrl.original_url.trim()) return;

    try {
      // Prepare data, removing empty strings
      const urlData = {
        namespace: id,
        original_url: editShortUrl.original_url.trim(),
        title: editShortUrl.title.trim() || undefined,
        description: editShortUrl.description.trim() || undefined,
        expiry_date: editShortUrl.expiry_date || undefined
      };

      // Only include short_code if it's not empty
      if (editShortUrl.short_code.trim()) {
        urlData.short_code = editShortUrl.short_code.trim();
      }

      const response = await shortUrlsAPI.update(editingShortUrl.id, urlData);
      setShortUrls(shortUrls.map(url => 
        url.id === editingShortUrl.id ? response.data : url
      ));
      setEditingShortUrl(null);
      setEditShortUrl({
        original_url: '',
        short_code: '',
        title: '',
        description: '',
        expiry_date: ''
      });
      setError(null);
    } catch (err) {
      console.error('Error updating short URL:', err);
      if (err.response?.status === 403) {
        setError('You do not have permission to update short URLs. Only organization admins and editors can manage short URLs.');
      } else if (err.response?.data) {
        const errorMessages = [];
        if (err.response.data.non_field_errors) {
          errorMessages.push(...err.response.data.non_field_errors);
        }
        Object.keys(err.response.data).forEach(key => {
          if (key !== 'non_field_errors' && Array.isArray(err.response.data[key])) {
            errorMessages.push(`${key}: ${err.response.data[key].join(', ')}`);
          }
        });
        setError(errorMessages.length > 0 ? errorMessages.join('; ') : 'Failed to update short URL');
      } else {
        setError('Failed to update short URL');
      }
    }
  };

  const handleDeleteShortUrl = async (shortUrlId) => {
    if (!window.confirm('Are you sure you want to delete this short URL? This action cannot be undone.')) {
      return;
    }

    try {
      await shortUrlsAPI.delete(shortUrlId);
      setShortUrls(shortUrls.filter(url => url.id !== shortUrlId));
      setError(null); // Clear any previous errors
    } catch (err) {
      if (err.response?.status === 403) {
        setError('You do not have permission to delete short URLs. Only organization admins and editors can manage short URLs.');
      } else {
        setError('Failed to delete short URL');
      }
      console.error('Error deleting short URL:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-slate-400">Loading namespace...</p>
        </div>
      </div>
    );
  }

  if (error || !namespace) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="h-16 w-16 text-red-400 mx-auto mb-4">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Error</h3>
          <p className="text-slate-400 mb-6">{error || 'Namespace not found'}</p>
          <Link
            to="/dashboard"
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
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
                to={`/organizations/${namespace.organization}`}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center shadow-lg shadow-purple-500/50">
                  <span className="text-white font-bold text-lg">
                    {namespace.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">{namespace.name}</h1>
                  <p className="text-sm text-slate-400">Namespace</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8 px-4">
        {/* Namespace Header */}
        <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-2xl p-8 mb-8 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">{namespace.name}</h2>
              {namespace.description && (
                <p className="text-slate-300 mb-2">{namespace.description}</p>
              )}
              <p className="text-slate-400 text-sm">
                Organization: {namespace.organization_name}
              </p>
            </div>
            <div className="text-right">
              <p className="text-slate-400 text-sm">Short URLs</p>
              <p className="text-white font-medium text-2xl">
                {shortUrls.length}
              </p>
            </div>
          </div>
        </div>

        {/* Short URLs Section */}
        <div className="bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-xl">
          <div className="flex justify-between items-center mb-8">
            <h3 className="text-2xl font-bold text-white">Short URLs</h3>
            {canCreateShortUrls && (
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg shadow-purple-500/25"
              >
                <svg className="h-5 w-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Create Short URL
              </button>
            )}
          </div>

          {error && (
            <div className="mb-6 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {showCreateForm && (
            <div className="mb-8 bg-slate-700/50 border border-slate-600/50 p-6 rounded-xl">
              <h4 className="text-lg font-semibold text-white mb-4">Create New Short URL</h4>
              <form onSubmit={handleCreateShortUrl} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Original URL *
                  </label>
                  <input
                    type="url"
                    value={newShortUrl.original_url}
                    onChange={(e) => setNewShortUrl({...newShortUrl, original_url: e.target.value})}
                    placeholder="https://example.com"
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Custom Short Code (optional)
                  </label>
                  <input
                    type="text"
                    value={newShortUrl.short_code}
                    onChange={(e) => setNewShortUrl({...newShortUrl, short_code: e.target.value})}
                    placeholder="Leave empty for auto-generation"
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Title (optional)
                  </label>
                  <input
                    type="text"
                    value={newShortUrl.title}
                    onChange={(e) => setNewShortUrl({...newShortUrl, title: e.target.value})}
                    placeholder="Short description"
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Description (optional)
                  </label>
                  <textarea
                    value={newShortUrl.description}
                    onChange={(e) => setNewShortUrl({...newShortUrl, description: e.target.value})}
                    placeholder="More details about this URL"
                    rows={3}
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Expiry Date (optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={newShortUrl.expiry_date}
                    onChange={(e) => setNewShortUrl({...newShortUrl, expiry_date: e.target.value})}
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
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
                      setShowCreateForm(false);
                      setNewShortUrl({
                        original_url: '',
                        short_code: '',
                        title: '',
                        description: '',
                        expiry_date: ''
                      });
                    }}
                    className="bg-slate-600 hover:bg-slate-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {editingShortUrl && (
            <div className="mb-8 bg-slate-700/50 border border-slate-600/50 p-6 rounded-xl">
              <h4 className="text-lg font-semibold text-white mb-4">Edit Short URL</h4>
              <form onSubmit={handleUpdateShortUrl} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Original URL *
                  </label>
                  <input
                    type="url"
                    value={editShortUrl.original_url}
                    onChange={(e) => setEditShortUrl({...editShortUrl, original_url: e.target.value})}
                    placeholder="https://example.com"
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Custom Short Code (optional)
                  </label>
                  <input
                    type="text"
                    value={editShortUrl.short_code}
                    onChange={(e) => setEditShortUrl({...editShortUrl, short_code: e.target.value})}
                    placeholder="Leave empty for auto-generation"
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Title (optional)
                  </label>
                  <input
                    type="text"
                    value={editShortUrl.title}
                    onChange={(e) => setEditShortUrl({...editShortUrl, title: e.target.value})}
                    placeholder="Short description"
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Description (optional)
                  </label>
                  <textarea
                    value={editShortUrl.description}
                    onChange={(e) => setEditShortUrl({...editShortUrl, description: e.target.value})}
                    placeholder="More details about this URL"
                    rows={3}
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Expiry Date (optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={editShortUrl.expiry_date}
                    onChange={(e) => setEditShortUrl({...editShortUrl, expiry_date: e.target.value})}
                    className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div className="flex gap-4">
                  <button
                    type="submit"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    Update
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setEditingShortUrl(null);
                      setEditShortUrl({
                        original_url: '',
                        short_code: '',
                        title: '',
                        description: '',
                        expiry_date: ''
                      });
                    }}
                    className="bg-slate-600 hover:bg-slate-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {shortUrls.length === 0 ? (
            <div className="text-center py-12">
              <div className="mx-auto h-16 w-16 text-slate-400 mb-4">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">No short URLs yet</h3>
              <p className="text-slate-400">Create your first short URL to get started.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {shortUrls.map((shortUrl) => (
                <div key={shortUrl.id} className="bg-slate-700/30 border border-slate-600/50 rounded-xl p-6 hover:border-purple-500/50 transition-all duration-300">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-lg font-semibold text-white">
                          {shortUrl.title || 'Untitled'}
                        </h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          shortUrl.is_active
                            ? 'bg-green-500/10 border border-green-500/30 text-green-400'
                            : 'bg-red-500/10 border border-red-500/30 text-red-400'
                        }`}>
                          {shortUrl.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <p className="text-slate-400 text-sm mb-2 break-all">
                        {shortUrl.original_url}
                      </p>
                      {shortUrl.description && (
                        <p className="text-slate-500 text-sm mb-3">{shortUrl.description}</p>
                      )}
                      <div className="flex items-center gap-4 text-sm text-slate-500">
                        <span>Created: {new Date(shortUrl.created_at).toLocaleDateString()}</span>
                        <span>•</span>
                        <span>{shortUrl.click_count} clicks</span>
                        <span>•</span>
                        <span>By: {shortUrl.created_by_email}</span>
                        {shortUrl.expiry_date && (
                          <>
                            <span>•</span>
                            <span>Expires: {new Date(shortUrl.expiry_date).toLocaleDateString()}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="ml-6 flex flex-col gap-2">
                      <div className="bg-slate-800/50 border border-slate-600/50 rounded-lg p-3 min-w-[200px]">
                        <p className="text-xs text-slate-400 mb-1">Short URL</p>
                        <p className="text-purple-400 font-mono text-sm break-all">
                          {shortUrl.full_short_url}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => copyToClipboard(shortUrl.full_short_url)}
                          className="bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 hover:border-purple-500/50 text-purple-400 hover:text-purple-300 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex-1"
                        >
                          <svg className="h-4 w-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          Copy
                        </button>
                        {canEditShortUrls && (
                          <>
                            <button
                              onClick={() => handleEditShortUrl(shortUrl)}
                              className="bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 hover:border-blue-500/50 text-blue-400 hover:text-blue-300 p-2 rounded-lg transition-all duration-200"
                              title="Edit short URL"
                            >
                              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                              </svg>
                            </button>
                            <button
                              onClick={() => handleDeleteShortUrl(shortUrl.id)}
                              className="bg-red-600/20 hover:bg-red-600/30 border border-red-500/30 hover:border-red-500/50 text-red-400 hover:text-red-300 p-2 rounded-lg transition-all duration-200"
                              title="Delete short URL"
                            >
                              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </>
                        )}
                      </div>
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

export default Namespace;
