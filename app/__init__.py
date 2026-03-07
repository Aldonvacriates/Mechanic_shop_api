from flask import Flask
from config import Config
from app.extensions import db, ma


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(f"config.{config_name}")

    db.init_app(app)
    ma.init_app(app)

    # import models
    from app import models

    # register blueprints
    from app.blueprints.customers import customers_bp

    app.register_blueprint(customers_bp)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return "Mechanic shop API running"

    return app
