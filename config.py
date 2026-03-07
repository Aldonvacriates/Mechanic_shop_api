"""Application configuration objects.

Why: centralizing environment settings keeps app creation predictable and
avoids hardcoding configuration in multiple places.
"""

class Config:
    """Base shared settings used by all runtime environments."""

    SQLALCHEMY_DATABASE_URI = (
        "mysql+mysqlconnector://root:Lolita1!@localhost/mechanic_shop_api_db"
    )
    # Why: disabling this avoids unnecessary overhead from change tracking.
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Local development settings."""

    # Why: detailed tracebacks help while building and debugging routes.
    DEBUG = True


config = {"DevelopmentConfig": DevelopmentConfig}


class TestingConfig:
    """Placeholder for test-specific overrides."""

    pass


class ProductionConfig:
    """Placeholder for production-specific overrides."""

    pass
