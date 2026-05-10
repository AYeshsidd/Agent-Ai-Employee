#!/usr/bin/env python3
"""Test Odoo Authentication - Debug Tool"""
import json
import requests
from pathlib import Path
import sys

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from config import Config

# Load config
config_file = Config.BASE_DIR / "credentials" / "odoo_config.json"
with open(config_file, 'r') as f:
    config = json.load(f)

url = config.get('url', 'http://localhost:8069')
db = config.get('database', 'myodoo')
username = config.get('username', 'admin')
password = config.get('password', 'admin')

print("\n" + "=" * 70)
print("  ODOO AUTHENTICATION DEBUG")
print("=" * 70)
print(f"\nTesting connection to: {url}")
print(f"Database: {db}")
print(f"Username: {username}")
print(f"Password: {'*' * len(password)}")

# Test 1: Basic connectivity
print("\n[TEST 1] Basic HTTP connectivity...")
try:
    response = requests.get(f"{url}/web/login", timeout=5)
    print(f"[OK] HTTP Status: {response.status_code}")
except Exception as e:
    print(f"[ERROR] HTTP failed: {e}")
    sys.exit(1)

# Test 2: Try Odoo 19 authentication method 1
print("\n[TEST 2] Authentication Method 1 (Odoo 19+)...")
payload1 = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "db": db,
        "login": username,
        "password": password,
        "context": {}
    },
    "id": 1
}

try:
    response = requests.post(
        f"{url}/web/session/authenticate",
        json=payload1,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('result', {}).get('uid'):
        print(f"[SUCCESS] Authenticated! UID: {result['result']['uid']}")
        sys.exit(0)
    else:
        print("[FAILED] Method 1 failed")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 3: Try common authentication method
print("\n[TEST 3] Authentication Method 2 (Common)...")
payload2 = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",
        "method": "authenticate",
        "args": [db, username, password, {}]
    },
    "id": 2
}

try:
    response = requests.post(
        f"{url}/web/session/authenticate",
        json=payload2,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('result', {}).get('uid'):
        print(f"[SUCCESS] Authenticated! UID: {result['result']['uid']}")
        sys.exit(0)
    else:
        print("[FAILED] Method 2 failed")
except Exception as e:
    print(f"[ERROR] {e}")

# Test 4: Try login endpoint
print("\n[TEST 4] Direct login endpoint...")
try:
    session = requests.Session()
    login_data = {
        'db': db,
        'login': username,
        'password': password
    }
    response = session.post(
        f"{url}/web/login",
        data=login_data,
        timeout=10
    )
    print(f"Response Status: {response.status_code}")
    print(f"Final URL: {response.url}")
    
    if 'web' in response.url or response.status_code == 200:
        print("[SUCCESS] Login via web endpoint!")
        sys.exit(0)
    else:
        print("[FAILED] Web login failed")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 70)
print("  ALL METHODS FAILED")
print("=" * 70)
print("\n[INFO] Possible issues:")
print("  1. Wrong username (should be your email)")
print("  2. Wrong password")
print("  3. Wrong database name")
print("  4. Odoo version incompatibility")
print("\n[INFO] Verify credentials by logging in via browser:")
print(f"       {url}/web/login")
print("=" * 70 + "\n")
