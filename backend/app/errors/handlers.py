from flask import jsonify
from app.errors.exceptions import AppError
from sqlalchemy.exc import OperationalError


def register_error_handlers(app):

    @app.errorhandler(AppError)
    def handle_app_error(error):
        app.logger.warning(str(error))
        return jsonify({
            "error": error.message
        }), error.status_code

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            "error": "Endpoint not found"
        }), 404

    @app.errorhandler(400)
    def handle_400(error):
        return jsonify({
            "error": "Bad request"
        }), 400

    @app.errorhandler(OperationalError)
    def handle_db_error(error):
        app.logger.exception("Database error")
        return jsonify({"error": "Database unavailable"}), 503

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled exception")
        return jsonify({
            "error": "Internal server error"
        }), 500
