import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [clauses, setClauses] = useState([]); // ensure it's an array
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setClauses([]);
    setError("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await axios.post("http://localhost:8000/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });

      if (response.data.matched_clauses) {
        setClauses(response.data.matched_clauses);
      } else {
        setError("No clauses matched or backend returned nothing.");
        setClauses([]);
      }
    } catch (err) {
      console.error("Upload error:", err);
      setError("Error uploading or processing file.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h1>ClauseGPT - PDF Clause Extractor</h1>

      <input
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
      />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Analyzing..." : "Upload & Analyze"}
      </button>

      {error && <p className="error-message">{error}</p>}

      {clauses.length > 0 && (
        <div className="results">
          <h3>Matched Clauses:</h3>
          <ul>
            {clauses.map((clause, index) => (
              <li key={index}>{clause}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
