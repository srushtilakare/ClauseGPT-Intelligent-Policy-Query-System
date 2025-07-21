// src/components/FileUpload.jsx

import React, { useState } from "react";
import axios from "axios";

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [clauses, setClauses] = useState([]);
  const [text, setText] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setClauses([]);
    setAnswer("");
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select a file.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:5000/upload", formData);
      setClauses(res.data.clauses);
      setText(res.data.text);
    } catch (err) {
      alert("Upload failed");
    }
  };

  const askGemini = async () => {
    try {
      const res = await axios.post("http://localhost:5000/ask", {
        question,
        context: text,
      });
      setAnswer(res.data.answer);
    } catch (err) {
      setAnswer("❌ Gemini API error. Try again.");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>ClauseGPT - PDF Clause Extractor</h2>
      <input type="file" accept="application/pdf" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload & Analyze</button>

      <h3>📄 Extracted Clauses</h3>
      <ul>
        {clauses.map((clause, idx) => (
          <li key={idx}>{clause}</li>
        ))}
      </ul>

      <h3>🤖 Gemini Response</h3>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask about a clause..."
        style={{ width: "70%" }}
      />
      <button onClick={askGemini}>Ask</button>

      {answer && (
        <div style={{ marginTop: "1rem", whiteSpace: "pre-wrap" }}>
          <strong>Answer:</strong>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
