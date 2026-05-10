#!/usr/bin/env python3
"""Run Odoo MCP Tools - Test and Demo"""
import sys
from pathlib import Path

# Robust project root detection
root = Path(__file__).resolve().parent
while root.name != "Personal-AI-Employee" and root.parent != root:
    root = root.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from odoo_mcp.odoo_module import OdooModule


def test_connection():
    """Test Odoo connection"""
    print("\n" + "=" * 70)
    print("  TESTING ODOO CONNECTION")
    print("=" * 70)
    
    module = OdooModule()
    result = module.execute("odoo_test_connection", {})
    
    print(f"\nResult: {result}")
    return result.get('status') == 'success'


def get_summary():
    """Get accounting summary"""
    print("\n" + "=" * 70)
    print("  ACCOUNTING SUMMARY")
    print("=" * 70)
    
    module = OdooModule()
    result = module.execute("odoo_get_summary", {})
    
    if result.get('status') == 'success':
        summary = result.get('summary', {})
        print(f"\nTotal Receivables: ${summary.get('total_receivables', 0):,.2f}")
        print(f"Total Payables: ${summary.get('total_payables', 0):,.2f}")
        print(f"Customer Invoices: {summary.get('customer_invoices', 0)}")
        print(f"Vendor Bills: {summary.get('vendor_bills', 0)}")
    else:
        print(f"\nError: {result.get('message')}")


def create_test_invoice():
    """Create a test invoice"""
    print("\n" + "=" * 70)
    print("  CREATE TEST INVOICE")
    print("=" * 70)
    
    module = OdooModule()
    
    # First, create a test partner
    print("\n[INFO] Creating test partner...")
    partner_result = module.execute("odoo_create_partner", {
        "name": "Test Customer",
        "email": "test@example.com",
        "is_customer": True
    })
    
    if partner_result.get('status') == 'success':
        partner_id = partner_result.get('partner_id')
        print(f"[OK] Partner created: ID {partner_id}")
        
        # Create invoice
        print("\n[INFO] Creating invoice...")
        invoice_result = module.execute("odoo_create_invoice", {
            "partner_id": partner_id,
            "invoice_lines": [
                {
                    "name": "Consulting Services",
                    "quantity": 1,
                    "price_unit": 1000.00
                }
            ],
            "invoice_date": "2026-03-22"
        })
        
        print(f"\nResult: {invoice_result}")
    else:
        print(f"\nError: {partner_result.get('message')}")


def list_invoices():
    """List recent invoices"""
    print("\n" + "=" * 70)
    print("  RECENT INVOICES")
    print("=" * 70)
    
    module = OdooModule()
    result = module.execute("odoo_list_invoices", {"limit": 5})
    
    if result.get('status') == 'success':
        invoices = result.get('invoices', [])
        if invoices:
            for inv in invoices:
                print(f"\n- {inv.get('name')}: ${inv.get('amount_total', 0):,.2f} "
                      f"({inv.get('state', 'draft')})")
        else:
            print("\n[INFO] No invoices found")
    else:
        print(f"\nError: {result.get('message')}")


def interactive_mode():
    """Interactive menu"""
    print("\n" + "=" * 70)
    print("  ODOO MCP TOOLS - INTERACTIVE MODE")
    print("=" * 70)
    
    module = OdooModule()
    
    while True:
        print("\nSelect operation:")
        print("1. Test Connection")
        print("2. Accounting Summary")
        print("3. List Invoices")
        print("4. Create Test Invoice")
        print("5. Search Partner")
        print("6. Create Expense")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-6): ").strip()
        
        if choice == '1':
            test_connection()
        elif choice == '2':
            get_summary()
        elif choice == '3':
            list_invoices()
        elif choice == '4':
            create_test_invoice()
        elif choice == '5':
            name = input("Enter partner name to search: ").strip()
            result = module.execute("odoo_search_partner", {"name": name})
            print(f"\nResult: {result}")
        elif choice == '6':
            try:
                product_id = int(input("Product ID: ").strip())
                amount = float(input("Amount: ").strip())
                desc = input("Description: ").strip()
                result = module.execute("odoo_create_expense", {
                    "product_id": product_id,
                    "amount": amount,
                    "description": desc
                })
                print(f"\nResult: {result}")
            except ValueError as e:
                print(f"\n[ERROR] Invalid input: {e}")
        elif choice == '0':
            print("\n[INFO] Exiting...")
            break
        else:
            print("\n[ERROR] Invalid choice")


def main():
    print("\n" + "=" * 70)
    print("  ODOO MCP TOOLS")
    print("=" * 70)
    
    print("\nSelect mode:")
    print("1. Interactive Mode")
    print("2. Quick Test (Connection + Summary)")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == '1':
        interactive_mode()
    elif choice == '2':
        if test_connection():
            get_summary()
    else:
        print("[ERROR] Invalid choice")


if __name__ == "__main__":
    main()
