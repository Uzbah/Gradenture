import logging
from flask import jsonify

logger = logging.getLogger(__name__)


def handle_exception(err):
    logger.exception(err)
    return jsonify({"error": "Internal server error"}), 500
