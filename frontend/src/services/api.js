import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api'}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API functions
export const authAPI = {
  register: (userData) => api.post('/auth/register/', userData),
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh: refreshToken }),
  getProfile: () => api.get('/auth/profile/'),
  refreshToken: (refreshToken) => api.post('/auth/token/refresh/', { refresh: refreshToken }),
  
  // OTP functions
  sendOTP: (email) => api.post('/auth/send-otp/', { email }),
  verifyOTP: (email, code) => api.post('/auth/verify-otp/', { email, code }),
  resendOTP: (email) => api.post('/auth/resend-otp/', { email }),
  getOTPStatus: (email) => api.get(`/auth/otp-status/?email=${email}`),
};

// Organizations API functions
export const organizationsAPI = {
  list: () => api.get('/organizations/'),
  create: (data) => api.post('/organizations/', data),
  get: (id) => api.get(`/organizations/${id}/`),
  update: (id, data) => api.put(`/organizations/${id}/`, data),
  delete: (id) => api.delete(`/organizations/${id}/`),
  getMembers: (id) => api.get(`/organizations/${id}/members/`),
  inviteMember: (id, data) => api.post(`/organizations/${id}/invite_member/`, data),
  
  // Invite functions
  getInvites: (id) => api.get(`/organizations/${id}/invites/`),
  createInvite: (id, data) => api.post(`/organizations/${id}/create_invite/`, data),
  revokeInvite: (id, data) => api.post(`/organizations/${id}/revoke_invite/`, data),
  acceptInvite: (data) => api.post('/invites/accept/', data),
  
  // Member management functions
  updateMemberRole: (orgId, memberId, data) => api.patch(`/organizations/${orgId}/members/${memberId}/`, data),
  removeMember: (orgId, memberId) => api.delete(`/organizations/${orgId}/members/${memberId}/`),
};

// Namespaces API functions
export const namespacesAPI = {
  list: () => api.get('/namespaces/'),
  create: (data) => api.post('/namespaces/', data),
  get: (id) => api.get(`/namespaces/${id}/`),
  update: (id, data) => api.put(`/namespaces/${id}/`, data),
  delete: (id) => api.delete(`/namespaces/${id}/`),
};

// Short URLs API functions
export const shortUrlsAPI = {
  list: () => api.get('/short-urls/'),
  create: (data) => api.post('/short-urls/', data),
  get: (id) => api.get(`/short-urls/${id}/`),
  update: (id, data) => api.put(`/short-urls/${id}/`, data),
  delete: (id) => api.delete(`/short-urls/${id}/`),
  getByNamespace: (namespaceId) => api.get(`/short-urls/by_namespace/?namespace_id=${namespaceId}`),
  redirect: (id) => api.post(`/short-urls/${id}/redirect/`),
};

export default api;
