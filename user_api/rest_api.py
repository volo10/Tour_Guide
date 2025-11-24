#!/usr/bin/env python3
"""
REST API for Tour Guide.

Provides HTTP endpoints for getting tour recommendations.
Requires Flask: pip install flask

Run with:
    python -m user_api.rest_api
    # or
    python user_api/rest_api.py

Endpoints:
    GET  /                      - API info
    GET  /tour?source=X&dest=Y  - Get tour recommendations
    POST /tour                  - Get tour (JSON body)
    GET  /health                - Health check
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None

from .tour_guide_api import TourGuideAPI


def create_app(default_interval: float = 3.0) -> 'Flask':
    """
    Create and configure the Flask application.

    Args:
        default_interval: Default seconds between junctions

    Returns:
        Configured Flask app
    """
    if not FLASK_AVAILABLE:
        raise ImportError(
            "Flask is required for REST API. Install with: pip install flask"
        )

    app = Flask(__name__)
    api = TourGuideAPI(junction_interval_seconds=default_interval)

    @app.route('/')
    def index():
        """API information."""
        return jsonify({
            "name": "Tour Guide API",
            "version": "1.0.0",
            "description": "Get personalized recommendations for your route",
            "endpoints": {
                "GET /": "This info",
                "GET /tour": "Get tour (query params: source, destination, interval)",
                "POST /tour": "Get tour (JSON body)",
                "GET /health": "Health check",
            },
            "example": {
                "url": "/tour?source=Tel+Aviv&destination=Jerusalem",
                "method": "GET",
            }
        })

    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({"status": "healthy"})

    @app.route('/tour', methods=['GET'])
    def get_tour():
        """
        Get tour recommendations via GET request.

        Query params:
            source: Starting address (required)
            destination: Destination address (required)
            interval: Seconds per junction (optional, default 3)
        """
        source = request.args.get('source')
        destination = request.args.get('destination')
        interval = request.args.get('interval', default_interval, type=float)

        if not source:
            return jsonify({"error": "Missing 'source' parameter"}), 400
        if not destination:
            return jsonify({"error": "Missing 'destination' parameter"}), 400

        # Update interval if specified
        api.junction_interval = interval

        result = api.get_tour(source, destination, verbose=False)
        return jsonify(result.to_dict())

    @app.route('/tour', methods=['POST'])
    def post_tour():
        """
        Get tour recommendations via POST request.

        JSON body:
            {
                "source": "Tel Aviv",
                "destination": "Jerusalem",
                "interval": 3.0  // optional
            }
        """
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400

        source = data.get('source')
        destination = data.get('destination')
        interval = data.get('interval', default_interval)

        if not source:
            return jsonify({"error": "Missing 'source' field"}), 400
        if not destination:
            return jsonify({"error": "Missing 'destination' field"}), 400

        api.junction_interval = interval

        result = api.get_tour(source, destination, verbose=False)
        return jsonify(result.to_dict())

    return app


def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Run the REST API server.

    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable debug mode
    """
    if not FLASK_AVAILABLE:
        print("❌ Flask is required for REST API.")
        print("   Install with: pip install flask")
        sys.exit(1)

    app = create_app()

    print(f"\n🚀 Tour Guide REST API")
    print(f"   Running on http://{host}:{port}")
    print(f"\n   Endpoints:")
    print(f"     GET  /                        - API info")
    print(f"     GET  /tour?source=X&dest=Y    - Get recommendations")
    print(f"     POST /tour                    - Get recommendations (JSON)")
    print(f"     GET  /health                  - Health check")
    print(f"\n   Example:")
    print(f"     curl 'http://localhost:{port}/tour?source=Tel+Aviv&destination=Jerusalem'")
    print()

    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Tour Guide REST API Server")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()
    run_server(host=args.host, port=args.port, debug=args.debug)
