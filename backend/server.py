import os
from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv

from src.config.rate_limiter import limiter
from src.routes import register_routes
from src.middleware.error_handler import handle_exception

load_dotenv()

app = Flask(__name__)

CORS(app, origins=["http://localhost:5173"])

limiter.init_app(app)

Swagger(app, template={
    "info": {
        "title": "CareerBridge API",
        "description": "CareerBridge REST API",
        "version": "1.0.0",
    },
    "basePath": "/api/v1",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Format: Bearer <jwt>",
        }
    },
})

register_routes(app)
app.register_error_handler(Exception, handle_exception)


@app.errorhandler(404)
def not_found(_e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(_e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def server_error(_e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    debug = os.getenv("NODE_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
