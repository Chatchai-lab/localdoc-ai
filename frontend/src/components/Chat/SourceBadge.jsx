import React from 'react';

const SourceBadge = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  // Deduplizierung: Wir machen die Objekte zu Strings, um Set zu nutzen, 
  // oder filtern manuell nach eindeutigen Dateiname+Seite Kombis
  const uniqueSources = sources.filter((v, i, a) => 
    a.findIndex(t => (t.source === v.source && t.page === v.page)) === i
  );

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      <span className="text-[10px] text-slate-500 self-center uppercase font-bold tracking-tight">Quellen:</span>
      {uniqueSources.map((src, index) => (
        <div 
          key={index} 
          className="flex items-center gap-1 bg-blue-500/10 border border-blue-500/30 text-blue-400 px-2 py-1 rounded-md text-[11px] font-medium"
          title={src.source} // Zeigt den vollen Pfad beim Hover
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {/* Nur Dateiname anzeigen, falls es ein Pfad ist */}
          {src.source.split('/').pop()} <span className="opacity-60 ml-0.5">S.{src.page}</span>
        </div>
      ))}
    </div>
  );
};

export default SourceBadge;