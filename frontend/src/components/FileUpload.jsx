import React, { useState } from "react";
import axios from "axios";
import "./FileUpload.css";

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [clauses, setClauses] = useState([]);
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setClauses([]);
    setResponse("");
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await axios.post("http://localhost:8000/analyze", formData);
      setClauses(res.data.clauses || []);
    } catch (err) {
      setError("Failed to analyze the file.");
    } finally {
      setUploading(false);
    }
  };

  const handleQuerySubmit = async () => {
    if (!query) return;
    try {
      const res = await axios.post("http://localhost:8000/parse_query", { query });
      setResponse(res.data.response);
    } catch (err) {
      setResponse("Error fetching answer.");
    }
  };

  return (
    <div className="upload-container">
      <h2>ClauseGPT - PDF Clause Extractor</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={uploading}>
        {uploading ? "Analyzing..." : "Upload & Analyze"}
      </button>

      <h3>📄 Extracted Clauses</h3>
      {clauses.length > 0 ? (
        <ul>
          {clauses.map((clause, idx) => (
            <li key={idx}>{clause}</li>
          ))}
        </ul>
      ) : (
        <p>No clauses detected yet.</p>
      )}

      <h3>🤖 Gemini Response</h3>
      <input
        type="text"
        placeholder="Ask about a clause..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleQuerySubmit}>Ask</button>

      <p><strong>Answer:</strong> {response}</p>
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default FileUpload;
