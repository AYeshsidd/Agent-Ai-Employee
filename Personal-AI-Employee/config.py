from pathlib import Path


class Config:
    """Centralized configuration for Bronze-tier Vault system"""

    BASE_DIR = Path(__file__).parent
    VAULT_ROOT = BASE_DIR / "Vault"
    LOGS_DIR = BASE_DIR / "logs"

    DROPS = VAULT_ROOT / "Drops"
    INBOX = VAULT_ROOT / "Inbox"
    NEEDS_ACTION = VAULT_ROOT / "Needs_Action"
    DONE = VAULT_ROOT / "Done"

    DASHBOARD = VAULT_ROOT / "Dashboard.md"
    HANDBOOK = VAULT_ROOT / "Company_Handbook.md"

    SKILLS_DIR = BASE_DIR / "skills"

    WATCHER_LOG = LOGS_DIR / "watcher.log"
    VAULT_LOG = LOGS_DIR / "vault_operations.log"
    BRONZE_TIER_LOG = LOGS_DIR / "bronze_tier.log"
