# 🤖 Telegram SMS Bot - Sistema Autônomo de Venda de Créditos

Bot Telegram completo para venda de créditos SMS descartáveis (SMS-Activate) e seguidores (Apex Seguidores) com pagamento automático via PIX (PixIntegra).

## 📋 Índice

- [Características](#características)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Fluxos de Negócio](#fluxos-de-negócio)
- [Segurança](#segurança)
- [Deploy](#deploy)
- [Troubleshooting](#troubleshooting)

---

## ✨ Características

### 🎯 Funcionalidades Principais

- ✅ **Pagamento PIX Automático**: Integração completa com PixIntegra
- ✅ **Números SMS Descartáveis**: Via API SMS-Activate
- ✅ **Compra de Seguidores**: Integração com Apex Seguidores
- ✅ **Sistema de Créditos**: Conversão automática BRL → Créditos
- ✅ **3 Planos de Preço**: Econômico, Padrão e Premium
- ✅ **Descontos Progressivos**: 5%, 12% e 20% conforme volume
- ✅ **Webhook Seguro**: HMAC SHA256 + Idempotência
- ✅ **Rate Limiting**: Proteção contra abuso
- ✅ **Logs Auditáveis**: Registro completo de transações
- ✅ **Retry Automático**: Polling inteligente para códigos SMS

### 💰 Estratégia de Precificação

**Fórmula**: `(custo_base + taxa_pixintegra) × margem`

| Pacote | Margem | Descrição |
|--------|--------|-----------|
| 💚 Econômico | ×1.7 | Uso básico |
| 🔵 Padrão | ×2.2 | Melhor custo-benefício |
| 🟡 Premium | ×3.5 | SLA 99% + Suporte prioritário |

**Descontos SMS**:
- 5-20 números: **5% OFF**
- 21-100 números: **12% OFF**
- 100+ números: **20% OFF**

**Mínimo de compra**: R$ 5,00

---

## 🏗 Arquitetura

```
┌─────────────────┐
│  Telegram Bot   │
│   (Usuário)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│      FastAPI Application        │
│  ┌───────────────────────────┐  │
│  │   Telegram Handlers       │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │   Business Logic Layer    │  │
│  │  • Pricing Service        │  │
│  │  • PixIntegra Client      │  │
│  │  • SMS-Activate Client    │  │
│  │  • Apex Seguidores Client │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │    Security & Utils       │  │
│  │  • HMAC Validation        │  │
│  │  • Idempotency Manager    │  │
│  │  • Encryption             │  │
│  └───────────┬───────────────┘  │
└──────────────┼───────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌──────────┐        ┌──────────┐
│PostgreSQL│        │  Redis   │
│  (Dados) │        │ (Cache)  │
└──────────┘        └──────────┘

External APIs:
• PixIntegra (Pagamentos PIX)
• SMS-Activate (Números SMS)
• Apex Seguidores (Seguidores)
```

---

## 🛠 Tecnologias

- **Backend**: Python 3.11 + FastAPI
- **Banco de Dados**: PostgreSQL 15
- **Cache/Idempotência**: Redis 7
- **Bot Framework**: python-telegram-bot 20+
- **ORM**: SQLAlchemy 2.0 (async)
- **Validação**: Pydantic
- **Logs**: structlog
- **Containerização**: Docker + Docker Compose
- **Segurança**: Cryptography, python-jose (JWT)

---

## 🚀 Instalação

### Pré-requisitos

- Docker 24+ e Docker Compose
- Python 3.11+ (para desenvolvimento local)
- PostgreSQL 15+
- Redis 7+

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-repo/telegram-sms-bot.git
cd telegram-sms-bot
```

### 2. Configure as Variáveis de Ambiente

```bash
cp .env.example .env
nano .env
```

**Variáveis obrigatórias**:

```env
# Telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_WEBHOOK_URL=https://seudominio.com/telegram/webhook
TELEGRAM_WEBHOOK_SECRET=gerar_secret_aleatorio

# PixIntegra
PIXINTEGRA_API_TOKEN=apitoken_fa6243cb521dbfaa0d6962661b82b8f8308e100101a934
PIXINTEGRA_WEBHOOK_SECRET=gerar_secret_aleatorio

# SMS-Activate
SMS_ACTIVATE_API_KEY=sua_api_key_sms_activate

# Apex Seguidores
APEX_API_KEY=sua_api_key_apex

# Security (gerar com: openssl rand -hex 32)
JWT_SECRET_KEY=sua_secret_key_jwt
ENCRYPTION_KEY=sua_encryption_key_32_bytes_base64
```

### 3. Gerar Chaves de Segurança

```bash
# JWT Secret
openssl rand -hex 32

# Encryption Key (Fernet)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 4. Iniciar com Docker Compose

```bash
docker-compose up -d
```

Isso irá iniciar:
- API FastAPI (porta 8000)
- PostgreSQL (porta 5432)
- Redis (porta 6379)
- PgAdmin (porta 5050)

### 5. Verificar Saúde

```bash
curl http://localhost:8000/health
```

---

## ⚙️ Configuração

### Criar Bot no Telegram

1. Abra [@BotFather](https://t.me/botfather) no Telegram
2. Envie `/newbot`
3. Escolha nome e username
4. Copie o token fornecido para `TELEGRAM_BOT_TOKEN`

### Configurar Webhook do Telegram

```bash
curl -X POST "https://api.telegram.org/bot<SEU_TOKEN>/setWebhook"   -H "Content-Type: application/json"   -d '{"url": "https://seudominio.com/telegram/webhook", "secret_token": "seu_webhook_secret"}'
```

### Obter API Keys

#### PixIntegra
1. Acesse [PixIntegra](https://pixintegra.com.br)
2. Cadastre-se e obtenha API token
3. Configure webhook URL no painel

#### SMS-Activate
1. Acesse [SMS-Activate](https://sms-activate.org)
2. Cadastre-se e adicione saldo
3. Gere API key em "API"

#### Apex Seguidores
1. Contate Apex Seguidores para API access
2. Obtenha credenciais e documentação

---

## 📱 Uso

### Comandos do Bot

| Comando | Descrição |
|---------|-----------|
| `/start` | Inicia o bot e cria usuário |
| `/help` | Mostra ajuda completa |
| `/saldo` | Consulta saldo atual |
| `/comprar_creditos` | Adiciona créditos via PIX |
| `/comprar_sms` | Aluga número SMS |
| `/comprar_seguidores` | Compra seguidores |
| `/historico` | Histórico de transações |

### Fluxo de Compra de Créditos

1. Usuário: `/comprar_creditos`
2. Bot: Mostra pacotes (Econômico, Padrão, Premium)
3. Usuário: Seleciona pacote
4. Bot: Solicita valor (mín. R$ 5,00)
5. Usuário: Envia valor
6. Bot: Gera QR Code PIX via PixIntegra
7. Usuário: Paga via PIX
8. **PixIntegra → Webhook → Bot credita automaticamente**
9. Bot: Notifica usuário do crédito

### Fluxo de Compra SMS

1. Usuário: `/comprar_sms`
2. Bot: Mostra serviços (WhatsApp, Telegram, Google, etc)
3. Usuário: Seleciona serviço
4. Bot: Chama SMS-Activate `getNumber`
5. Bot: Envia número ao usuário
6. **Polling automático** (10 min) aguardando SMS
7. Ao receber: Bot envia código
8. Se timeout: **Reembolso automático**

---

## 🔌 API Endpoints

### Webhook PixIntegra

**POST** `/pixintegra/webhook`

Recebe confirmações de pagamento do PixIntegra.

**Headers**:
```
X-Signature: <hmac_sha256_signature>
Content-Type: application/json
```

**Payload**:
```json
{
  "charge_id": "chg_abc123",
  "status": "paid",
  "paid_amount": 50.00,
  "paid_at": "2025-11-17T10:30:00Z"
}
```

**Response**:
```json
{
  "message": "Payment processed",
  "order_id": 123,
  "credits_added": 50.00,
  "new_balance": 150.00
}
```

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "environment": "production"
}
```

---

## 🔄 Fluxos de Negócio

### 1. Processamento de Pagamento (com Idempotência)

```python
# Webhook PixIntegra
1. Validar HMAC signature
2. Verificar idempotência (Redis)
   - Se já processado: retornar resultado anterior
   - Senão: criar lock
3. Buscar Order no banco
4. Atualizar status → PAID
5. Creditar User.balance
6. Marcar como completado (Redis)
7. Enviar notificação Telegram
8. Retornar sucesso
```

### 2. Polling SMS (com Auto-Reembolso)

```python
# Background task
1. Criar SMSRent (status=PENDING)
2. Chamar SMS-Activate getNumber
3. Atualizar com phone_number (status=ACTIVE)
4. Loop polling (max 60x, interval 10s):
   - Chamar getStatus
   - Se STATUS_OK: extrair código, atualizar DB, notificar usuário
   - Se STATUS_CANCEL: break
5. Se timeout:
   - Chamar setStatus(8) para cancelar
   - Reembolsar créditos ao User.balance
   - Atualizar status=EXPIRED
```

---

## 🔒 Segurança

### Implementações

✅ **HMAC SHA256**: Validação de webhooks PixIntegra  
✅ **Idempotência**: Redis com TTL para prevenir double-processing  
✅ **Rate Limiting**: 10 req/min por usuário  
✅ **Criptografia**: Fernet para dados sensíveis  
✅ **JWT**: Tokens para APIs internas (se necessário)  
✅ **SQL Injection**: Proteção via SQLAlchemy ORM  
✅ **Logs Auditáveis**: Todas transações registradas  

### Validação de Webhook

```python
def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)
```

### Idempotência

```python
# Check and lock
can_process = await idempotency_manager.check_and_lock(
    key=f"payment_{charge_id}",
    ttl_seconds=300
)

if not can_process:
    # Já processando ou processado
    return cached_result
```

---

## 🚢 Deploy

### Deploy em Produção (Docker)

1. **Configure domínio e SSL**:
   ```bash
   # Nginx reverse proxy com Let's Encrypt
   sudo apt install nginx certbot python3-certbot-nginx
   sudo certbot --nginx -d seudominio.com
   ```

2. **Configure variáveis de produção**:
   ```env
   ENVIRONMENT=production
   DEBUG=false
   DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/bot
   ```

3. **Inicie os containers**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Configure webhook do Telegram**:
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook"      -d "url=https://seudominio.com/telegram/webhook"
   ```

### Monitoramento

- **Logs**: `docker-compose logs -f api`
- **Métricas**: Integrar Prometheus + Grafana
- **Alertas**: Configurar alertas para erros críticos

---

## 🐛 Troubleshooting

### Problema: Webhook PixIntegra não funciona

**Solução**:
1. Verificar logs: `docker-compose logs api`
2. Testar assinatura HMAC localmente
3. Confirmar URL do webhook no painel PixIntegra
4. Verificar firewall/porta 8000 acessível

### Problema: SMS-Activate retorna NO_NUMBERS

**Solução**:
- Tentar outro país/serviço
- Verificar disponibilidade na API
- Implementar fallback para serviços similares

### Problema: Saldo não creditado após pagamento

**Solução**:
1. Verificar logs do webhook
2. Consultar Order no banco: `SELECT * FROM orders WHERE pixintegra_charge_id = 'xxx'`
3. Verificar idempotência no Redis: `redis-cli GET idempotency:pixintegra_payment_xxx`
4. Reprocessar manualmente se necessário

### Problema: Bot não responde

**Solução**:
1. Verificar token do bot: `curl https://api.telegram.org/bot<TOKEN>/getMe`
2. Confirmar webhook configurado: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
3. Reiniciar aplicação: `docker-compose restart api`

---

## 📊 Estrutura do Banco de Dados

### Tabelas

- **users**: Usuários do Telegram
- **orders**: Pedidos de compra de créditos
- **sms_rents**: Aluguéis de números SMS
- **followers_orders**: Pedidos de seguidores
- **logs**: Logs de auditoria

### Migrations

```bash
# Criar migration
docker-compose exec api alembic revision --autogenerate -m "initial"

# Aplicar migrations
docker-compose exec api alembic upgrade head
```

---

## 📝 Licença

MIT License - Veja LICENSE para detalhes.

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-repo/issues)
- **Email**: suporte@seudominio.com
- **Telegram**: @seu_suporte_bot

---

**Desenvolvido com ❤️ usando FastAPI + Telegram Bot API**
