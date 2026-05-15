from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    CORS(app)  # allow React to connect

    db.init_app(app)

    #from app.routes.user_routes import main as main_blueprint
    #app.register_blueprint(main_blueprint)
    from app.routes import main
    app.register_blueprint(main)

    return app