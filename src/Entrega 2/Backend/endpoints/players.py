from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("players", __name__, url_prefix="/api/players")

@bp.get("")
@bp.get("/")
def list_players():
    """Lista tudo (com limit/offset opcionais)."""
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    db = get_db()
    rows = db.execute(f"SELECT * FROM players LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    return jsonify([dict(r) for r in rows]), 200

@bp.get("/<id_>")
def get_player(id_):
    db = get_db()
    # tenta tratar id numérico ou texto
    row = db.execute("SELECT * FROM players WHERE id = ? OR CAST(id AS TEXT) = ?", (id_, id_)).fetchone()
    if not row:
        return jsonify({"error": "não encontrado"}), 404
    return jsonify(dict(row)), 200
