#!/usr/bin/env python3
"""
Test script para verificar se o bot está funcionando
"""
import os
import requests
import sys

BOT_TOKEN = "8272365950:AAHbEBzucYLtYnBdKiYDyc3xLCcAMLUmRjw"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def test_bot_info():
    """Testa se o bot está acessível"""
    print("🤖 Testando informações do bot...")
    response = requests.get(f"{BASE_URL}/getMe")
    data = response.json()

    if data.get("ok"):
        bot = data["result"]
        print(f"✅ Bot encontrado: @{bot['username']}")
        print(f"   Nome: {bot['first_name']}")
        print(f"   ID: {bot['id']}")
        return True
    else:
        print(f"❌ Erro: {data}")
        return False

def test_webhook(domain):
    """Testa configuração do webhook"""
    print(f"\n📡 Testando webhook para: {domain}")
    response = requests.get(f"{BASE_URL}/getWebhookInfo")
    data = response.json()

    if data.get("ok"):
        info = data["result"]
        print(f"✅ Webhook configurado")
        print(f"   URL: {info.get('url', 'Não configurado')}")
        print(f"   Pending: {info.get('pending_update_count', 0)} mensagens")

        if info.get('last_error_message'):
            print(f"   ⚠️ Último erro: {info['last_error_message']}")
            return False
        return True
    else:
        print(f"❌ Erro: {data}")
        return False

def test_health(domain):
    """Testa endpoint de health"""
    print(f"\n🏥 Testando health endpoint...")
    try:
        response = requests.get(f"https://{domain}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Servidor respondendo: {response.json()}")
            return True
        else:
            print(f"❌ Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 Teste do Telegram SMS Bot")
    print("=" * 60)

    # Teste 1: Bot Info
    if not test_bot_info():
        sys.exit(1)

    # Pedir domínio
    print("\n" + "=" * 60)
    domain = input("Cole o domínio do Railway: ").strip()

    if not domain:
        print("❌ Domínio não pode ser vazio")
        sys.exit(1)

    # Teste 2: Health
    health_ok = test_health(domain)

    # Teste 3: Webhook
    webhook_ok = test_webhook(domain)

    # Resultado final
    print("\n" + "=" * 60)
    print("📊 Resultado dos Testes")
    print("=" * 60)
    print(f"Bot Info:    {'✅' if True else '❌'}")
    print(f"Health:      {'✅' if health_ok else '❌'}")
    print(f"Webhook:     {'✅' if webhook_ok else '❌'}")

    if health_ok and webhook_ok:
        print("\n🎉 Tudo funcionando! Bot está ONLINE!")
        print("\n📱 Teste agora no Telegram:")
        print("   1. Busque seu bot")
        print("   2. Envie /start")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique a configuração.")
        sys.exit(1)

if __name__ == "__main__":
    main()
