import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
});

export const runPipeline = () => api.post('/run');
export const getRunHistory = () => api.get('/runs');
export const getLastReport = () => api.get('/report/latest');
export const getCompetitors = () => api.get('/competitors');
export const getArticles = (company) => api.get(`/articles${company ? `?company=${company}` : ''}`);
export const getSignals = () => api.get('/signals');
export const getAnalyses = () => api.get('/analyses');
export const getPipelineStatus = () => api.get('/status');
export const getVectorStats = () => api.get('/vector-stats');

export default api;
