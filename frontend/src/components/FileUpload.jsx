import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [clauses, setClauses] = useState([]);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setClauses([]);
    setResponse('');
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first.");
    const formData = new FormData();
    formData.append('file', file);
    try {
      setLoading(true);
      const res = await axios.post('http://localhost:5000/upload', formData);
      setClauses(res.data.clauses || []);
      setResponse('');
    } catch (error) {
      alert('File upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!question) return alert("Please type a question.");
    try {
      setLoading(true);
      const res = await axios.post('http://localhost:5000/ask', { question });
      setResponse(res.data.response || 'No response from Gemini');
    } catch (err) {
      setResponse('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload a PDF and Extract Clauses</h2>
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? 'Uploading...' : 'Upload & Analyze'}
      </button>

      {clauses.length > 0 && (
        <>
          <h3>📄 Extracted Clauses</h3>
          <ul className="clauses-list">
            {clauses.map((clause, i) => (
              <li key={i}>{clause}</li>
            ))}
          </ul>
        </>
      )}

      <div className="ask-section">
        <h3>🤖 Ask about a clause</h3>
        <input
          type="text"
          value={question}
          placeholder="e.g., What are the termination conditions?"
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button onClick={handleAsk} disabled={loading}>
          Ask
        </button>

        {response && (
          <div className="response-box">
            <strong>Answer:</strong>
            <p>{response}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
