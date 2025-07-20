// src/components/ClauseQuery.jsx

import React, { useState } from "react";
import axios from "axios";

const ClauseQuery = ({ onAnswer }) => {
  const [query, setQuery] = useState("");

  const handleQuery = async () => {
    if (!query.trim()) return;

    try {
      const res = await axios.post("http://127.0.0.1:8000/parse_query", { query });
      onAnswer(res.data.answer || "No answer received.");
    } catch (err) {
      onAnswer("Error reaching backend.");
      console.error(err);
    }
  };

  return (
    <div className="query-container">
      <input
        type="text"
        placeholder="Ask about a clause..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleQuery}>Ask</button>
    </div>
  );
};

export default ClauseQuery;
