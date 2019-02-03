import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very secret key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    PAGINATION_PAGE_SIZE = 10
    PAGINATION_PAGE_ARGUMENT_NAME = 'page'

    @staticmethod
    def init_app(app):
        pass

class DevConfig(Config):
    DEBUG=True
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DevDatabase') or \
    #     "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(os.getenv('FAM_DB_USER_DBG'), DB_PASS=os.getenv('FAM_DB_PASS_DBG'), DB_ADDR="127.0.0.1", DB_NAME="familytree_dev"))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'familytree-dev.sqlite')

class TestConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite://'

class ProdConfig(Config):
    # SQLALCHEMY_DATABASE_URI = os.environ.get('ProdDatabase') or \
    #     "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(os.getenv('FAM_DB_USER'), DB_PASS=os.getenv('FAM_DB_PASS'), DB_ADDR="127.0.0.1", DB_NAME="familytree")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'familytree-prod.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging import FileHandler

        file_handler = FileHandler('flask_familytree.log')      
        file_handler.setLevel(logging.DEBUG)
 
        # Create a Formatter for formatting the log messages
        logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        
        # Add the Formatter to the Handler
        file_handler.setFormatter(logger_formatter)

        app.logger.addHandler(file_handler)

class DockerConfig(ProdConfig):
    @classmethod
    def init_app(cls, app):
        ProdConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


configs = {
    'development': DevConfig(),
    'test': TestConfig(),
    'prod': ProdConfig(),
    'docker': DockerConfig(),
    'default': DevConfig()
}