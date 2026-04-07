#!/bin/bash

# Abilita l'uscita in caso di errore
set -e

echo "========================================="
echo "🚀 Avvio Pannello di Controllo..."
echo "========================================="

# Esegue il main.py in modalità interattiva (-it) dentro il container
docker exec -it neural_network_agent python main.py