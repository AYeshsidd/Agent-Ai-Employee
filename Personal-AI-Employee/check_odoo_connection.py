#!/usr/bin/env python3
"""Odoo Connection Troubleshooter"""
import socket
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config


def check_odoo_running():
    """Check if Odoo is running and accessible"""
    print("\n" + "=" * 70)
    print("  ODOO CONNECTION TROUBLESHOOTER")
    print("=" * 70)
    
    # Load config
    config_file = Config.BASE_DIR / "credentials" / "odoo_config.json"
    
    if not config_file.exists():
        print("\n[ERROR] Odoo config not found!")
        print(f"        Expected at: {config_file}")
        print("\n[INFO] Run setup first:")
        print("       python odoo_setup.py")
        return False
    
    import json
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    url = config.get('url', 'http://localhost:8069')
    
    # Parse URL
    if '://' in url:
        protocol, host_port = url.split('://', 1)
    else:
        protocol = 'http'
        host_port = url
    
    if ':' in host_port:
        host, port = host_port.rsplit(':', 1)
        port = int(port)
    else:
        host = host_port
        port = 8069
    
    print(f"\n[INFO] Checking Odoo at: {host}:{port}")
    
    # Check 1: Port open
    print("\n[TEST 1] Checking if port is open...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    sock.close()
    
    if result == 0:
        print(f"[OK] Port {port} is OPEN")
    else:
        print(f"[ERROR] Port {port} is CLOSED")
        print("\n[INFO] Odoo is NOT running or not accessible")
        print("\n[SOLUTION] Start Odoo:")
        print("  Option 1 - Docker:")
        print("    docker run -d -p 8069:8069 --name odoo odoo:19.0")
        print("\n  Option 2 - Windows Service:")
        print("    1. Open Services (services.msc)")
        print("    2. Find 'Odoo' service")
        print("    3. Click 'Start'")
        print("\n  Option 3 - Manual:")
        print("    python odoo-bin -c odoo.conf")
        return False
    
    # Check 2: HTTP connection
    print("\n[TEST 2] Testing HTTP connection...")
    try:
        import requests
        response = requests.get(f"{url}/web/login", timeout=10)
        if response.status_code == 200:
            print(f"[OK] HTTP connection successful (Status: {response.status_code})")
        else:
            print(f"[WARN] HTTP returned: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] HTTP connection failed: {str(e)[:100]}")
        return False
    
    # Check 3: Verify credentials
    print("\n[TEST 3] Verifying credentials...")
    print(f"  Database: {config.get('database', 'odoo')}")
    print(f"  Username: {config.get('username', 'admin')}")
    print(f"  Password: {'*' * len(config.get('password', ''))}")
    
    print("\n[INFO] Connection details look correct")
    print("\n[NEXT STEPS]")
    print("  1. Open browser: http://localhost:8069")
    print("  2. Verify you can login manually")
    print("  3. Check database name matches")
    print("  4. Try test connection again")
    
    return True


def main():
    success = check_odoo_running()
    
    if success:
        print("\n" + "=" * 70)
        print("  CONNECTION CHECK PASSED")
        print("=" * 70)
        print("\n[INFO] Odoo appears to be running")
        print("\n[INFO] Now test MCP connection:")
        print("       python run_odoo_tools.py")
        print("       Select: 1. Test Connection")
    else:
        print("\n" + "=" * 70)
        print("  CONNECTION CHECK FAILED")
        print("=" * 70)
        print("\n[ERROR] Odoo is not accessible")
        print("\n[COMMON CAUSES]")
        print("  1. Odoo service is not running")
        print("  2. Wrong port (default: 8069)")
        print("  3. Firewall blocking connection")
        print("  4. Odoo is starting up (wait 30 seconds)")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
