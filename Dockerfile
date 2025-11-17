# Multi-stage build para otimizar tamanho da imagem
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependências de build
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage final
FROM python:3.11-slim

WORKDIR /app

# Copiar dependências do builder
COPY --from=builder /root/.local /root/.local

# Adicionar ao PATH
ENV PATH=/root/.local/bin:$PATH

# Copiar código da aplicação
COPY app ./app
COPY .env.example .env

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
