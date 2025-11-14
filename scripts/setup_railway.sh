#!/bin/bash

# Railway Setup Script
echo "🚂 Configurando projeto no Railway..."

# 1. Instalar Railway CLI
echo "📦 Instalando Railway CLI..."
npm i -g @railway/cli

# 2. Login
echo "🔐 Faça login no Railway..."
railway login

# 3. Criar projeto
echo "🎯 Criando projeto..."
railway init

# 4. Link com GitHub
echo "🔗 Conectando com GitHub..."
railway link

# 5. Adicionar PostgreSQL
echo "🗄️ Adicionando PostgreSQL..."
railway add --database postgres

# 6. Deploy
echo "🚀 Fazendo deploy..."
railway up

echo "✅ Setup completo! Acesse: railway open"
