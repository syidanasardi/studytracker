from app.main import app
from app.migrate import apply_migrations

# Try to run migrations on startup
try:
    apply_migrations()
except Exception as e:
    print(f"Migration warning: {e}")