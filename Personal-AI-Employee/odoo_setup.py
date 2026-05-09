#!/usr/bin/env python3
"""Odoo Setup - Configure connection and credentials"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config


def setup_odoo_config():
    """Create Odoo configuration file securely"""
    print("\n" + "=" * 70)
    print("  ODOO CONFIGURATION SETUP")
    print("=" * 70)
    
    config_file = Config.BASE_DIR / "credentials" / "odoo_config.json"
    
    # Ensure credentials directory exists
    config_file.parent.mkdir(exist_ok=True)
    
    print("\n[INFO] Enter your Odoo connection details:\n")
    
    # Get configuration from user
    url = input("Odoo URL (e.g., http://localhost:8069): ").strip()
    if not url:
        url = "http://localhost:8069"
    
    database = input("Database name: ").strip()
    if not database:
        database = "odoo"
    
    username = input("Username (e.g., admin): ").strip()
    if not username:
        username = "admin"
    
    password = input("Password: ").strip()
    if not password:
        print("\n[ERROR] Password is required")
        return False
    
    # Create config
    config = {
        "url": url,
        "database": database,
        "username": username,
        "password": password
    }
    
    # Save securely
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        # Set file permissions (Unix only)
        try:
            config_file.chmod(0o600)  # Read/write for owner only
        except:
            pass  # Windows doesn't support chmod
        
        print(f"\n[OK] Configuration saved to: {config_file}")
        print("\n[WARNING] This file contains sensitive credentials!")
        print("[WARNING] It is git-ignored and should never be committed.")
        
        # Test connection
        print("\n[INFO] Testing connection...")
        from odoo_mcp.connector import get_odoo_connector
        
        odoo = get_odoo_connector()
        if odoo.authenticate():
            print(f"[OK] Connected successfully! (UID: {odoo.uid})")
        else:
            print("[WARN] Connection test failed. Check credentials.")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Failed to save configuration: {str(e)}")
        return False


def main():
    """Main entry point"""
    success = setup_odoo_config()
    
    if success:
        print("\n" + "=" * 70)
        print("  SETUP COMPLETE")
        print("=" * 70)
        print("\n[INFO] You can now use Odoo MCP tools:")
        print("  - python run_odoo_tools.py")
        print("  - Access via MCP Server: odoo_* tools")
        print("\n[INFO] Available operations:")
        print("  - Create invoices")
        print("  - Register payments")
        print("  - Manage expenses")
        print("  - Create/search partners")
        print("  - Get accounting summary")
        print("=" * 70 + "\n")
    else:
        print("\n[ERROR] Setup failed. Please try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
