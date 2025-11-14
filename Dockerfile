# Use Python 3.11 (compatível com todas as dependências)
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (para cache de build)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código
COPY . .

# Expor porta (Railway vai definir a variável PORT)
EXPOSE 8000

# Comando de inicialização
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
