import React from "react";
import "./App.css";
import FileUpload from "./components/FileUpload";

function App() {
  return (
    <div className="app-container">
      <h1><center>📄 ClauseGPT - PDF Clause Extractor</center></h1>
      <FileUpload />
    </div>
  );
}

export default App;
