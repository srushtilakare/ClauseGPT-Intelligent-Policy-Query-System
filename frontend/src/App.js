import React from 'react';
import FileUpload from './components/FileUpload';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <h1>ClauseGPT - PDF Clause Extractor</h1>
      <FileUpload />
    </div>
  );
}

export default App;
