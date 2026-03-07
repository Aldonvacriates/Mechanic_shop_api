class Config:
    SQLALCHEMY_DATABASE_URI = (
        "mysql+mysqlconnector://root:Lolita1!@localhost/mechanic_shop_api_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


config = {"DevelopmentConfig": DevelopmentConfig}

class TestingConfig:
    pass

class ProductionConfig:
    pass
