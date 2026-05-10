# Personal AI Employee: Project Explanation

Welcome to the **Personal AI Employee** (Autonomous FTE) project. This system is a sophisticated, modular, and autonomous AI agent framework designed to handle tasks across multiple platforms (Social Media, Email, Accounting) with human-in-the-loop safety.

This document provides a deep, technically detailed explanation of how the system works, its architecture, and the flow of data through its various components.

---

## 1. System Architecture

The system follows a modular "Watcher-Planner-Executor" architecture, built on a Markdown-based "Vault" for persistence and communication.

### High-Level Architecture Diagram

```ascii
┌──────────────────────────────────────────────────────────────────────────┐
│                           External Platforms                             │
│      (Gmail, LinkedIn, WhatsApp, Twitter, Facebook, Filesystem)          │
└──────────┬──────────────────────┬───────────────────────┬────────────────┘
           │                      │                       │
           ▼                      ▼                       ▼
┌──────────────────┐      ┌──────────────────┐     ┌──────────────────┐
│     Watchers     │      │   Social Media   │     │   File Monitor   │
│ (Gmail/WhatsApp) │      │ (LinkedIn/Tw/Fb) │     │ (Drops Folder)   │
└──────────┬───────┘      └───────┬──────────┘     └───────┬──────────┘
           │                      │                       │
           └───────────┬──────────┴───────────────────────┘
                       │
                       ▼
           ┌────────────────────────┐
           │     Vault / Inbox      │ (Raw Markdown Tasks)
           └───────────┬────────────┘
                       │
                       ▼
           ┌────────────────────────┐
           │   Ralph Wiggum Loop    │ (The Brain)
           │ ────────────────────── │
           │ 1. Task Analyzer       │
           │ 2. Plan Generator      │
           │ 3. Action Executor     │
           └───────────┬────────────┘
                       │
           ┌───────────┴───────────┐
           ▼                       ▼
┌──────────────────┐      ┌────────────────────────┐
│  Approval System │      │       MCP Server       │ (Modular Tools)
│ (Human-in-Loop)  │      ├────────────────────────┤
│ Dashboard        │ <──> │ • Email Module         │
│ Manager          │      │ • Social Module        │
└───────────┬──────┘      │ • Accounting Module    │
           │              └───────────┬────────────┘
           │                          │
           ▼                          ▼
┌──────────────────┐      ┌────────────────────────┐
│  Vault / Done    │      │    External Actions    │
│ (Audit Trail)    │      │ (Posts, Emails, Odoo)  │
└──────────────────┘      └────────────────────────┘
```

---

## 2. Folder-by-Folder Breakdown

### Core System
- `main.py`: The entry point for the basic "Bronze-tier" system.
- `run_ralph_wiggum.py`: The main runner for the autonomous "Silver-tier" loop.
- `config.py`: Centralized configuration (paths, folders).
- `vault_manager.py`: Handles all operations related to the Markdown Vault (init, list, move).
- `bronze_logger.py`: Centralized logging engine with standardized formatting.

### Component Directories
- `ralph_wiggum_loop/`: The heart of the autonomous agent.
    - `loop.py`: Orchestrates the continuous scan-analyze-execute cycle.
    - `task_analyzer.py`: Identifies intent and required actions from raw text.
    - `action_executor.py`: Maps planned actions to tool calls (Skills or MCP).
    - `error_handler.py`: Manages retries and fallback logic.
- `Vault/`: The persistent storage system.
    - `Inbox/`: Raw incoming tasks from watchers.
    - `Needs_Action/`: Tasks analyzed and ready for execution/approval.
    - `Done/`: Completed tasks with full audit history.
    - `Drops/`: Folder monitored for manual file uploads.
- `mcp_server/`: Modular execution environment (Model Context Protocol).
    - `server.py`: Main router that maintains backward compatibility.
    - `modules/`: Domain-specific toolsets (Email, Social, Accounting).
- `skills/`: Atomic capabilities of the agent.
    - `watcher_skills/`: Logic for monitoring different platforms.
    - `*_auto_post_skill.py`: Platform-specific posting logic (LinkedIn, Twitter, Facebook).
    - `plan_generator_skill.py`: Generates structured `Plan.md` files.
- `approval_system/`: Human-in-the-loop component.
    - `approval_dashboard.py`: A Flask-based web UI for approving pending tasks.
    - `approval_manager.py`: Logic for tracking and persisting approval states.
- `watchers/`: Scripts to run the various monitoring agents.
- `odoo_mcp/`: Specialized integration for Odoo ERP (Accounting, CRM).
- `logs/`: Comprehensive audit trail for every component.
- `docs/`: Technical guides and architecture summaries.

---

## 3. The Autonomous Execution Flow

The system operates in a continuous cycle, moving tasks through the Vault as they progress.

### Step-by-Step Data Flow

1.  **Detection (The Watchers):**
    - The `FileWatcher` monitors the `Vault/Drops` folder.
    - Social/Gmail watchers (e.g., `GmailWatcherSkill`) poll APIs or use browser automation (Playwright) to detect new mentions, messages, or emails.
2.  **Ingestion:**
    - When an input is detected, a watcher creates a new Markdown file in `Vault/Inbox`.
    - This file contains the source, timestamp, and raw content.
3.  **Analysis (Ralph Wiggum Loop):**
    - The `RalphWiggumLoop` scans the `Inbox`.
    - `TaskAnalyzer` parses the Markdown and determines the **Task Type** (e.g., `SOCIAL_POST`, `ACCOUNTING_INVOICE`, `EMAIL_REPLY`).
    - It extracts parameters (e.g., "recipient", "subject", "post_content").
4.  **Planning:**
    - `PlanGeneratorSkill` creates a detailed execution plan (`{TASK_NAME}_PLAN.md`) in `Needs_Action`.
    - The task itself is moved from `Inbox` to `Needs_Action`.
5.  **Approval (Human-in-the-Loop):**
    - If a task is marked as "high priority" or requires sensitive actions (like posting to social media or sending money), it enters the `Approval System`.
    - The user reviews the plan via the `Approval Dashboard`.
    - Once approved, the task status is updated to `APPROVED`.
6.  **Execution:**
    - `ActionExecutor` picks up the approved task.
    - It identifies which **MCP Tool** or **Skill** to call.
    - It executes the action (e.g., `mcp_server.call_tool("send_email", ...)`).
7.  **Finalization & Auditing:**
    - The results are appended to the task file.
    - The task is moved to `Vault/Done`.
    - All events are logged in `logs/bronze_tier.log` and specialized logs.

---

## 4. Key Components Detail

### MCP Server (Modular Toolset)
The MCP (Model Context Protocol) server is the "arms and legs" of the agent. It is modular, allowing for easy expansion.
- **Email Module:** Handles Gmail integration for sending and reading emails.
- **Social Module:** Manages posting to LinkedIn, Twitter, and Facebook.
- **Accounting Module:** Integrates with Odoo for invoice creation and expense tracking.

### Ralph Wiggum Loop (The Brain)
Named after the character who "helps," this loop is actually a robust state machine.
- **Continuous Mode:** Scans every X seconds.
- **Error Handling:** Implements exponential backoff and "Fallback Actions" (e.g., if a LinkedIn post fails via API, notify the user instead).
- **Task Identity:** Every task has a unique ID based on its timestamp and content, preventing duplicate processing.

### The Vault (Markdown Database)
Instead of a complex SQL database, the system uses a human-readable folder structure.
- **Transparency:** You can see exactly what the agent is thinking by opening the `.md` files in `Needs_Action`.
- **Editability:** You can manually edit a task file to correct the agent before it executes.

---

## 5. Important Functions & Usage

| Function | Component | Purpose |
| :--- | :--- | :--- |
| `run_loop()` | `ralph_wiggum_loop` | Starts the autonomous scanning engine. |
| `analyze_task()` | `TaskAnalyzer` | Uses regex and logic to categorize raw text. |
| `call_tool()` | `MCPServer` | The bridge between the AI's intent and actual API calls. |
| `generate_plan()` | `PlanGenerator` | Converts a vague task into a step-by-step `Plan.md`. |
| `execute_with_retry()`| `ErrorHandler` | Ensures transient network issues don't kill a task. |
| `log_lifecycle_event()`| `BronzeLogger` | Records every time a task moves between folders. |

---

## 6. Libraries & Purpose

- **Playwright / Selenium:** Used for browser automation (LinkedIn/Twitter/WhatsApp) where APIs are limited.
- **Watchdog:** Real-time filesystem monitoring for the `Drops` folder.
- **Flask:** Powers the `Approval Dashboard` web interface.
- **Google API Client:** Handles Gmail authentication and operations.
- **OdooRPC:** Connects the agent to the Odoo ERP system.
- **Markdown:** Used for structured data storage that remains human-readable.

---

## 7. Error Handling & Reliability

1.  **Duplicate Prevention:** The system tracks processed IDs (filenames and hashes) to ensure an email isn't processed twice.
2.  **Retry Logic:** Failed network calls are retried up to 3 times with increasing delays.
3.  **Fallback Mechanism:** If a primary action fails, the system can trigger a "notification fallback" to alert the human.
4.  **Audit Logs:** Every single action, from "file detected" to "tool execution success," is logged with a timestamp in the `logs/` directory.

---

## 8. End-to-End Example: "The Invoice Request"

1.  **Trigger:** A client sends an email asking for an invoice.
2.  **Watch:** `GmailWatcherSkill` sees the email and creates `20260509_Invoice_Request.md` in `Vault/Inbox`.
3.  **Analyze:** `TaskAnalyzer` sees the word "invoice" and marks it as `ACCOUNTING_INVOICE`.
4.  **Plan:** `PlanGenerator` creates a plan: "1. Create invoice in Odoo, 2. Download PDF, 3. Email to client."
5.  **Approve:** The user sees a notification, opens the `Approval Dashboard`, and clicks "Approve".
6.  **Execute:**
    - `ActionExecutor` calls `odoo_mcp.create_invoice()`.
    - `ActionExecutor` calls `mcp_server.send_email()` with the invoice details.
7.  **Done:** The file is moved to `Vault/Done` with a note: "Completed successfully."

---

## Summary

The **Personal AI Employee** is more than just a script; it is a scalable, reliable framework for delegating complex, multi-platform workflows to an AI while maintaining full visibility and control through the Markdown Vault and Approval System.
