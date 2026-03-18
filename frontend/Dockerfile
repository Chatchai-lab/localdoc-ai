# 1. Node.js als Basis - Version 20 für Vite-Kompatibilität
FROM node:20-slim

WORKDIR /app

# 2. Package-Dateien kopieren
COPY package*.json ./

# 3. Installieren
RUN npm install

# 4. Restlichen Code kopieren
COPY . .

# 5. Port für Vite (Vorschau-Modus)
EXPOSE 5173

# 6. Startbefehl für Entwicklung
CMD ["npm", "run", "dev", "--", "--host"]