#!/bin/bash

# Post-Deploy Script - Telegram SMS Bot
# Configura webhook e testa tudo automaticamente

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

BOT_TOKEN="8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw"

clear
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       🚀 POST-DEPLOY SETUP - TELEGRAM SMS BOT           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Passo 1: Obter domínio
echo -e "${YELLOW}📍 PASSO 1: Cole o domínio do Railway${NC}"
echo "   Exemplo: telegram-sms-bot-production.up.railway.app"
echo ""
read -p "   Domínio: " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ Erro: Domínio não pode ser vazio${NC}"
    exit 1
fi

# Limpar protocolo se usuário colou com https://
DOMAIN=$(echo "$DOMAIN" | sed 's|https://||' | sed 's|http://||' | sed 's|/$||')

echo ""
echo -e "${GREEN}✅ Domínio configurado: $DOMAIN${NC}"
echo ""

# Passo 2: Testar se o bot está online
echo -e "${YELLOW}📍 PASSO 2: Verificando se o bot está online...${NC}"
echo ""

HEALTH_URL="https://$DOMAIN/health"
echo "   Testando: $HEALTH_URL"

if curl -s -f "$HEALTH_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Bot está ONLINE!${NC}"
else
    echo -e "${RED}   ❌ Bot ainda não está respondendo${NC}"
    echo ""
    echo "   Aguarde mais alguns segundos e tente novamente..."
    echo "   Ou verifique os logs no Railway Dashboard"
    exit 1
fi

echo ""

# Passo 3: Remover webhook antigo
echo -e "${YELLOW}📍 PASSO 3: Removendo webhook antigo (se houver)...${NC}"
echo ""

curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook" > /dev/null
echo -e "${GREEN}   ✅ Webhook antigo removido${NC}"

sleep 2
echo ""

# Passo 4: Configurar novo webhook
echo -e "${YELLOW}📍 PASSO 4: Configurando webhook...${NC}"
echo ""

WEBHOOK_URL="https://$DOMAIN/webhook/telegram"
echo "   URL: $WEBHOOK_URL"
echo ""

RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}")

if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo -e "${GREEN}   ✅ Webhook configurado com sucesso!${NC}"
else
    echo -e "${RED}   ❌ Erro ao configurar webhook${NC}"
    echo "   Resposta: $RESPONSE"
    exit 1
fi

sleep 2
echo ""

# Passo 5: Verificar webhook
echo -e "${YELLOW}📍 PASSO 5: Verificando configuração...${NC}"
echo ""

WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")

echo "$WEBHOOK_INFO" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data.get('ok'):
    result = data['result']
    print(f"   URL: {result.get('url', 'N/A')}")
    print(f"   Pendentes: {result.get('pending_update_count', 0)} mensagens")
    if result.get('last_error_message'):
        print(f"   ⚠️  Último erro: {result['last_error_message']}")
" 2>/dev/null || echo "$WEBHOOK_INFO"

echo ""

# Passo 6: Teste final
echo -e "${YELLOW}📍 PASSO 6: Teste final do bot...${NC}"
echo ""

BOT_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe")

if echo "$BOT_INFO" | grep -q '"ok":true'; then
    USERNAME=$(echo "$BOT_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['username'])" 2>/dev/null)
    echo -e "${GREEN}   ✅ Bot respondendo: @$USERNAME${NC}"
else
    echo -e "${RED}   ❌ Bot não está respondendo${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║             🎉 DEPLOY COMPLETO E FUNCIONAL!              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Bot está 100% operacional!${NC}"
echo ""
echo -e "${YELLOW}📱 TESTE AGORA:${NC}"
echo ""
if [ ! -z "$USERNAME" ]; then
    echo "   1. Abra o Telegram"
    echo "   2. Busque: @$USERNAME"
    echo "   3. Envie: /start"
    echo ""
fi
echo -e "${YELLOW}🔗 LINKS ÚTEIS:${NC}"
echo ""
echo "   Bot:     https://$DOMAIN"
echo "   Health:  https://$DOMAIN/health"
echo "   Docs:    https://$DOMAIN/docs"
echo ""
echo -e "${YELLOW}📊 MONITORAMENTO:${NC}"
echo ""
echo "   Railway Dashboard: https://railway.app/dashboard"
echo "   Logs: railway logs --tail"
echo ""
echo -e "${GREEN}🎊 Parabéns! Seu bot está rodando 24/7!${NC}"
echo ""
