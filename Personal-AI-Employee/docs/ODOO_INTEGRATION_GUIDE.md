# Odoo Accounting Integration - Complete Guide

## Branch: `feature/odoo-accounting-integration`

## Overview

This integration connects the Autonomous FTE system with **self-hosted Odoo Community Edition** (v19+) via JSON-RPC API, enabling automated accounting operations through MCP tools.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              ODOO INTEGRATION ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Needs_Action    │────▶│  Odoo MCP        │────▶│  Odoo ERP    │
│  Tasks           │     │  Server          │     │  (Local)     │
│                  │     │                  │     │              │
│ - Invoice tasks  │     │ - JSON-RPC API   │     │ - Invoices   │
│ - Payment tasks  │     │ - Authentication │     │ - Payments   │
│ - Expense tasks  │     │ - Operations     │     │ - Expenses   │
└──────────────────┘     └──────────────────┘     └──────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                    BronzeLogger (Audit Trail)                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
Bronze-tier/
├── odoo_mcp/                          # Odoo MCP Package
│   ├── __init__.py
│   ├── connector.py                   # Odoo JSON-RPC connector
│   ├── accounting.py                  # Accounting operations
│   └── odoo_module.py                 # MCP module definition
│
├── odoo_setup.py                      # Initial setup & configuration
├── run_odoo_tools.py                  # Test & demo tools
├── odoo_task_integration.py           # Needs_Action integration
│
├── credentials/
│   └── odoo_config.json              # Odoo credentials (git-ignored)
│
└── logs/
    └── bronze_tier.log                # Odoo operations logged
```

---

## Installation & Setup

### Step 1: Install Odoo Community Edition

**Option A: Docker (Recommended)**
```bash
docker run -d -p 8069:8069 --name odoo -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres odoo:19.0
```

**Option B: Local Installation**
1. Download from: https://www.odoo.com/page/download
2. Install on your system
3. Access at: http://localhost:8069

### Step 2: Configure Odoo Connection

```bash
cd Bronze-tier
python odoo_setup.py
```

**Enter your details:**
```
Odoo URL: http://localhost:8069
Database name: odoo
Username: admin
Password: [your password]
```

**Configuration saved to:** `credentials/odoo_config.json`

### Step 3: Test Connection

```bash
python run_odoo_tools.py
# Select: 2. Quick Test
```

---

## MCP Tools Available

### Invoices

| Tool | Description | Parameters |
|------|-------------|------------|
| `odoo_create_invoice` | Create customer invoice | partner_id, invoice_lines, invoice_date, due_date |
| `odoo_get_invoice` | Get invoice details | invoice_id |
| `odoo_list_invoices` | List invoices | partner_id, state, limit |
| `odoo_validate_invoice` | Post/validate invoice | invoice_id |

### Payments

| Tool | Description | Parameters |
|------|-------------|------------|
| `odoo_register_payment` | Register payment | invoice_id, amount, payment_date |

### Expenses

| Tool | Description | Parameters |
|------|-------------|------------|
| `odoo_create_expense` | Create expense | product_id, amount, description, date |
| `odoo_list_expenses` | List expenses | employee_id, state, limit |

### Partners

| Tool | Description | Parameters |
|------|-------------|------------|
| `odoo_create_partner` | Create customer/vendor | name, email, phone, is_customer, is_vendor |
| `odoo_search_partner` | Search partners | name, email |

### Reports

| Tool | Description |
|------|-------------|
| `odoo_get_summary` | Get accounting summary (receivables, payables) |
| `odoo_test_connection` | Test Odoo connection |

---

## Usage Examples

### Via MCP Server

```python
from mcp_server import get_server

server = get_server()

# Create invoice
result = server.call_tool("odoo_create_invoice", {
    "partner_id": 1,
    "invoice_lines": [
        {
            "name": "Consulting Services",
            "quantity": 1,
            "price_unit": 1000.00
        }
    ],
    "invoice_date": "2026-03-22"
})

# Register payment
result = server.call_tool("odoo_register_payment", {
    "invoice_id": 5,
    "amount": 1000.00,
    "payment_date": "2026-03-22"
})

# Get summary
result = server.call_tool("odoo_get_summary", {})
```

### Via Command Line

```bash
# Interactive mode
python run_odoo_tools.py

# Process task from Needs_Action
python odoo_task_integration.py 20260322_Create_Invoice.md
```

### Via Needs_Action Integration

**Create task file:** `Vault/Needs_Action/Create_Invoice_For_Client.md`

```markdown
# Create Invoice for Client

**Priority**: High

## Odoo Operation

Create Invoice

## Details

- **Partner ID**: 1
- **Amount**: 1500.00
- **Description**: Web Development Services
- **Due Date**: 2026-04-22

## Action Items

- [ ] Create invoice in Odoo
```

**Run integration:**
```bash
python odoo_task_integration.py Create_Invoice_For_Client.md
```

---

## Workflow: Task → Odoo → Done

```
1. Task created in Needs_Action
   │
   ▼
2. Task contains Odoo operation keywords
   │
   ▼
3. Run: python odoo_task_integration.py <task_file>
   │
   ▼
4. Integration detects operation type
   │
   ▼
5. Executes Odoo MCP tool
   │
   ▼
6. Updates task with result
   │
   ▼
7. Moves task to Done folder
   │
   ▼
8. Logged in bronze_tier.log
```

---

## Security

### Credentials Protection

| File | Protection |
|------|------------|
| `credentials/odoo_config.json` | Git-ignored, owner-only permissions |
| `credentials/*.json` | All credential files git-ignored |
| Logs | No passwords logged |

### Best Practices

1. **Never commit** `odoo_config.json`
2. **Use environment variables** in production
3. **Restrict Odoo user permissions** to minimum required
4. **Enable Odoo audit logs** for compliance
5. **Use HTTPS** for remote Odoo instances

---

## Odoo Model Reference

### account.move (Invoices/Bills)
```python
# Create invoice
odoo.create('account.move', {
    'move_type': 'out_invoice',  # or 'in_invoice' for bills
    'partner_id': 1,
    'invoice_line_ids': [(0, 0, {
        'name': 'Service',
        'quantity': 1,
        'price_unit': 1000.00
    })]
})
```

### account.payment (Payments)
```python
# Register payment
odoo.execute('account.move', 'action_register_payment', [invoice_id])
```

### hr.expense (Expenses)
```python
# Create expense
odoo.create('hr.expense', {
    'product_id': 1,
    'total_amount': 100.00,
    'name': 'Travel Expense'
})
```

### res.partner (Customers/Vendors)
```python
# Create partner
odoo.create('res.partner', {
    'name': 'Company Name',
    'email': 'contact@company.com',
    'customer_rank': 1,  # Mark as customer
    'supplier_rank': 1   # Mark as vendor
})
```

---

## Testing

### Run Test Suite

```bash
cd Bronze-tier
python run_odoo_tools.py
# Select: 1. Interactive Mode
# Test each operation
```

### Verify Connection

```bash
python -c "
from odoo_mcp.odoo_module import OdooModule
module = OdooModule()
result = module.execute('odoo_test_connection', {})
print(result)
"
```

### Expected Output
```
{'status': 'success', 'message': 'Connected to Odoo (UID: 2)'}
```

---

## Troubleshooting

### Connection Failed

**Error:** `Connection refused`
**Solution:**
1. Check if Odoo is running: `http://localhost:8069`
2. Verify URL in `credentials/odoo_config.json`
3. Check firewall settings

### Authentication Failed

**Error:** `Authentication failed - invalid credentials`
**Solution:**
1. Verify database name
2. Check username/password
3. Re-run `python odoo_setup.py`

### Operation Failed

**Error:** `Odoo API Error: ...`
**Solution:**
1. Check user permissions in Odoo
2. Verify required fields are provided
3. Check Odoo logs for details

---

## Audit & Compliance

### Logged Operations

All Odoo operations are logged to:
- `logs/bronze_tier.log`
- Task files (result section)
- Odoo's native audit trail

### Sample Log Entry
```
2026-03-22 14:30:00 - OdooAccounting - INFO - [SKILL] OdooAccounting | 
Operation: create_customer_invoice | Status: SUCCESS | Details: Invoice created: 42
```

---

## Future Enhancements

### Planned Features
- [ ] Automated invoice generation from tasks
- [ ] Payment reconciliation automation
- [ ] Financial report generation
- [ ] Multi-company support
- [ ] Odoo.sh deployment guide
- [ ] Webhook integration for real-time sync

### Integration Possibilities
- Gmail watcher → Auto-create vendor bills
- LinkedIn auto-post → Track marketing expenses
- Twitter auto-post → Track social media costs
- Approval system → Invoice approval workflow

---

## Summary

✅ **Odoo Connector** - JSON-RPC API client
✅ **Accounting Operations** - Invoices, payments, expenses
✅ **MCP Integration** - 11 Odoo tools available
✅ **Task Integration** - Needs_Action → Odoo → Done
✅ **Security** - Credentials protected, git-ignored
✅ **Documentation** - Complete setup & usage guide
✅ **Testing** - Interactive test tools included

**Status:** Production-ready for self-hosted Odoo Community Edition 19+
