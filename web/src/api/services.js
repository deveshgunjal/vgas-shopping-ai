import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// Auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('vgas_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
};

export const searchAPI = {
  search: (query) => api.get('/search/', { params: { query } }),
  lootDeals: () => api.get('/search/loot-deals'),
  trending: () => api.get('/search/trending'),
  visualSearch: (image) => api.post('/visual-search', { image }),
};

export const productsAPI = {
  getById: (id) => api.get(`/products/${id}`),
  compare: (ids) => api.post('/compare/', { product_ids: ids }),
  priceHistory: (id) => api.get(`/products/${id}/price-history`),
  stores: (id) => api.get(`/products/${id}/stores`),
};

export const aiAPI = {
  chat: (message) => api.post('/ai/chat/send', { message }),
  pricePrediction: (id) => api.get(`/ai/predict/${id}`),
  recommendations: () => api.get('/ai/recommendations'),
};

export const cartAPI = {
  get: () => api.get('/cart'),
  add: (productId) => api.post('/cart/add', { product_id: productId }),
  remove: (productId) => api.delete(`/cart/${productId}`),
  checkout: () => api.post('/cart/checkout'),
};

export const userAPI = {
  profile: () => api.get('/users/me'),
  updateProfile: (data) => api.put('/users/me', data),
  alerts: () => api.get('/users/alerts'),
  createAlert: (data) => api.post('/users/alerts', data),
  earnings: () => api.get('/users/earnings'),
};

export const adminAPI = {
  stats: () => api.get('/admin/stats'),
  products: () => api.get('/admin/products'),
  scrapers: () => api.get('/admin/scrapers'),
  users: () => api.get('/admin/users'),
  deals: () => api.get('/admin/deals'),
};

export default api;
