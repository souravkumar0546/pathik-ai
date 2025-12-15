from flask import Flask,request
from .extensions import db, migrate, cors
from app.logging import setup_logging

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    setup_logging(app)

    @app.before_request
    def log_request():
        app.logger.info(
            f"{request.method} {request.path} from {request.remote_addr}"
        )
    @app.after_request
    def log_response(response):
        app.logger.info(
            f"{request.method} {request.path} -> {response.status_code}"
        )
        return response

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from .routes.campaigns import campaigns_bp
    app.register_blueprint(campaigns_bp, url_prefix="/api/campaigns")

    return app