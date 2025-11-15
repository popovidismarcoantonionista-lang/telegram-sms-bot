# 🚀 GUIA COMPLETO DE DEPLOY - Telegram SMS Bot

## ✅ PRÉ-REQUISITOS CONCLUÍDOS:
- ✅ Webhook deletado
- ✅ Config.py corrigido (campos opcionais)
- ✅ SQLite como banco padrão
- ✅ Commit no GitHub realizado

---

## 🛤️ DEPLOY NO RAILWAY (MÉTODO AUTOMÁTICO)

### PASSO 1: Criar Projeto

Acesse um destes links:

**Opção A - Template direto:**
```
https://railway.app/template/github.com/popovidismarcoantonionista-lang/telegram-sms-bot
```

**Opção B - Deploy manual:**
```
https://railway.app/new
```

---

### PASSO 2: Configurar Variáveis (MÍNIMAS)

No Railway Dashboard → **Variables**, adicione:

```bash
TELEGRAM_BOT_TOKEN=8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw
TELEGRAM_WEBHOOK_URL=https://AGUARDE-URL.up.railway.app/webhook/telegram
```

⚠️ **IMPORTANTE:** Deixe a URL temporária, vamos atualizar!

---

### PASSO 3: Aguardar Build (2-3 min)

Railway vai:
- ✅ Clonar repositório
- ✅ Instalar Python + dependências
- ✅ Iniciar FastAPI
- ✅ Gerar URL automática

**Status esperado:** 🟢 Active

---

### PASSO 4: Copiar URL Gerada

Exemplo de URL:
```
telegram-sms-bot-production.up.railway.app
```

---

### PASSO 5: Atualizar Webhook URL

**No Railway → Variables**, edite para:
```bash
TELEGRAM_WEBHOOK_URL=https://SUA-URL-REAL.up.railway.app/webhook/telegram
```

Railway reinicia automaticamente!

---

## 📡 CONFIGURAR WEBHOOK DO TELEGRAM

### Opção A - Comando cURL (RECOMENDADO)

```bash
curl -X POST "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/setWebhook?url=https://SUA-URL-RAILWAY.up.railway.app/webhook/telegram"
```

### Opção B - Browser

Cole no navegador:
```
https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/setWebhook?url=https://SUA-URL-RAILWAY.up.railway.app/webhook/telegram
```

**Resposta esperada:**
```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

---

## 🧪 TESTAR BOT

1. Abra Telegram
2. Procure: **@vendasmseseguidoresbot**
3. Envie: **/start**

**Resposta esperada:** Mensagem de boas-vindas! ✅

---

## 🔍 VERIFICAR STATUS

### Verificar Webhook:
```bash
curl "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/getWebhookInfo"
```

### Verificar Health:
```bash
curl https://SUA-URL-RAILWAY.up.railway.app/health
```

**Resposta esperada:**
```json
{"status":"healthy"}
```

---

## 🐛 TROUBLESHOOTING

### Bot não responde?

1. **Verificar logs no Railway:**
   - Dashboard → Deployments → View Logs

2. **Verificar webhook:**
   ```bash
   curl "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/getWebhookInfo"
   ```

3. **Verificar variáveis:**
   - Railway → Variables
   - Confirmar TELEGRAM_WEBHOOK_URL está correto

### Erro "Connection refused"?

- Aguardar 30-60 segundos após deploy
- Railway pode estar iniciando

### Webhook não recebe updates?

- Deletar webhook e reconfigurar:
  ```bash
  curl -X POST "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/deleteWebhook"
  curl -X POST "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/setWebhook?url=https://SUA-URL.up.railway.app/webhook/telegram"
  ```

---

## ⚙️ CONFIGURAÇÕES OPCIONAIS (DEPOIS)

### Adicionar SMS-Activate:
```bash
SMSACTIVATE_API_KEY=fdc8b17A0d37f586b31f7fef44A04263
```

### Adicionar PIX (PixIntegra):
```bash
PIXINTEGRA_API_TOKEN=sua_chave
PIXINTEGRA_WEBHOOK_SECRET=AmvmPouOg!KV@d9vF6*TYy4Qth7crsad
```

### Adicionar Seguidores (Apex):
```bash
APEX_API_KEY=sua_chave
```

### Trocar para PostgreSQL:
```bash
DATABASE_URL=postgresql://user:password@host:5432/db
```

---

## 📊 MONITORAMENTO

### Métricas Railway:
- CPU usage
- Memory usage
- Network traffic

### Logs em tempo real:
```bash
railway logs --follow
```

---

## 🎉 DEPLOY COMPLETO!

✅ Bot funcionando 24/7 no Railway
✅ Webhook configurado
✅ Banco SQLite funcionando
✅ Logs disponíveis

---

## 🔗 LINKS ÚTEIS

- **Repositório:** https://github.com/popovidismarcoantonionista-lang/telegram-sms-bot
- **Railway:** https://railway.app/dashboard
- **Bot Telegram:** @vendasmseseguidoresbot
- **Commit de correção:** https://github.com/popovidismarcoantonionista-lang/telegram-sms-bot/commit/448614f677b843179e3cf45b61251c8ec87cc11f

---

**🚀 BOT PRONTO PARA PRODUÇÃO!**
