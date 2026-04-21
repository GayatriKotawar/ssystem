import axios from 'axios';

const isLocalDevelopment =
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1';

const api = axios.create({
  baseURL: isLocalDevelopment ? 'http://localhost:8000/api' : '/api',
});

// Since we're not using JWT right now, we can pass user ID if needed or let components handle auth state
export default api;
