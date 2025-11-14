# 🤖 Bot Telegram SMS & Seguidores

Bot autônomo para venda de créditos, compra de números SMS descartáveis (SMS-Activate) e seguidores (Apex Seguidores) com pagamento automático via PIX (Pluggy.ai).

## 🚀 Recursos

- ✅ **Pagamento PIX Automático** via Pluggy.ai
- ✅ **Números SMS** de 190+ países via SMS-Activate
- ✅ **Compra de Seguidores** para Instagram, TikTok, YouTube via Apex
- ✅ **Liberação Instantânea** de créditos após pagamento
- ✅ **Sistema de Precificação** com 3 pacotes (Econômico, Padrão, Premium)
- ✅ **Descontos Progressivos** (5%, 12%, 20%)
- ✅ **Webhooks Seguros** com validação HMAC
- ✅ **Idempotência** para evitar duplicação de créditos
- ✅ **Logs Completos** em banco e arquivo

## 📦 Stack Tecnológica

- **Backend**: FastAPI + Python 3.11
- **Bot**: python-telegram-bot 20.7
- **Banco**: PostgreSQL 16
- **Cache/Rate Limit**: Redis
- **Deploy**: Docker + Railway
- **Segurança**: JWT, HMAC, Criptografia AES

## 🏗️ Estrutura do Projeto

```
telegram-sms-bot/
├── app/
│   ├── main.py              # FastAPI + Webhooks
│   ├── bot.py               # Handlers Telegram
│   ├── config.py            # Configurações
│   ├── database.py          # Models SQLAlchemy
│   ├── services/
│   │   ├── pluggy_service.py    # PIX Pluggy
│   │   ├── sms_activate.py      # SMS-Activate API
│   │   ├── apex_service.py      # Apex Seguidores API
│   │   ├── pricing.py           # Sistema precificação
│   │   └── security.py          # JWT/HMAC/Crypto
│   ├── models/
│   │   └── schemas.py           # Pydantic schemas
│   └── utils/
│       ├── logger.py            # Sistema logs
│       └── helpers.py           # Funções auxiliares
├── migrations/
│   └── init.sql                 # Schema PostgreSQL
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Deploy no Railway (5 minutos)

### 1️⃣ Pré-requisitos

- Conta no [Railway](https://railway.app)
- Conta no [Pluggy](https://pluggy.ai) (PIX)
- Conta no [SMS-Activate](https://sms-activate.org)
- Conta no [Apex Seguidores](https://apexseguidores.com)
- Bot Telegram criado via [@BotFather](https://t.me/botfather)

### 2️⃣ Configurar Serviços no Railway

1. **Criar Novo Projeto**
   ```bash
   # Clonar repositório
   git clone https://github.com/SEU_USUARIO/telegram-sms-bot.git
   cd telegram-sms-bot
   ```

2. **No Railway Dashboard:**
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Conecte este repositório

3. **Adicionar PostgreSQL:**
   - Clique em "+ New"
   - Selecione "Database" → "PostgreSQL"
   - Copie a `DATABASE_URL`

4. **Adicionar Redis:**
   - Clique em "+ New"
   - Selecione "Database" → "Redis"
   - Copie a `REDIS_URL`

### 3️⃣ Configurar Variáveis de Ambiente

No Railway, vá em "Variables" e adicione:

```env
# Database (copiado do Railway PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/db

# Telegram
TELEGRAM_BOT_TOKEN=seu_token_do_botfather
TELEGRAM_WEBHOOK_URL=https://seu-app.up.railway.app/webhook/telegram

# Pluggy.ai
PLUGGY_CLIENT_ID=seu_client_id
PLUGGY_CLIENT_SECRET=seu_client_secret
PLUGGY_WEBHOOK_SECRET=seu_webhook_secret
PLUGGY_API_URL=https://api.pluggy.ai

# SMS-Activate
SMS_ACTIVATE_API_KEY=sua_api_key
SMS_ACTIVATE_API_URL=https://api.sms-activate.org/stubs/handler_api.php

# Apex Seguidores
APEX_API_KEY=sua_apex_key
APEX_API_URL=https://api.apexseguidores.com
APEX_CREATE_ORDER_PATH=/v1/orders

# Security (gerar chaves seguras)
JWT_SECRET_KEY=chave_aleatoria_minimo_32_caracteres
ENCRYPTION_KEY=chave_base64_32_bytes

# App
APP_HOST=0.0.0.0
APP_PORT=8000
ENVIRONMENT=production
MIN_PURCHASE_BRL=5.00

# Redis (copiado do Railway Redis)
REDIS_URL=redis://default:pass@host:port
```

### 4️⃣ Configurar Webhooks

**Pluggy Webhook:**
- URL: `https://seu-app.up.railway.app/webhook/pluggy`
- Eventos: `payment.status.updated`

**Telegram Webhook:**
```bash
curl -X POST "https://api.telegram.org/bot<SEU_TOKEN>/setWebhook?url=https://seu-app.up.railway.app/webhook/telegram"
```

### 5️⃣ Deploy Automático

O Railway detecta o `Dockerfile` e faz deploy automático! 🚀

Aguarde 2-3 minutos e seu bot estará online 24/7!

## 🧪 Testar o Bot

1. Abra o Telegram
2. Procure seu bot pelo username
3. Envie `/start`
4. Teste os comandos:
   - `/comprar_creditos` - Comprar créditos via PIX
   - `/comprar_sms` - Adquirir número SMS
   - `/comprar_seguidores` - Comprar seguidores
   - `/saldo` - Ver saldo e histórico

## 💰 Sistema de Precificação

### Fórmula
```
Preço Final = (Custo Base + Taxa Pluggy + Taxa API) × Multiplicador
```

### Multiplicadores
- **Econômico**: 1.7x
- **Padrão**: 2.2x
- **Premium**: 3.5x (SLA 99%, suporte prioritário, reembolso garantido)

### Descontos Progressivos
- **5-20 números**: 5% OFF
- **21-100 números**: 12% OFF
- **100+ números**: 20% OFF

### Mínimo de Compra
R$ 5,00

### Conversão
1 crédito = R$ 1,00

## 🔐 Segurança

- ✅ Criptografia AES-256 para chaves sensíveis
- ✅ Validação HMAC de webhooks Pluggy
- ✅ Rate limiting por usuário/IP
- ✅ JWT para autenticação de APIs
- ✅ Idempotência para evitar duplicação
- ✅ Logs auditáveis em banco

## 📊 Fluxo de Funcionamento

### Compra de Créditos
1. Usuário envia `/comprar_creditos`
2. Escolhe pacote (Econômico/Padrão/Premium)
3. Informa valor (mín. R$ 5)
4. Bot gera cobrança PIX via Pluggy
5. Usuário paga via QR Code
6. Webhook Pluggy confirma pagamento
7. Créditos liberados automaticamente

### Compra SMS
1. Usuário envia `/comprar_sms`
2. Seleciona país e serviço
3. Bot reserva número via SMS-Activate
4. Polling automático aguarda SMS
5. Código enviado ao usuário
6. Se expirar, créditos devolvidos

### Compra Seguidores
1. Usuário envia `/comprar_seguidores`
2. Informa plataforma, quantidade e perfil
3. Bot cria pedido via Apex API
4. Créditos descontados
5. Webhook notifica conclusão

## 🛠️ Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Docker (opcional)

### Setup
```bash
# Clonar repositório
git clone https://github.com/SEU_USUARIO/telegram-sms-bot.git
cd telegram-sms-bot

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Copiar e configurar .env
cp .env.example .env
# Edite .env com suas credenciais

# Inicializar banco
psql -U postgres -d telegram_bot -f migrations/init.sql

# Rodar aplicação
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Com Docker
```bash
# Build e run
docker-compose up -d

# Verificar logs
docker-compose logs -f app

# Parar serviços
docker-compose down
```

## 📝 Comandos do Bot

| Comando | Descrição |
|---------|-----------|
| `/start` | Inicia o bot e mostra menu principal |
| `/comprar_creditos` | Comprar créditos via PIX |
| `/comprar_sms` | Adquirir número SMS descartável |
| `/comprar_seguidores` | Comprar seguidores para redes sociais |
| `/saldo` | Ver saldo, histórico e números ativos |
| `/ajuda` | Ajuda completa do bot |

## 🗃️ Estrutura do Banco

### Tabelas
- **users**: Usuários e saldos
- **orders**: Pedidos de créditos
- **sms_rents**: Aluguel de números SMS
- **followers_orders**: Pedidos de seguidores
- **logs**: Logs de sistema

## 🔍 Monitoramento

### Logs
```bash
# Ver logs da aplicação
tail -f app.log

# Ver logs do Docker
docker-compose logs -f app

# Ver logs do banco
docker-compose logs -f postgres
```

### Healthcheck
```bash
curl https://seu-app.up.railway.app/health
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- 📧 Email: suporte@seudominio.com
- 💬 Telegram: @seu_suporte_bot
- 📚 Documentação: [docs.seudominio.com](https://docs.seudominio.com)

## 🚨 Avisos Importantes

⚠️ **Nunca commite credenciais no repositório!**
⚠️ **Use `.env` para configurações sensíveis**
⚠️ **Ative 2FA em todas as contas de API**
⚠️ **Monitore logs regularmente**

---

**Desenvolvido com ❤️ para automação de vendas via Telegram**

🚀 **Deploy em produção em menos de 5 minutos!**
