"""
Flask API for GROWv2
RESTful API endpoints for the cultivation game.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from .. import __version__
from ..config import get_settings
from ..db.session import init_db
from .game_api import game_bp
from .errors import register_error_handlers
from .observability import register_observability
from .openapi import register_openapi
from .ratelimit import init_limiter


def create_app(init_database: bool = True):
    """Create and configure Flask application"""
    app = Flask(__name__)
    settings = get_settings()

    # Behind Render's proxy: trust one hop of X-Forwarded-For/-Proto so client
    # IPs (used for rate limiting + logging) and scheme are accurate.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    # Restrict CORS to an explicit origin allowlist (no wildcard by default) and
    # only on the API surface. Allow the X-API-Key header used for auth.
    CORS(
        app,
        resources={r"/api/*": {"origins": settings.cors_allowed_origins}},
        allow_headers=["Content-Type", "X-API-Key"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        max_age=3600,
    )

    # Rate limiting (brute-force / spam protection), keyed by client IP.
    app.config["RATELIMIT_ENABLED"] = settings.ratelimit_enabled
    app.config["RATELIMIT_STORAGE_URI"] = settings.ratelimit_storage_uri
    init_limiter(app)

    # Ensure the persistent game schema exists (no-op for already-migrated DBs).
    if init_database:
        init_db()

    # Consistent JSON error responses + request-size cap.
    register_error_handlers(app)

    # Health/readiness probes + per-request logging.
    register_observability(app)

    # Self-describing API docs: /openapi.json + Swagger UI at /docs.
    register_openapi(app)

    # DB-backed game layer (players, economy, strains, breeding, market).
    app.register_blueprint(game_bp)

    @app.route('/')
    def index():
        """API root endpoint"""
        return jsonify({
            "name": "GROWv2 API",
            "version": __version__,
            "description": "Cannabis cultivation game: economy, genetics, real-time sim & on-chain assets",
            "endpoints": {
                "game": "/api/game",
                "docs": "/docs",
            }
        })

    return app


if __name__ == '__main__':
    import os
    app = create_app()
    # Only enable debug mode if explicitly set in environment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
