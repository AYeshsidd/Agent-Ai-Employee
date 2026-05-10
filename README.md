
# 🤖 Personal AI Employee (Autonomous FTE)

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Architecture](https://img.shields.io/badge/Architecture-Autonomous--AI--Agent-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Overview

**Personal AI Employee** is an autonomous AI agent system designed to function like a *Full-Time Equivalent (FTE)* digital employee.  
It automates real-world business and communication workflows across Gmail, LinkedIn, Twitter/X, WhatsApp, and Odoo ERP using intelligent planning, execution, and approval-based control.

It bridges the gap between **LLMs and real business systems** through modular automation and MCP-based tool orchestration.

---

## 🎯 What This AI Employee Can Do

- 📧 Monitor Gmail and generate actionable tasks automatically  
- 💼 Create invoices, payments, and expenses in **Odoo ERP**
- 🔗 Automate LinkedIn, Twitter/X, and Facebook workflows  
- 🤖 Convert messages into structured execution plans  
- 🧠 Run autonomous task processing pipelines  
- 👨‍💻 Maintain human approval for critical actions  
- 📊 Keep full audit logs of all operations  

---

## 🏗 System Architecture

The system follows a **Watcher → Planner → Executor → Approval → Action** lifecycle.

```

External Platforms (Gmail, LinkedIn, WhatsApp, Twitter)
│
▼
Watchers Layer
(Email, Social, File Monitoring)
│
▼
Vault / Task Inbox
(Markdown-based storage)
│
▼
Autonomous Execution Engine
(Task Analyzer + Planner + Executor)
│
┌────────┴────────┐
▼                 ▼
Approval System   MCP Server
(Human Control)   (Tool APIs)
│                 │
└──────┬──────────┘
▼
External Actions
(Odoo, Email, Social APIs)
│
▼
Vault / Done
(Audit Trail)

````

---

## 🧠 Core Features

### ⚙️ Autonomous Execution Engine
Self-operating loop that detects tasks, understands intent, creates plans, and executes workflows.

### 💼 Odoo ERP Integration
- Invoice generation from natural language
- Payment tracking & reconciliation
- CRM and accounting automation

### 🌐 Multi-Platform Watchers
- Gmail monitoring
- LinkedIn / Twitter / Facebook automation
- WhatsApp message detection
- File system event tracking

### 🛠 MCP (Model Context Protocol) Server
Modular tool system that allows AI models to execute real-world actions:
- Email automation
- Social media automation
- Accounting operations (Odoo)
- Extensible architecture

### 👨‍💻 Human-in-the-Loop System
Critical actions require approval before execution via dashboard interface.

### 📜 Audit & Vault System
Every action is stored in a markdown-based vault for transparency and traceability.

---

## 🛠 Tech Stack

- **Backend:** Python 3.10+
- **Automation:** Playwright, Watchdog
- **AI Logic:** Structured prompting + rule-based orchestration
- **ERP Integration:** Odoo JSON-RPC
- **MCP Server:** Modular Python architecture
- **Storage:** Markdown Vault system
- **Logging:** Custom audit logging system

---

## 🔄 Task Lifecycle

1. **Detection** → Watcher detects event (email, message, file)
2. **Analysis** → Task is classified and structured
3. **Planning** → Execution plan is generated
4. **Approval** → Human approves action (if required)
5. **Execution** → MCP tools perform real-world actions
6. **Archival** → Task moved to Done with full logs

---

## 🔒 Security Design

- Credentials stored outside Git (ignored via `.gitignore`)
- Session-based authentication handling
- Human approval for sensitive actions
- Full audit logging system
- Isolated MCP modules

---

## ⚙️ Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/personal-ai-employee.git
cd Personal-AI-Employee
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start System

```bash
python main.py
```

### 4. Run Autonomous Engine

```bash
python run_ralph_wiggum.py
```

---

## 🧭 Roadmap

* 🔄 Multi-agent collaboration system
* 🎤 Voice-based AI employee (Whisper + TTS)
* 📚 RAG-based memory system for long-term intelligence
* 🐳 Dockerized MCP deployment
* 📊 Advanced analytics dashboard

---

## 💎 Premium Tier (Coming Soon)

This project is designed with a scalable architecture. A **Premium Tier expansion** is planned to extend capabilities into enterprise-grade automation, including:

- 🏢 Advanced business workflow automation (end-to-end enterprise operations)  
- 🤝 Multi-tenant AI employee system for organizations  
- 📊 AI-driven financial insights and reporting layer on top of Odoo  
- 🔐 Enhanced security, role-based access control (RBAC)  
- ⚙️ Cloud deployment with scalable MCP microservices  

> This turns the system from a personal AI employee into a **full enterprise autonomous workforce platform**.

## 👨‍💻 Author

**Ayesh Sidd**
AI Engineer | Agentic AI Developer | Full-Stack Developer

* LinkedIn: [linkedin.com/in/aaish-siddiqui](linkedin.com/in/aaish-siddiqui)
* Email: [hafizayeshsidd@gmail.com](mailto:hafizayeshsidd@gmail.com)

---

## 💡 Vision

This project represents a step toward **Autonomous Digital Employees** — systems that can understand intent, plan execution, and perform real business operations with minimal human intervention.

> “From AI tools → to AI employees”

```
