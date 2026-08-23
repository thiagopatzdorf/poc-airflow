#!/usr/bin/env bash
set -euo pipefail

# Executar uma vez, em terminal interativo na honda. Exige sudo e nao recebe senhas.
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker patz
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
sudo tailscale set --operator=patz

echo "Host preparado. Encerre e abra a sessao para aplicar o grupo docker."
echo "Depois: cd ~/poc-airflow && make init && make up && tailscale serve --bg 8080 && make status"
