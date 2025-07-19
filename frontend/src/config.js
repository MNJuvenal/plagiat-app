// Configuration des URLs API
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://plagiat-backend.onrender.com'  // URL de production sur Render
  : 'http://localhost:8000';  // URL de développement local

export const API_ENDPOINTS = {
  check: `${API_BASE_URL}/check`,
  upload: `${API_BASE_URL}/upload`,
  reformulate: `${API_BASE_URL}/reformulate`
};

export default API_BASE_URL;
