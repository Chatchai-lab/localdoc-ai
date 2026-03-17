import React from 'react';

const Stats = ({ stats }) => {
  return (
    <div className="grid grid-cols-2 gap-2 text-[10px] uppercase font-bold tracking-tighter">
      <div className="p-2 bg-slate-800 rounded border border-slate-700/50">
        <div className="text-slate-500 mb-1">Standard DB</div>
        <div className={`text-lg ${stats.standard > 0 ? "text-blue-400" : "text-slate-600"}`}>
          {stats.standard}
        </div>
      </div>
      <div className="p-2 bg-slate-800 rounded border border-slate-700/50">
        <div className="text-slate-500 mb-1">Docling DB</div>
        <div className={`text-lg ${stats.docling > 0 ? "text-purple-400" : "text-slate-600"}`}>
          {stats.docling}
        </div>
      </div>
    </div>
  );
};

export default Stats;