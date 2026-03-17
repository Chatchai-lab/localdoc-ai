import React, { useRef, useState } from 'react';
import { api } from '../../api/client';

const UploadButton = ({ onUploadSuccess }) => {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      await api.uploadDocument(file);
      // Benachrichtige die App.jsx, dass neue Daten geladen werden müssen
      onUploadSuccess(); 
    } catch (error) {
      alert("Upload fehlgeschlagen: " + error.message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="w-full">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf"
        className="hidden"
      />
      <button
        onClick={() => fileInputRef.current.click()}
        disabled={uploading}
        className={`w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-bold transition-all shadow-lg ${
          uploading 
          ? 'bg-slate-700 cursor-not-allowed' 
          : 'bg-blue-600 hover:bg-blue-500 active:scale-95'
        }`}
      >
        {uploading ? (
          <span className="animate-spin border-2 border-white border-t-transparent rounded-full w-4 h-4" />
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
          </svg>
        )}
        {uploading ? "Verarbeite..." : "PDF Hochladen"}
      </button>
    </div>
  );
};

export default UploadButton;