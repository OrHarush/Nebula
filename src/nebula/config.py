from pathlib import Path

# <project root>/src/nebula/config.py -> parents[2] is the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = DATA_DIR / "models"
DB_PATH = DATA_DIR / "database.db"
