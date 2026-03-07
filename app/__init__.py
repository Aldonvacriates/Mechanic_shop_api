from flask import Flask
from config import config
from app.extensions import db, ma


def create_app(config_name="DevelopmentConfig"):

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    ma.init_app(app)

    # import models
    from app import models

    # register blueprints
    from app.blueprints.customers import customers_bp
    from app.blueprints.mechanics import mechanics_bp
    from app.blueprints.vehicles import vehicles_bp
    from app.blueprints.service_tickets import service_tickets_bp

    app.register_blueprint(customers_bp)
    app.register_blueprint(mechanics_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(service_tickets_bp)

    with app.app_context():
        db.create_all()

    return app
