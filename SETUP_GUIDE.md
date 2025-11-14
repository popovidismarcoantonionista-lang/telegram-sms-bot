# 🔧 Guia Completo de Configuração

## 📋 Índice
1. [Variáveis de Ambiente](#variáveis-de-ambiente)
2. [Configuração do Webhook Telegram](#webhook-telegram)
3. [Configuração do Webhook PixIntegra](#webhook-pixintegra)
4. [Obter Chaves das APIs](#obter-chaves)
5. [Testes e Verificação](#testes)

---

## 1️⃣ Variáveis de Ambiente

### 🚂 No Railway Dashboard

1. **Acesse seu projeto** no Railway
2. Clique na aba **"Variables"**
3. Clique em **"New Variable"**
4. **Cole uma por vez** as variáveis abaixo:

### 📝 Variáveis para Copiar

```env
TELEGRAM_BOT_TOKEN=8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw
```
**O que é:** Token do seu bot Telegram (já configurado)

---

```env
TELEGRAM_WEBHOOK_URL=https://SEU-DOMINIO.up.railway.app/webhook/telegram
```
**⚠️ IMPORTANTE:** Troque `SEU-DOMINIO` pela URL gerada pelo Railway!

**Como obter o domínio:**
1. Railway → Settings → Networking
2. Clique em "Generate Domain"
3. Copie a URL (ex: `telegram-sms-bot-production.up.railway.app`)
4. Use: `https://telegram-sms-bot-production.up.railway.app/webhook/telegram`

---

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
```
**O que é:** Conexão automática com PostgreSQL do Railway
**Ação:** Apenas cole assim mesmo, o Railway preenche automaticamente

---

```env
PIXINTEGRA_API_TOKEN=apitoken_fa6243cb521dbfaa0d6962661b82b8f8308e100101a934
```
**O que é:** Token da API PixIntegra (já configurado)

---

```env
PIXINTEGRA_WEBHOOK_SECRET=AmvmPouOg!KV@d9vF6*TYy4Qth7crsad
```
**O que é:** Secret para validar webhooks do PixIntegra
**Ação:** Copie exatamente como está (gerado automaticamente)

---

```env
PIXINTEGRA_BASE_URL=https://api.pixintegra.com.br/v1
```

---

```env
SMSACTIVATE_API_KEY=COLE_SUA_CHAVE_AQUI
```
**⚠️ VOCÊ PRECISA OBTER ESTA CHAVE!**

**Como obter:**
1. Acesse: https://sms-activate.org/
2. Faça cadastro/login
3. Vá em "Profile" → "API Key"
4. Copie a chave e cole aqui

---

```env
SMSACTIVATE_BASE_URL=https://api.sms-activate.org/stubs/handler_api.php
```

---

```env
APEX_API_KEY=84357bf831e306d7ecac494c34280025
```
**O que é:** API Key da Apex Seguidores (já configurada)

---

```env
APEX_BASE_URL=https://apexseguidores.com/api/v2
```

---

```env
JWT_SECRET_KEY=0uvtfSH1L12@y2iaU6Stoa)mJ=AxNhdIwSey8OfzFOpH+Xl^
```
**O que é:** Secret para tokens JWT (gerado automaticamente)

---

```env
WEBHOOK_HMAC_SECRET=@4^D%sQyn!Ue0PT83!&N)4XIbBH@vA0D(L!WBfZ1F3@R%6O$
```
**O que é:** Secret para validar webhooks (gerado automaticamente)

---

```env
ENVIRONMENT=production
```

---

```env
LOG_LEVEL=INFO
```

---

## 2️⃣ Configuração do Webhook Telegram

### Opção A: Via Script Automático (Recomendado)

1. Baixe o arquivo `scripts/setup_webhook.sh` do repositório
2. Edite e coloque seu domínio Railway
3. Execute:

```bash
chmod +x scripts/setup_webhook.sh
./scripts/setup_webhook.sh
```

### Opção B: Via cURL Manual

**Substitua `SEU-DOMINIO` pela URL do Railway:**

```bash
curl -X POST "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/setWebhook?url=https://SEU-DOMINIO.up.railway.app/webhook/telegram"
```

**Exemplo real:**
```bash
curl -X POST "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/setWebhook?url=https://telegram-sms-bot-production.up.railway.app/webhook/telegram"
```

### ✅ Verificar se funcionou:

```bash
curl "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/getWebhookInfo"
```

**Resposta esperada:**
```json
{
  "ok": true,
  "result": {
    "url": "https://seu-dominio.up.railway.app/webhook/telegram",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## 3️⃣ Configuração do Webhook PixIntegra

### No Dashboard da PixIntegra

1. Acesse: https://dashboard.pixintegra.com.br
2. Vá em **"Webhooks"** ou **"Configurações"**
3. Configure:

**URL do Webhook:**
```
https://SEU-DOMINIO.up.railway.app/webhook/pixintegra
```

**Secret/HMAC:**
```
AmvmPouOg!KV@d9vF6*TYy4Qth7crsad
```

**Eventos para escutar:**
- ✅ `charge.paid` (Pagamento confirmado)
- ✅ `charge.expired` (Pagamento expirado)
- ✅ `charge.cancelled` (Pagamento cancelado)

---

## 4️⃣ Obter Chaves das APIs

### 🔑 SMS-Activate

1. **Cadastro**: https://sms-activate.org/
2. **API Key**: 
   - Login → Profile → API
   - Copie a chave
   - Cole em `SMSACTIVATE_API_KEY`

### 💰 Adicionar Saldo (SMS-Activate)

O bot precisa de saldo para alugar números:
1. Vá em "Wallet" → "Add Funds"
2. Adicione pelo menos $10 USD
3. Use para testes

---

## 5️⃣ Testes e Verificação

### ✅ Checklist de Verificação

#### 1. Bot está Online?
```bash
curl https://SEU-DOMINIO.up.railway.app/health
```
**Esperado:** `{"status": "healthy"}`

#### 2. Webhook Telegram Configurado?
```bash
curl "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/getWebhookInfo"
```

#### 3. Bot Responde?
No Telegram:
1. Busque: `@SeuBotUsername`
2. Envie: `/start`
3. **Esperado:** Mensagem de boas-vindas

#### 4. Banco de Dados Conectado?
Railway Dashboard → Logs
**Procure:** `"Bot started successfully!"`

#### 5. Teste Completo: Comprar Créditos
1. `/start` - Iniciar bot
2. `/comprar_creditos` - Escolher plano
3. Enviar valor (ex: `10`)
4. **Esperado:** Receber QR Code PIX

---

## 🆘 Troubleshooting

### Erro: "Webhook não configurado"
```bash
# Remover webhook antigo
curl -X POST "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/deleteWebhook"

# Configurar novamente
curl -X POST "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/setWebhook?url=https://SEU-DOMINIO.up.railway.app/webhook/telegram"
```

### Erro: "Database connection failed"
Railway → Variables → Verifique `DATABASE_URL=${{Postgres.DATABASE_URL}}`

### Erro: "SMS-Activate API error"
1. Verifique se `SMSACTIVATE_API_KEY` está correto
2. Verifique saldo em https://sms-activate.org/

### Bot não responde
1. Railway → Logs → Procure erros
2. Verifique se todas as variáveis estão configuradas
3. Reinicie o deploy: Railway → Deployments → Redeploy

---

## 📊 Monitoramento

### Railway Logs
```bash
railway logs --tail
```

### Health Check
```bash
curl https://SEU-DOMINIO.up.railway.app/health
```

### Webhook Status
```bash
curl "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/getWebhookInfo"
```

---

## 🎉 Pronto!

Se tudo estiver verde ✅, seu bot está **100% operacional**!

**Próximos passos:**
1. Adicionar saldo no SMS-Activate
2. Testar compra de créditos com PIX de teste
3. Divulgar o bot para usuários

**Suporte:** Abra uma issue no GitHub se precisar de ajuda!
