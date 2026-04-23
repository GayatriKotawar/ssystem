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

// In local development, use a relative path so Vite's proxy handles the request.
// This avoids CORS entirely since requests stay on the same origin.
// In production, use the configured API base URL.
export const apiBaseUrl = isLocalDevelopment ? '/api' : (configuredApiBaseUrl || '/api');

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
      return 'Backend is not configured. Set VITE_API_BASE_URL in your environment variables.';
    }

    return 'Cannot connect to the backend server. Make sure the FastAPI backend is running on port 8000.';
  }

  if (error.response.status === 404) {
    return 'API route was not found. Check that the backend URL points to your deployed FastAPI service.';
  }

  if (error.response.status >= 500) {
    return 'The backend server returned an internal error. Check the backend logs.';
  }

  return fallbackMessage;
}

// Since we're not using JWT right now, we can pass user ID if needed or let components handle auth state
export default api;
