import axios from "axios";

const baseURL =
  (process.env.REACT_APP_API_URL && process.env.REACT_APP_API_URL.trim()) ||
  "http://127.0.0.1:5000";

const http = axios.create({
  baseURL,
  timeout: 15000,
});

http.interceptors.response.use(
  (res) => res,
  (err) => {
    const apiMsg =
      err?.response?.data?.message ||
      err?.response?.data?.error ||
      err?.message ||
      "Erro de rede. Tente novamente.";

    const normalized = new Error(apiMsg);
    normalized.status = err?.response?.status;
    normalized.data = err?.response?.data;

    return Promise.reject(normalized);
  }
);

export default http;
