#!/usr/bin/env python3
"""
TEST LOCAL
Zapusti etot skript, chtoby proverit, chto vse rabotaet PERED zagruzkoy na Render.

Ustanovka zavisimostey:
    pip install -r requirements.txt

Zapusk:
    export TELEGRAM_BOT_TOKEN='tvoy_token'
    export TELEGRAM_CHANNEL_ID='@tvoy_kanal'
    export GROQ_API_KEY='tvoy_klyuch'
    export BOT_MODE=once
    python test_local.py
"""

import os
import sys

# Proverka peremennykh okruzheniya
required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHANNEL_ID', 'GROQ_API_KEY']
missing = [v for v in required_vars if not os.getenv(v)]

if missing:
    print("OSIBKA! Ne zadany peremennye okruzheniya:")
    for v in missing:
        print(f"   - {v}")
    print("\nZaday ikh komandoy:")
    print("   export TELEGRAM_BOT_TOKEN='tvoy_token'")
    print("   export TELEGRAM_CHANNEL_ID='@tvoy_kanal'")
    print("   export GROQ_API_KEY='tvoy_klyuch'")
    sys.exit(1)

print("Vse peremennye okruzheniya zadany!")
print("Zapuskaem bota v testovom rezhime...\n")

# Zapuskaem osnovnoy skript
os.environ['BOT_MODE'] = 'once'
exec(open('main.py').read())
