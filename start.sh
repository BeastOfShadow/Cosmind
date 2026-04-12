#!/bin/bash

# Abilita l'uscita in caso di errore
set -e

echo "========================================="
echo "🧠 Avvio Sistema Neural Network"
echo "========================================="

docker-compose up -d --build

# 1. Controllo strategia LLM (Cloud vs Locale)
set -a
[ -f .env ] && source .env
set +a

if [ -n "$OPENAI_API_KEY" ]; then
    echo "🔑 Chiave OpenAI trovata in .env! Verrà usata l'API in cloud per velocizzare tutto."
    echo "⏭️ Salto il controllo e il download del modello locale (Ollama)."
else
    # Fallback logico: l'utente non ha impostato la chiave OpenAI, usiamo Ollama
    TARGET_MODEL=${LLM_MODEL:-qwen2.5:14b}
    echo "🦙 Nessuna chiave OpenAI trovata. Eseguo il fallback in locale."
    echo "🔄 Verifica e aggiornamento dei modelli Ollama sul Mac..."
    ollama pull $TARGET_MODEL || echo "⚠️ Ollama non sta girando o comando fallito. Assicurati che l'app Ollama sia aperta sul Mac!"
    
    # Check vision model for images
    VISION_MODEL="llama3.2-vision"
    echo "👁️ Scaricando il modello vision di default per le immagini ($VISION_MODEL)..."
    ollama pull $VISION_MODEL || echo "⚠️ Modello vision non scaricato, usa OPENAI per la visione se fallisce."
fi

# 2. Ricostruisci e avvia i container Docker
echo "🐳 Avvio del container Docker..."
docker-compose up -d --build

echo "========================================="
echo "✅ Sistema pronto!"
echo "👉 Lancia il programma con ./run.sh"
echo "========================================="