import React from 'react';
import ReactMarkdown from 'react-markdown';
import SourceBadge from './SourceBadge';

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user';
  const isBot = message.role === 'bot';

  // Wir nehmen die Daten direkt so, wie der Hook sie vorbereitet hat
  const displayContent = String(message.text || "");
  const extractedSources = message.sources || [];

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[85%] p-4 rounded-2xl shadow-lg ${
        isUser 
        ? 'bg-blue-600 text-white rounded-tr-none' 
        : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-none'
      }`}>
        {/* Markdown Anzeige für den Text */}
        <div className="prose prose-invert prose-sm max-w-none overflow-x-auto">
          <ReactMarkdown>
            {displayContent}
          </ReactMarkdown>
        </div>

        {/* Quellen Anzeige: Nur wenn es ein Bot ist und Quellen da sind */}
        {isBot && Array.isArray(extractedSources) && extractedSources.length > 0 && (
          <div className="mt-3">
            <SourceBadge sources={extractedSources} />
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;