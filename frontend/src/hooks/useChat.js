import { useState } from 'react';
import { api } from '../api/client';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (input, onStreamComplete) => {
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    const botMsgId = Date.now();
    // WICHTIG: Wir fügen hier 'sources: []' hinzu
    setMessages(prev => [...prev, { role: 'bot', text: "", id: botMsgId, sources: [] }]);

    let fullAiText = "";
    try {
      // JETZT ÜBERGEBEN WIR DREI ARGUMENTE: input, chunk-funktion, sources-funktion
      await api.askStream(
        input, 
        (chunk) => {
          fullAiText += chunk;
          setMessages(prev => prev.map(msg => 
            msg.id === botMsgId ? { ...msg, text: fullAiText } : msg
          ));
        },
        (sources) => {
          // Wenn Quellen reinkommen, speichern wir sie in der Nachricht ab
          setMessages(prev => prev.map(msg => 
            msg.id === botMsgId ? { ...msg, sources: sources } : msg
          ));
        }
      );
      
      if (onStreamComplete) onStreamComplete();
      
    } catch (err) {
      console.error("Chat Hook Fehler:", err);
      setMessages(prev => prev.map(msg => 
        msg.id === botMsgId ? { ...msg, text: "Fehler: Verbindung unterbrochen." } : msg
      ));
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => setMessages([]);

  return { messages, loading, sendMessage, clearChat };
};