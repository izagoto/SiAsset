import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor untuk menambahkan token
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

// Response interceptor untuk handle token expired
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  
  refreshToken: (refreshToken) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  
  getCurrentUser: () =>
    api.get('/auth/me'),
  
  logout: () =>
    api.post('/auth/logout'),
};

// Users API
export const usersAPI = {
  getUsers: (params = {}) =>
    api.get('/users', { params }),
  
  getUser: (userId) =>
    api.get(`/users/${userId}`),
  
  createUser: (data) =>
    api.post('/users', data),
  
  updateUser: (userId, data) =>
    api.put(`/users/${userId}`, data),
  
  deleteUser: (userId) =>
    api.delete(`/users/${userId}`),
  
  activateUser: (userId) =>
    api.post(`/users/${userId}/activate`),
  
  deactivateUser: (userId) =>
    api.post(`/users/${userId}/deactivate`),
};

// Assets API
export const assetsAPI = {
  getAssets: (params = {}) =>
    api.get('/assets/list_assets', { params }),
  
  getAsset: (assetId) =>
    api.get(`/assets/${assetId}/get_asset`),
  
  createAsset: (data) =>
    api.post('/assets/create_asset', data),
  
  updateAsset: (assetId, data) =>
    api.put(`/assets/${assetId}/update_asset`, data),
  
  deleteAsset: (assetId) =>
    api.delete(`/assets/${assetId}/delete_asset`),
};

// Loans API
export const loansAPI = {
  getLoans: (params = {}) =>
    api.get('/loans', { params }),
  
  getLoan: (loanId) =>
    api.get(`/loans/${loanId}`),
  
  createLoan: (data) =>
    api.post('/loans', data),
  
  approveLoan: (loanId, data = {}) =>
    api.post(`/loans/${loanId}/approve`, data),
  
  rejectLoan: (loanId, data = {}) =>
    api.post(`/loans/${loanId}/reject`, data),
  
  startBorrowing: (loanId) =>
    api.post(`/loans/${loanId}/start`),
  
  returnLoan: (loanId, data = {}) =>
    api.post(`/loans/${loanId}/return`, data),
  
  checkOverdue: () =>
    api.post('/loans/check-overdue'),
};

export default api;

