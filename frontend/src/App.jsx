import React, { useState, useEffect } from 'react';
import { api } from './api/client';
import UploadButton from './components/Sidebar/UploadButton';
import Stats from './components/Sidebar/Stats';
import ChatWindow from './components/Chat/ChatWindow';
import DocumentList from './components/Sidebar/DocumentList';

function App() {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState({ standard: 0, docling: 0 });

  // Daten vom Backend laden
  const fetchData = async () => {
    try {
      const docsData = await api.getDocuments();
      const statsData = await api.getStats();
      setDocuments(docsData.documents || []);
      setStats(statsData.documents_counts || { standard: 0, docling: 0 });
    } catch (err) {
      console.error("Backend nicht erreichbar?", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="flex h-screen w-full bg-[#0f172a] text-slate-200 overflow-hidden font-sans">

      {/* SIDEBAR: Verwaltung der Dokumente */}
      <aside className="w-80 bg-[#1e293b] border-r border-slate-700 flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-xl font-bold text-blue-400">LocalDoc AI</h1>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <UploadButton onUploadSuccess={fetchData} />
          <h3 className="text-xs uppercase text-slate-500 font-bold mb-4 tracking-wider mt-6">
            Dokumente
          </h3>
          <DocumentList
            documents={documents}
            onDelete={async (docName) => {
              try {
                await api.deleteDocument(docName);
                fetchData();
              } catch (err) {
                console.error("Fehler beim Löschen:", err);
              }
            }}
          />
        </div>

        <div className="p-4 bg-[#111827] border-t border-slate-700">
          <Stats stats={stats} />
        </div>
      </aside>

      {/* MAIN AREA: Der Chat-Spezialist */}
      <main className="flex-1 flex flex-col bg-[#0f172a] relative">
        <ChatWindow onMessageSent={fetchData} />
      </main>
    </div>
  );
}

export default App;