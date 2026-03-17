import React from 'react';
import ReactMarkdown from 'react-markdown';
import SourceBadge
 from './SourceBadge';

 const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user';
  const isBot = message.role === 'bot';

  // NEU: Logik zum Trennen von Text und Quellen-JSON
  let displayContent = String(message.text || message.content || ""); // Sicherstellen, dass es ein String ist
  let extractedSources = message.sources || [];

  // Wenn es vom Bot kommt und den Trenner enthält
if (isBot && typeof displayContent === 'string' && displayContent.includes(' [SOURCES] ')) {
    const parts = displayContent.split(' [SOURCES] ');
    displayContent = parts[0];
    try {
      extractedSources = JSON.parse(parts[1]);
    } catch (e) {
      console.error("Quellen-Parsing fehlgeschlagen", e);
    }
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[85%] p-4 rounded-2xl shadow-lg ${
        isUser 
        ? 'bg-blue-600 text-white rounded-tr-none' 
        : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-none'
      }`}>
        <div className="prose prose-invert prose-sm max-w-none">
          <ReactMarkdown>
            {displayContent} 
          </ReactMarkdown>
        </div>

        {/* NEU: Wir übergeben das extrahierte Array */}
        {!isUser && extractedSources.length > 0 && (
          <SourceBadge sources={extractedSources} />
        )}
      </div>
    </div>
  );
};

export default MessageBubble;