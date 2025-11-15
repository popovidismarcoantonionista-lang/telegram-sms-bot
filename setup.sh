#!/bin/bash

# 🚀 Script de Setup Automático - Telegram SMS Bot
# Este script configura o webhook automaticamente após o deploy

echo "================================================"
echo "🚀 SETUP TELEGRAM SMS BOT"
echo "================================================"
echo ""

# Verificar se a URL foi fornecida
if [ -z "$1" ]; then
    echo "❌ ERRO: URL do Railway não fornecida!"
    echo ""
    echo "USO:"
    echo "  ./setup.sh https://seu-dominio.up.railway.app"
    echo ""
    exit 1
fi

RAILWAY_URL="$1"
BOT_TOKEN="8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw"
WEBHOOK_URL="${RAILWAY_URL}/webhook/telegram"

echo "📋 Configurações:"
echo "  Railway URL: $RAILWAY_URL"
echo "  Webhook URL: $WEBHOOK_URL"
echo ""

# Passo 1: Verificar health
echo "🔍 Passo 1: Verificando health do bot..."
HEALTH_RESPONSE=$(curl -s "${RAILWAY_URL}/health")
echo "  Resposta: $HEALTH_RESPONSE"
echo ""

# Passo 2: Deletar webhook antigo (se houver)
echo "🧹 Passo 2: Removendo webhook antigo..."
DELETE_RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook")
echo "  Resposta: $DELETE_RESPONSE"
echo ""

# Passo 3: Configurar novo webhook
echo "📡 Passo 3: Configurando novo webhook..."
WEBHOOK_RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}")
echo "  Resposta: $WEBHOOK_RESPONSE"
echo ""

# Passo 4: Verificar webhook
echo "✅ Passo 4: Verificando webhook..."
INFO_RESPONSE=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")
echo "  Resposta: $INFO_RESPONSE"
echo ""

echo "================================================"
echo "✅ SETUP COMPLETO!"
echo "================================================"
echo ""
echo "🧪 TESTAR BOT:"
echo "  1. Abra o Telegram"
echo "  2. Procure: @vendasmseseguidoresbot"
echo "  3. Envie: /start"
echo ""
echo "🔗 VERIFICAR STATUS:"
echo "  curl ${RAILWAY_URL}/health"
echo "  curl https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo"
echo ""
