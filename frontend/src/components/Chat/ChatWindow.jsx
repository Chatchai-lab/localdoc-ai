import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../api/client';
import MessageBubble from './MessageBubble';

const ChatWindow = ({ onMessageSent }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messageEndRef = useRef(null);

  // Automatischer Scroll nach unten
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput("");
    setLoading(true);

    // Platzhalter für KI-Antwort (Wichtig: role 'bot' passend zur MessageBubble Logik)
    const botMsgId = Date.now();
    setMessages(prev => [...prev, { role: 'bot', text: "", id: botMsgId }]);

    let fullAiText = "";
    try {
      await api.askStream(currentInput, (chunk) => {
        fullAiText += chunk;
        setMessages(prev => prev.map(msg => 
          msg.id === botMsgId ? { ...msg, text: fullAiText } : msg
        ));
      });
    } catch (err) {
      console.error("Streaming Fehler", err);
    } finally {
      setLoading(false);
      // Callback aufrufen, um z.B. Stats in der Sidebar zu aktualisieren
      if (onMessageSent) onMessageSent();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Nachrichtenbereich */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="max-w-3xl mx-auto w-full">
          {messages.length === 0 && (
            <div className="text-center mt-20 text-slate-500">
              <div className="text-4xl mb-4">📚</div>
              <p>Frag etwas über deine Dokumente oder lade ein neues PDF hoch.</p>
            </div>
          )}

          {messages.map((m, i) => (
            <MessageBubble key={m.id || i} message={m} />
          ))}

          <div ref={messageEndRef} />

          {loading && messages[messages.length-1]?.text === "" && (
            <div className="flex justify-start mb-4">
              <div className="bg-slate-800 p-4 rounded-2xl rounded-tl-none border border-slate-700 animate-pulse text-blue-400 text-xs font-mono">
                KI analysiert Dokumente...
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Eingabebereich */}
      <div className="p-6 bg-gradient-to-t from-[#0f172a] to-transparent">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Frage stellen..."
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-5 py-3 outline-none focus:ring-2 focus:ring-blue-500 transition-all text-slate-100"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 px-6 py-3 rounded-xl font-bold transition-all shadow-lg"
          >
            {loading ? '...' : 'Senden'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;