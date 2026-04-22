import axios from 'axios';

const isLocalDevelopment =
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1';

function normalizeApiBaseUrl(url) {
  if (!url) {
    return '';
  }

  const trimmedUrl = url.trim().replace(/\/+$/, '');
  return trimmedUrl.endsWith('/api') ? trimmedUrl : `${trimmedUrl}/api`;
}

const configuredApiBaseUrl = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL);
const localApiBaseUrl = 'http://localhost:8000/api';
const productionApiBaseUrl = configuredApiBaseUrl || localApiBaseUrl;

export const apiBaseUrl = isLocalDevelopment ? localApiBaseUrl : productionApiBaseUrl;

const api = axios.create({
  baseURL: apiBaseUrl,
});

export function getApiErrorMessage(error, fallbackMessage) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  if (!error?.response) {
    if (!isLocalDevelopment && !configuredApiBaseUrl) {
      return 'Backend is not configured for this Netlify site. Set VITE_API_BASE_URL in Netlify environment variables.';
    }

    return 'Cannot connect to the backend server. Check whether the API is deployed and VITE_API_BASE_URL is correct.';
  }

  if (error.response.status === 404) {
    return 'API route was not found. Check that the backend URL points to your deployed FastAPI service.';
  }

  if (error.response.status >= 500) {
    return 'The backend server returned an internal error. Check the backend deployment logs.';
  }

  return fallbackMessage;
}

// Since we're not using JWT right now, we can pass user ID if needed or let components handle auth state
export default api;
