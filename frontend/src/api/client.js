const API_BASE_URL = "http://backend:8000";

export const api = {
    // Ruft persistierte Dokumentenstatistiken aus dem Backend ab
    getStats: async () => {
        const response = await fetch(`${API_BASE_URL}/stats`);
        return await response.json();
    },

    // Ruft die Liste prozessierter PDF-Dokumente ab
    getDocuments: async () => {
        const response = await fetch(`${API_BASE_URL}/documents`);
        return await response.json();
    },

    // Überträgt ein neues Dokument zwecks Vektorisierung
    uploadDocument: async (file) => {
        const formData = new FormData();
        formData.append("file", file);
        const response = await fetch(`${API_BASE_URL}/documents`, {
            method: "POST",
            body: formData,
        });
        return await response.json();
    },

    // Entfernt ein Dokument und dessen zugehörige Vektoren
    deleteDocument: async (filename) => {
        const response = await fetch(`${API_BASE_URL}/documents/${filename}`, {
            method: "DELETE",
        });
        return await response.json();
    },

    askStream: async (question, onChunk, onSources) => {
        const response = await fetch(`${API_BASE_URL}/ask/stream`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question, k: 3 }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        // WICHTIG: Speicher für unvollständige Chunks
        let buffer = "";
        let sourcesFound = false;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk; // Wir sammeln erst mal alles im Buffer

            // Wenn wir den Marker noch nicht verarbeitet haben
            if (!sourcesFound && buffer.includes("[SOURCES]")) {
                const parts = buffer.split("[SOURCES]");

                // Alles VOR dem Marker ist normaler Text
                if (parts[0]) {
                    onChunk(parts[0]);
                }

                // Wir merken uns den Rest (das JSON)
                buffer = parts[1];
                sourcesFound = true;
            }

            // Wenn der Marker noch NICHT da ist, streamen wir den Text normal
            else if (!sourcesFound) {
                // Wir lassen ein bisschen Puffer am Ende (ca. 10 Zeichen), 
                // falls dort gerade "[SOURCES]" anfängt
                if (buffer.length > 10) {
                    const textToStream = buffer.slice(0, -10);
                    onChunk(textToStream);
                    buffer = buffer.slice(-10);
                }
            }
        }

        // Am Ende: Wenn wir im "Sources-Modus" sind, parsen wir den Rest des Buffers
        if (sourcesFound && buffer.trim()) {
            try {
                const sources = JSON.parse(buffer.trim());
                onSources(sources);
            } catch (e) {
                console.error("Fehler beim Parsen der Quellen:", e, buffer);
            }
        } else if (buffer.length > 0 && !sourcesFound) {
            // Falls noch Text übrig war, der kein Source-Marker war
            onChunk(buffer);
        }
    }
};