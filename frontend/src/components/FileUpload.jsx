import React, { useState } from "react";
import axios from "axios";
import "./FileUpload.css";

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [clauses, setClauses] = useState([]);
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setClauses([]);
    setResponse("");
    setError("");
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError("");
    setResponse("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:5000/upload", formData);
      setClauses(res.data.clauses || []);
    } catch (err) {
      setError("Failed to extract clauses. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!question) return;
    setLoading(true);
    setError("");

    try {
      const res = await axios.post("http://localhost:5000/ask", {
        question: question,
      });
      setResponse(res.data.answer || "No response.");
    } catch (err) {
      setError("Error getting response.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <input type="file" accept=".pdf" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Analyzing..." : "Upload & Analyze"}
      </button>

      {clauses.length > 0 && (
        <div className="clauses-container">
          <h3>📑 Extracted Clauses</h3>
          <ul>
            {clauses.map((clause, index) => (
              <li key={index}>{clause}</li>
            ))}
          </ul>
        </div>
      )}

      {clauses.length > 0 && (
        <div className="question-box">
          <h3>🤖 Ask about a clause</h3>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. What are the termination conditions?"
          />
          <button onClick={handleAsk} disabled={loading}>
            Ask
          </button>
        </div>
      )}

      {response && (
        <div className="response-box">
          <h3>💡 Answer:</h3>
          <p>{response}</p>
        </div>
      )}

      {error && <p className="error-msg">❌ {error}</p>}
    </div>
  );
};

export default FileUpload;
