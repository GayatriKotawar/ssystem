import axios from 'axios';

const isLocalDevelopment =
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1';

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const localApiBaseUrl = 'http://localhost:8000/api';
const productionApiBaseUrl = configuredApiBaseUrl || localApiBaseUrl;

const api = axios.create({
  baseURL: isLocalDevelopment ? localApiBaseUrl : productionApiBaseUrl,
});

// Since we're not using JWT right now, we can pass user ID if needed or let components handle auth state
export default api;
