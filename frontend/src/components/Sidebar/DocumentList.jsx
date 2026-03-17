import React from 'react';
import Button from '../UI/Button';

const DocumentList = ({ documents, onDelete }) => {
  if (documents.length === 0) {
    return (
      <div className="text-center p-4 bg-slate-800/30 rounded-lg border border-dashed border-slate-700">
        <p className="text-xs text-slate-500">Keine Dokumente vorhanden</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div 
          key={doc.name} 
          className="group flex justify-between items-center p-3 bg-slate-800/50 rounded-lg border border-slate-700/50 hover:border-blue-500/50 transition-all"
        >
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-medium truncate text-slate-200" title={doc.name}>
              {doc.name}
            </span>
            <span className="text-[10px] text-slate-500 font-mono">
              {doc.size_kb} KB
            </span>
          </div>
          
          <Button
            onClick={() => onDelete(doc.name)}
            variant="danger"
            className="opacity-0 group-hover:opacity-100 p-1.5"
            title="Löschen"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </Button>
        </div>
      ))}
    </div>
  );
};

export default DocumentList;