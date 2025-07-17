import React, { useState } from "react";
import axios from "axios";
import "./FileUpload.css"; // Make sure this file exists for styling

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [clauses, setClauses] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await axios.post("http://localhost:8000/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setClauses(response.data.clauses || []);
      setLoading(false);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Error uploading file. Try again.");
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Your Insurance Policy</h2>
      <input type="file" accept=".pdf" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>

      {loading && <p>⏳ Processing file, please wait...</p>}

      {clauses.length > 0 && (
        <div className="clauses-container">
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
