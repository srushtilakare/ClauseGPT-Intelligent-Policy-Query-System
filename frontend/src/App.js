// src/App.jsx

import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import ClauseQuery from "./components/ClauseQuery";
import "./App.css";

const App = () => {
  const [clauses, setClauses] = useState([]);
  const [answer, setAnswer] = useState("");

  return (
    <div className="app">
      <h1>ClauseGPT: Intelligent Policy Analyzer</h1>
      <FileUpload onClausesReceived={setClauses} />
      <ClauseQuery onAnswer={setAnswer} />

      <div className="output-section">
        <h2>📄 Extracted Clauses</h2>
        {clauses.length === 0 ? (
          <p>No clauses detected yet.</p>
        ) : (
          <ul>
            {clauses.map((clause, idx) => (
              <li key={idx}>{clause}</li>
            ))}
          </ul>
        )}

        <h2>🤖 Gemini Response</h2>
        <p>{answer}</p>
      </div>
    </div>
  );
};

export default App;
