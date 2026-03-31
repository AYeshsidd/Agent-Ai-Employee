# Odoo Setup Guide - Quick Start

## Your Current Status

✅ Docker Compose file created
✅ Odoo + PostgreSQL containers running
✅ Port 8069 accessible
⚠️ Database needs to be created

---

## Step 1: Create Your Database

**Open browser and go to:**
```
http://localhost:8069
```

**You'll see the Odoo database manager.**

### Create Database:

1. **Click "Create Database"**
2. **Enter details:**
   ```
   Master Password: admin  (default Odoo master password)
   Database Name: myodoo
   Email: your-email@example.com
   Password: myodooadmin
   Language: English (US)
   Country: United States
   ```
3. **Click "Create Database"**
4. **Wait 1-2 minutes** for database creation
5. **You'll be redirected** to Odoo login page

---

## Step 2: Login to Odoo

**After database creation:**

1. **Login with:**
   ```
   Email: your-email@example.com
   Password: myodooadmin
   ```

2. **You're now in Odoo!**

---

## Step 3: Update MCP Configuration

Your current config has:
```json
{
  "url": "http://localhost:8069",
  "database": "myodoo",
  "username": "aaish",
  "password": "myodooadmin"
}
```

**After creating the database, the username will be your email.**

**Run setup again with correct credentials:**
```bash
cd Bronze-tier
python odoo_setup.py
```

**Enter:**
```
Odoo URL: http://localhost:8069
Database name: myodoo
Username: your-email@example.com  (the email you used)
Password: myodooadmin
```

---

## Step 4: Test Connection

```bash
cd Bronze-tier
python run_odoo_tools.py
# Select: 1. Test Connection
```

**Expected output:**
```
{'status': 'success', 'message': 'Connected to Odoo (UID: 2)'}
```

---

## Docker Commands Reference

### Start Odoo
```bash
cd D:\Autonomus-fte
docker-compose up -d
```

### Stop Odoo
```bash
cd D:\Autonomus-fte
docker-compose down
```

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f odoo
docker-compose logs -f db
```

### Restart Odoo
```bash
docker restart odoo
```

---

## Troubleshooting

### Port 8069 Already in Use

**Error:** "Bind for 0.0.0.0:8069 failed: port is already allocated"

**Solution:**
```bash
# Find what's using port 8069
netstat -ano | findstr "8069"

# Kill the process
taskkill /PID <PID> /F

# Or change Odoo port in docker-compose.yml to 8070:8069
```

### Database Creation Fails

**Solution:**
1. Use master password: `admin`
2. Make sure no other database with same name exists
3. Check Odoo logs: `docker-compose logs odoo`

### Can't Access http://localhost:8069

**Solutions:**
1. Wait 60 seconds after starting containers
2. Check containers are running: `docker-compose ps`
3. Check logs: `docker-compose logs odoo`

---

## Quick Commands

```bash
# Start everything
cd D:\Autonomus-fte
docker-compose up -d

# Wait for Odoo to start (first time: 60 seconds)
timeout /t 60

# Test connection
cd Bronze-tier
python check_odoo_connection.py

# Test MCP
python run_odoo_tools.py
```

---

## Your Next Steps

1. ✅ **Open:** http://localhost:8069
2. ✅ **Create database** "myodoo"
3. ✅ **Login** with your credentials
4. ✅ **Run:** `python odoo_setup.py` (update credentials)
5. ✅ **Test:** `python run_odoo_tools.py`

**You're almost there!** 🚀
