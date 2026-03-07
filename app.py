"""Development entry point for running the Flask API locally.

Why: this file gives one predictable startup path while bootstrapping tables
for quick iteration during development.
"""

from app import create_app
from app.models import db

app = create_app("DevelopmentConfig")

# Why: auto-create tables on startup so local testing works without migrations.
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Why: debug mode speeds up development by reloading on code changes.
    app.run(debug=True)
