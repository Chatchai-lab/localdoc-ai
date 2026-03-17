import React from 'react';

const SourceBadge = ({ sources }) => {
  if (!Array.isArray(sources) || sources.length === 0) return null;

  // 1. Intelligentes Filtern von Duplikaten
  const uniqueSources = sources.filter((v, i, a) => 
    v && a.findIndex(t => t && (
      (t.source || t.name || t.metadata?.source || t.file_name) === 
      (v.source || v.name || v.metadata?.source || v.file_name) && 
      (t.page || t.metadata?.page) === (v.page || v.metadata?.page)
    )) === i
  );

  return (
    <div className="mt-3 pt-3 border-t border-slate-700/50 flex flex-wrap gap-2">
      <span className="text-[10px] text-slate-500 self-center uppercase font-bold tracking-tight">
        Quellen:
      </span>
      {uniqueSources.map((src, index) => {
        // 2. Wir suchen den Dateinamen in allen üblichen Verdächtigen
        const rawPath = src.source || src.name || src.metadata?.source || src.file_name || src.filename || "Dokument";
        
        // 3. Wir suchen die Seitenzahl (viele Loader nutzen metadata.page)
        const pageNumber = src.page ?? src.metadata?.page ?? src.page_label ?? "?";

        // Dateinamen aus Pfad extrahieren (Windows & Linux Support)
        const fileName = rawPath.split('/').pop().split('\\').pop();

        return (
          <div 
            key={index} 
            className="flex items-center gap-1 bg-blue-500/10 border border-blue-500/30 text-blue-400 px-2 py-1 rounded-md text-[11px] font-medium"
            title={rawPath}
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="max-w-[180px] truncate">{fileName}</span>
            <span className="opacity-60 ml-0.5 whitespace-nowrap text-[10px]">S.{pageNumber}</span>
          </div>
        );
      })}
    </div>
  );
};

export default SourceBadge;