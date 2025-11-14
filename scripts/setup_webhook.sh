#!/bin/bash

# Setup Telegram Webhook Script
# Author: Telegram SMS Bot
# Description: Configura o webhook do Telegram automaticamente

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BOT_TOKEN="8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw"

echo -e "${GREEN}🤖 Telegram Webhook Setup${NC}"
echo "================================"
echo ""

# Perguntar domínio
echo -e "${YELLOW}Por favor, cole a URL do seu Railway:${NC}"
echo "Exemplo: telegram-sms-bot-production.up.railway.app"
read -p "Domínio: " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ Erro: Domínio não pode ser vazio${NC}"
    exit 1
fi

# Construir URL do webhook
WEBHOOK_URL="https://${DOMAIN}/webhook/telegram"

echo ""
echo -e "${YELLOW}📡 Configurando webhook...${NC}"
echo "URL: $WEBHOOK_URL"
echo ""

# Remover webhook antigo (se houver)
echo "🗑️  Removendo webhook antigo..."
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook" > /dev/null

sleep 2

# Configurar novo webhook
echo "✨ Configurando novo webhook..."
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}")

echo ""
echo "📋 Resposta:"
echo "$RESPONSE" | python3 -m json.tool

# Verificar se funcionou
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo ""
    echo -e "${GREEN}✅ Webhook configurado com sucesso!${NC}"
    echo ""
    echo "🔍 Verificando status..."
    sleep 1
    curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | python3 -m json.tool
    echo ""
    echo -e "${GREEN}🎉 Tudo pronto! Seu bot está online!${NC}"
    echo ""
    echo "📱 Teste agora:"
    echo "   1. Abra o Telegram"
    echo "   2. Busque seu bot"
    echo "   3. Envie /start"
else
    echo ""
    echo -e "${RED}❌ Erro ao configurar webhook${NC}"
    echo "Verifique se a URL está correta e o bot está rodando"
    exit 1
fi
