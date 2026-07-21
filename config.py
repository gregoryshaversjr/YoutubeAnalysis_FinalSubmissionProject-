from pathlib import Path

#class to hold configuration constants for the application
class Config:
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    WATCH_HISTORY_PATH = DATA_DIR / "demo_watch_history.json"
    UPLOADED_DATA_PATH = DATA_DIR / "uploaded.json"
    APP_STATE_PATH = DATA_DIR / "app_state.json"
    SESSION_DATA_DIR = DATA_DIR / "sessions"
    DEMO_MODE = "demo"
    UPLOADED_MODE = "uploaded"


