from flask import Flask
from flask_bootstrap import Bootstrap
from app.main import main as main_blueprint
from app_config import config


app = Flask(__name__)
bootstrap = Bootstrap()
bootstrap.init_app(app)
app.config.from_mapping(config)
app.register_blueprint(main_blueprint, url_prefix='/hupu')