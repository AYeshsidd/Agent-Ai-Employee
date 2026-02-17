from pathlib import Path


class Config:
    """Centralized configuration for Bronze-tier Vault system"""

    BASE_DIR = Path(__file__).parent
    VAULT_ROOT = BASE_DIR / "Vault"

    INBOX = VAULT_ROOT / "Inbox"
    NEEDS_ACTION = VAULT_ROOT / "Needs_Action"
    DONE = VAULT_ROOT / "Done"

    DASHBOARD = VAULT_ROOT / "Dashboard.md"
    HANDBOOK = VAULT_ROOT / "Company_Handbook.md"

    SKILLS_DIR = BASE_DIR / "skills"
