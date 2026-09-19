from pathlib import Path

# Backend package root (the directory holding main.py)
BASE_PATH = Path(__file__).resolve().parent.parent

# Repository root (holds backend/, frontend/, supabase/)
REPO_PATH = BASE_PATH.parent

# Environment files
ENV_FILE_PATH = BASE_PATH / '.env'
ENV_EXAMPLE_FILE_PATH = BASE_PATH / '.env.example'

# Log file directory
LOG_DIR = BASE_PATH / 'log'

# Raw SQL migrations, applied by backend/scripts/migrate.py
MIGRATION_DIR = REPO_PATH / 'supabase' / 'migrations'

# Built frontend, served at / in production when present
FRONTEND_DIST_DIR = REPO_PATH / 'frontend' / 'dist'
