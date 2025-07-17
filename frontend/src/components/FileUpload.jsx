// 📁 File: frontend/src/components/FileUpload.jsx

import React, { useState } from "react";
import axios from "axios";

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [clauses, setClauses] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return alert("Please choose a file");

    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);

    try {
      const response = await axios.post("/upload", formData);
      setClauses(response.data);
    } catch (error) {
      alert("Upload failed!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-4 text-center">ClauseGPT - Upload Policy Document</h1>

      <input type="file" onChange={handleFileChange} accept=".pdf,.docx" className="mb-4" />
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        onClick={handleUpload}
      >
        {loading ? "Uploading..." : "Upload & Extract Clauses"}
      </button>

      {clauses.length > 0 && (
        <div className="mt-6">
          <h2 className="font-semibold text-lg">Extracted Clauses</h2>
          <ul className="bg-gray-100 p-4 rounded mt-2">
            {clauses.map((clause) => (
              <li key={clause.clause_id} className="mb-2">
                <strong>{clause.clause_id}</strong>: {clause.text}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
