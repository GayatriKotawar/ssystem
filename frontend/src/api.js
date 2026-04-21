import axios from 'axios';

// The FastAPI backend runs on 8000 by default (uvicorn)
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Since we're not using JWT right now, we can pass user ID if needed or let components handle auth state
export default api;
