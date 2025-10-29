from flask import Blueprint, jsonify, request
from controllers import listar_base_lojas, listar_base_players, listar_base_simulacao, listar_base_transacoes

bp = Blueprint("bases", __name__)

@bp.route("/players", methods=["GET"])
def get_usuario():
    body, status = listar_base_players()
    return jsonify(body), status

@bp.route("/simulacao", methods=["GET"])
def get_usuario():
    body, status = listar_base_simulacao()
    return jsonify(body), status

@bp.route("/trasacoes", methods=["GET"])
def get_usuario():
    body, status = listar_base_transacoes()
    return jsonify(body), status

@bp.route("/lojas", methods=["GET"])
def get_usuario():
    body, status = listar_base_lojas()
    return jsonify(body), status