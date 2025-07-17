// src/api.js
import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000", // Matches your FastAPI port
});

export default API;
