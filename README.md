# 🤖 Telegram SMS Bot - Créditos e Seguidores

Bot Telegram autônomo para venda de créditos SMS e seguidores com pagamento PIX automático.

## 📋 Funcionalidades

### ✅ Compra de Créditos
- **3 Planos**: Econômico (×1.7), Padrão (×2.2), Premium (×3.5)
- Pagamento via **PIX automático** (PixIntegra)
- Confirmação instantânea via webhook
- Crédito automático no saldo do usuário
- Descontos progressivos: 5%, 12%, 20%

### 📱 Números SMS Descartáveis
- Integração com **SMS-Activate**
- Suporte para WhatsApp, Telegram, Instagram, etc.
- Polling automático para receber código
- Devolução de créditos se expirar

### 👥 Compra de Seguidores
- Integração com **Apex Seguidores**
- Instagram, TikTok, YouTube, Twitter
- Acompanhamento de status do pedido

## 🏗️ Arquitetura

```
telegram-sms-bot/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configurações
│   ├── database.py             # SQLAlchemy models
│   ├── bot/
│   │   ├── telegram_bot.py     # Setup do bot
│   │   ├── handlers.py         # Comandos
│   │   └── keyboards.py        # Keyboards inline
│   ├── api/
│   │   ├── pixintegra_client.py
│   │   ├── sms_activate_client.py
│   │   └── apex_seguidores_client.py
│   ├── webhooks/
│   │   ├── telegram_webhook.py
│   │   └── pixintegra_webhook.py
│   └── utils/
│       ├── pricing.py          # Cálculo de preços
│       └── security.py         # JWT, HMAC
├── migrations/
│   └── init.sql                # Schema PostgreSQL
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## 🚀 Deploy Rápido

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/telegram-sms-bot.git
cd telegram-sms-bot
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
nano .env
```

**Variáveis obrigatórias:**
```env
# Telegram
TELEGRAM_BOT_TOKEN=seu_bot_token
TELEGRAM_WEBHOOK_URL=https://seu-dominio.com/webhook/telegram

# Database (use Supabase)
DATABASE_URL=postgresql://user:pass@host:5432/db

# PixIntegra
PIXINTEGRA_API_TOKEN=seu_token
PIXINTEGRA_WEBHOOK_SECRET=seu_secret

# SMS-Activate
SMSACTIVATE_API_KEY=sua_chave

# Apex Seguidores
APEX_API_KEY=sua_chave

# Security
JWT_SECRET_KEY=seu_secret_min_32_chars
WEBHOOK_HMAC_SECRET=seu_hmac_secret
```

### 3. Inicie com Docker
```bash
docker-compose up -d
```

### 4. Configure o webhook
```bash
curl -X POST "https://api.telegram.org/bot<SEU_TOKEN>/setWebhook?url=https://seu-dominio.com/webhook/telegram"
```

## 🗄️ Banco de Dados

O projeto usa **PostgreSQL** com as seguintes tabelas:

- **users**: Usuários do bot (tg_id, balance)
- **orders**: Pedidos de créditos (PIX)
- **sms_rents**: Aluguéis de números SMS
- **followers_orders**: Pedidos de seguidores
- **logs**: Logs de auditoria

### Schema automático
O schema é criado automaticamente via `migrations/init.sql` no primeiro start.

## 📱 Comandos do Bot

| Comando | Descrição |
|---------|-----------|
| `/start` | Iniciar o bot |
| `/saldo` | Ver saldo atual |
| `/comprar_creditos` | Comprar créditos via PIX |
| `/comprar_sms` | Alugar número SMS |
| `/comprar_seguidores` | Comprar seguidores |
| `/ajuda` | Ajuda e suporte |

## 💰 Sistema de Precificação

### Planos de Créditos
```python
PLAN_ECONOMIC_MULTIPLIER = 1.7   # R$ 10 → R$ 17 em créditos
PLAN_STANDARD_MULTIPLIER = 2.2   # R$ 10 → R$ 22 em créditos
PLAN_PREMIUM_MULTIPLIER = 3.5    # R$ 10 → R$ 35 em créditos
```

### Descontos Progressivos
```python
5-20 números:   5% desconto
21-100 números: 12% desconto
100+ números:   20% desconto
```

### Valor Mínimo
```python
MIN_PURCHASE_AMOUNT = 5.00  # R$ 5,00
```

## 🔒 Segurança

### Webhook PixIntegra
- Validação de assinatura **HMAC SHA256**
- Idempotência para evitar duplicações
- Rate limiting via Redis (opcional)

### JWT
- Tokens seguros para sessões
- Expiração configurável

### HTTPS
- **Obrigatório** para webhooks do Telegram

## 📊 Logs e Monitoramento

Todos os eventos são registrados na tabela `logs`:
- Webhooks recebidos
- Pagamentos confirmados
- Números SMS alugados
- Erros e exceções

```sql
SELECT * FROM logs WHERE source = 'pixintegra_webhook' ORDER BY timestamp DESC LIMIT 10;
```

## 🔄 Fluxo de Compra de Créditos

1. Usuário envia `/comprar_creditos`
2. Escolhe plano (Econômico/Padrão/Premium)
3. Envia valor em R$
4. Bot gera QR Code PIX via PixIntegra
5. Usuário paga o PIX
6. PixIntegra envia webhook de confirmação
7. Bot credita saldo automaticamente
8. Usuário recebe notificação no Telegram

## 📱 Fluxo de Compra de SMS

1. Usuário envia `/comprar_sms`
2. Escolhe serviço (WhatsApp, Telegram, etc.)
3. Bot aluga número via SMS-Activate
4. Desconta créditos do saldo
5. Envia número ao usuário
6. Bot faz polling para receber SMS
7. Envia código ao usuário
8. Se expirar, devolve créditos

## 🔧 Desenvolvimento

### Instalar dependências
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Rodar localmente
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testes com ngrok (webhook local)
```bash
ngrok http 8000
# Use a URL do ngrok como TELEGRAM_WEBHOOK_URL
```

## 📡 APIs Integradas

### PixIntegra
- **Documentação**: https://pixintegra-api.readme.io
- **Endpoint**: `https://api.pixintegra.com.br/v1`
- **Métodos**: `/charges` (POST), webhook (POST)

### SMS-Activate
- **Documentação**: https://sms-activate.org/en/api2
- **Endpoint**: `https://api.sms-activate.org/stubs/handler_api.php`
- **Métodos**: `getNumber`, `getStatus`, `setStatus`

### Apex Seguidores
- **Documentação**: Contate o suporte
- **Endpoint**: `https://apexseguidores.com/api/v2`
- **Métodos**: `/services`, `/order`, `/status`, `/cancel`

## 🐛 Troubleshooting

### Webhook não recebe pagamentos
```bash
# Verifique se o webhook está configurado
curl -X GET "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Verifique logs do PixIntegra
docker-compose logs app | grep pixintegra
```

### Números SMS não chegam
```bash
# Verifique o status da ativação
# O bot faz polling automático, mas você pode checar manualmente
```

### Banco de dados não conecta
```bash
# Verifique se o PostgreSQL está rodando
docker-compose ps

# Teste a conexão
psql -h localhost -U botuser -d telegram_bot
```

## 📝 TODO / Roadmap

- [ ] Painel admin web (FastAPI + React)
- [ ] Sistema de referral/afiliados
- [ ] Suporte a múltiplos idiomas
- [ ] Histórico de transações no bot
- [ ] Notificações push para status de pedidos
- [ ] Integração com mais provedores de SMS
- [ ] Sistema de cupons de desconto

## 📄 Licença

MIT License - veja `LICENSE` para detalhes.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📧 Suporte

- **Issues**: https://github.com/seu-usuario/telegram-sms-bot/issues
- **Email**: seu-email@exemplo.com
- **Telegram**: @seu_usuario

---

**Desenvolvido com ❤️ usando Python, FastAPI, e Telegram Bot API**
