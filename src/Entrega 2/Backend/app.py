from flask import Flask, jsonify
from flask_cors import CORS
from db import close_db
from endpoints.players import bp as players_bp
from endpoints.transactions import bp as transactions_bp
from endpoints.stores import bp as stores_bp
from endpoints.simulations import bp as simulations_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["JSON_AS_ASCII"] = False

    @app.after_request
    def force_utf8_in_json(resp):
        if resp.mimetype == "application/json" and "charset" not in resp.content_type:
            resp.headers["Content-Type"] = "application/json; charset=utf-8"
        return resp

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    app.register_blueprint(players_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(stores_bp)
    app.register_blueprint(simulations_bp)

    app.teardown_appcontext(close_db)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
