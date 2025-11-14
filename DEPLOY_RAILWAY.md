# 🚂 Deploy no Railway

## Configuração Automática via GitHub

### 1. Acesse Railway
👉 https://railway.app/

### 2. Crie um Novo Projeto
1. Clique em **"New Project"**
2. Escolha **"Deploy from GitHub repo"**
3. Selecione: `popovidismarcoantonionista-lang/telegram-sms-bot`
4. Clique em **"Deploy Now"**

### 3. Configure as Variáveis de Ambiente

No Railway Dashboard, vá em **"Variables"** e adicione:

```env
# Telegram
TELEGRAM_BOT_TOKEN=8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw
TELEGRAM_WEBHOOK_URL=https://seu-app.railway.app/webhook/telegram

# Database (Railway PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# PixIntegra
PIXINTEGRA_API_TOKEN=apitoken_fa6243cb521dbfaa0d6962661b82b8f8308e100101a934
PIXINTEGRA_WEBHOOK_SECRET=seu_secret_hmac
PIXINTEGRA_BASE_URL=https://api.pixintegra.com.br/v1

# SMS-Activate
SMSACTIVATE_API_KEY=sua_chave
SMSACTIVATE_BASE_URL=https://api.sms-activate.org/stubs/handler_api.php

# Apex Seguidores
APEX_API_KEY=84357bf831e306d7ecac494c34280025
APEX_BASE_URL=https://apexseguidores.com/api/v2

# Security
JWT_SECRET_KEY=generate_random_32_chars_here
WEBHOOK_HMAC_SECRET=generate_random_hmac_secret

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 4. Adicione PostgreSQL
1. No Railway, clique em **"New"** → **"Database"** → **"Add PostgreSQL"**
2. O Railway irá automaticamente:
   - Criar o banco de dados
   - Adicionar `DATABASE_URL` às variáveis
   - Conectar ao seu app

### 5. Configure o Domínio
1. Vá em **"Settings"** → **"Networking"**
2. Clique em **"Generate Domain"**
3. Copie a URL gerada (ex: `telegram-sms-bot-production.up.railway.app`)
4. Atualize a variável `TELEGRAM_WEBHOOK_URL` com essa URL

### 6. Configure o Webhook do Telegram

```bash
curl -X POST "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/setWebhook?url=https://SEU-DOMINIO.railway.app/webhook/telegram"
```

### 7. Execute as Migrations

Via Railway CLI:
```bash
railway run python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

Ou acesse o PostgreSQL e execute `migrations/init.sql`

---

## ✅ Deploy Completo!

Seu bot estará rodando 24/7 no Railway com:
- ✅ Auto-deploy no push do GitHub
- ✅ PostgreSQL integrado
- ✅ SSL automático
- ✅ Logs em tempo real
- ✅ Métricas de performance

## 📊 Monitoramento

- **Logs**: Railway Dashboard → Logs
- **Métricas**: Railway Dashboard → Metrics
- **Status**: https://seu-dominio.railway.app/health

## 🔧 Troubleshooting

### Bot não responde
```bash
# Verifique se o webhook está configurado
curl https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/getWebhookInfo
```

### Database error
```bash
# Verifique a conexão
railway run psql $DATABASE_URL -c "SELECT 1;"
```

### Logs
```bash
# Railway CLI
railway logs
```

---

## 💰 Custos Railway

- **Starter Plan**: $5/mês
  - 500 horas de execução
  - 5GB transferência
  - Perfeito para o bot

- **Developer Plan**: $20/mês (se precisar escalar)

---

## 🔄 Auto-Deploy

Qualquer push para `main` no GitHub dispara deploy automático! 🚀
