# endpoints/simulations.py
from flask import Blueprint, jsonify, request
from db import get_db

bp = Blueprint("simulations", __name__, url_prefix="/api/simulations")

@bp.get("")
@bp.get("/")
def list_simulations():
    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    db = get_db()
    rows = db.execute("SELECT * FROM simulations LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    return jsonify([dict(r) for r in rows]), 200

@bp.get("/<id_>")
def get_simulation(id_):
    db = get_db()
    row = db.execute("SELECT * FROM simulations WHERE id = ? OR CAST(id AS TEXT) = ?", (id_, id_)).fetchone()
    if not row: return jsonify({"error":"não encontrado"}), 404
    return jsonify(dict(row)), 200
