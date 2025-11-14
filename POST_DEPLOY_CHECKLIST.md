# ✅ Checklist Pós-Deploy

## 🚀 Após o Deploy Completar

### 1. ✅ Verificar Build
- [ ] Build completou sem erros
- [ ] Railway mostra status "Active"
- [ ] Logs não mostram erros críticos

### 2. ✅ Verificar Domínio
- [ ] Domínio foi gerado automaticamente
- [ ] Copiou o domínio (ex: `telegram-sms-bot-production.up.railway.app`)
- [ ] Health endpoint responde: `https://seu-dominio.up.railway.app/health`

### 3. ✅ Atualizar Variável
- [ ] Editou `TELEGRAM_WEBHOOK_URL` com o domínio correto
- [ ] Formato: `https://seu-dominio.up.railway.app/webhook/telegram`
- [ ] Salvou as alterações no Railway

### 4. ✅ Configurar Webhook
Execute UM dos comandos abaixo:

**Opção A - Script Automático (Recomendado):**
```bash
curl -o post_deploy.sh https://raw.githubusercontent.com/popovidismarcoantonionista-lang/telegram-sms-bot/main/scripts/post_deploy.sh
chmod +x post_deploy.sh
./post_deploy.sh
```

**Opção B - Manual:**
```bash
# Substitua SEU-DOMINIO
curl -X POST "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/setWebhook?url=https://SEU-DOMINIO.up.railway.app/webhook/telegram"
```

### 5. ✅ Testar Bot
- [ ] Abriu o Telegram
- [ ] Buscou o bot pelo username
- [ ] Enviou `/start`
- [ ] Bot respondeu com mensagem de boas-vindas

### 6. ✅ Testar Funcionalidades

**Comandos básicos:**
- [ ] `/start` - Iniciar bot
- [ ] `/saldo` - Ver saldo (deve mostrar R$ 0,00)
- [ ] `/comprar_creditos` - Mostrar planos
- [ ] `/ajuda` - Mostrar ajuda

**Fluxo de compra (se tiver PIX de teste):**
- [ ] `/comprar_creditos` → Escolher plano → Enviar valor
- [ ] Receber QR Code PIX
- [ ] (Pagar e verificar crédito automático)

### 7. ✅ Configurações Adicionais

**PixIntegra Webhook:**
- [ ] Acessar: https://dashboard.pixintegra.com.br
- [ ] Configurar webhook: `https://seu-dominio.up.railway.app/webhook/pixintegra`
- [ ] Secret: `AmvmPouOg!KV@d9vF6*TYy4Qth7crsad`
- [ ] Eventos: `charge.paid`, `charge.expired`, `charge.cancelled`

**SMS-Activate:**
- [ ] Verificar chave configurada: `fdc8b17A0d37f586b31f7fef44A04263`
- [ ] Adicionar saldo (mínimo $10): https://sms-activate.org/

### 8. ✅ Monitoramento

**Railway Dashboard:**
- [ ] Verificar métricas (CPU, RAM, Network)
- [ ] Configurar alertas se necessário
- [ ] Revisar logs em busca de erros

**Testes Periódicos:**
```bash
# Health check
curl https://seu-dominio.up.railway.app/health

# Webhook status
curl "https://api.telegram.org/bot8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw/getWebhookInfo"
```

## 🎉 Deploy Completo!

Se todos os itens estão marcados ✅, seu bot está **100% operacional**!

## 📊 Métricas Esperadas

- **Tempo de resposta**: < 500ms
- **Uptime**: 99.9%
- **Webhook latency**: < 200ms
- **Database queries**: < 100ms

## 🆘 Troubleshooting

### Bot não responde no Telegram
1. Verifique webhook: `curl "https://api.telegram.org/bot.../getWebhookInfo"`
2. Verifique logs: Railway Dashboard → Logs
3. Teste health: `curl https://seu-dominio.up.railway.app/health`

### Erro "Connection refused"
1. Aguarde 30-60 segundos após deploy
2. Verifique se o build completou
3. Verifique variáveis de ambiente

### Webhook não recebe atualizações
1. Remova webhook: `curl -X POST "https://api.telegram.org/bot.../deleteWebhook"`
2. Configure novamente com domínio correto
3. Verifique se Railway não está em "sleep mode"

## 📝 Próximos Passos

1. **Adicionar saldo SMS-Activate**: $10+ para testes
2. **Testar PIX**: Use ambiente de teste da PixIntegra
3. **Divulgar bot**: Compartilhe com usuários
4. **Monitorar**: Acompanhe logs e métricas
5. **Escalar**: Se necessário, upgrade Railway plan

## 🔗 Links Úteis

- **Repositório**: https://github.com/popovidismarcoantonionista-lang/telegram-sms-bot
- **Railway Dashboard**: https://railway.app/dashboard
- **PixIntegra**: https://dashboard.pixintegra.com.br
- **SMS-Activate**: https://sms-activate.org/
- **Apex Seguidores**: https://apexseguidores.com/

---

**✨ Seu bot está pronto para produção!** 🚀
