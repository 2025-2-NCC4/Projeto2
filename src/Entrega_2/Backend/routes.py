from flask import Blueprint, jsonify, request
from controllers import players_ctrl, simulations_ctrl, stores_ctrl, transactions_ctrl

bp = Blueprint("api", __name__)

def _int(v):
    try:
        return int(v) if v not in (None,"") else None
    except:
        return None

def _float(v):
    try:
        return float(v) if v not in (None,"") else None
    except:
        return None

def _limit():
    v = _int(request.args.get("limit"))
    v = 200 if v is None else v
    return min(max(v, 1), 5000)

@bp.get("/players")
@bp.get("/players/")
def players():
    payload = dict(
        filters={
            "celular": request.args.get("celular"),
            "sexo": request.args.get("sexo"),
            "cidade_residencial": request.args.get("cidade_residencial"),
            "bairro_residencial": request.args.get("bairro_residencial"),
            "cidade_trabalho": request.args.get("cidade_trabalho"),
            "bairro_trabalho": request.args.get("bairro_trabalho"),
            "cidade_escola": request.args.get("cidade_escola"),
            "bairro_escola": request.args.get("bairro_escola"),
            "categoria_frequentada": request.args.get("categoria_frequentada"),
            "idade_min": _int(request.args.get("idade_min")),
            "idade_max": _int(request.args.get("idade_max")),
            "data_nascimento_from": request.args.get("data_nascimento_from"),
            "data_nascimento_to": request.args.get("data_nascimento_to"),
        },
        cursor=_int(request.args.get("cursor")),
        limit=_limit(),
        fields=request.args.get("fields"),
        sort_by=request.args.get("sort_by","id"),
        sort_dir=request.args.get("sort_dir","asc"),
        q=request.args.get("q"),
    )
    body = players_ctrl(**payload)
    return jsonify(body), 200

@bp.get("/simulacao")
@bp.get("/simulacao/")
def simulations():
    payload = dict(
        filters={
            "celular": request.args.get("celular"),
            "data_from": request.args.get("data_from"),
            "data_to": request.args.get("data_to"),
            "horario": request.args.get("horario"),
            "local": request.args.get("local"),
            "latitude": request.args.get("latitude"),
            "longitude": request.args.get("longitude"),
            "tipo_celular": request.args.get("tipo_celular"),
            "modelo_celular": request.args.get("modelo_celular"),
            "possui_app_picmoney": request.args.get("possui_app_picmoney"),
            "data_ultima_compra_from": request.args.get("data_ultima_compra_from"),
            "data_ultima_compra_to": request.args.get("data_ultima_compra_to"),
            "ultimo_tipo_cupom": request.args.get("ultimo_tipo_cupom"),
            "ultimo_valor_capturado_min": _float(request.args.get("ultimo_valor_capturado_min")),
            "ultimo_valor_capturado_max": _float(request.args.get("ultimo_valor_capturado_max")),
            "ultimo_tipo_loja": request.args.get("ultimo_tipo_loja"),
            "idade_min": _int(request.args.get("idade_min")),
            "idade_max": _int(request.args.get("idade_max")),
            "sexo": request.args.get("sexo"),
        },
        cursor=_int(request.args.get("cursor")),
        limit=_limit(),
        fields=request.args.get("fields"),
        sort_by=request.args.get("sort_by","id"),
        sort_dir=request.args.get("sort_dir","asc"),
        q=request.args.get("q"),
    )
    body = simulations_ctrl(**payload)
    return jsonify(body), 200

@bp.get("/lojas")
@bp.get("/lojas/")
def stores():
    payload = dict(
        filters={
            "numero_celular": request.args.get("numero_celular"),
            "data_captura_from": request.args.get("data_captura_from"),
            "data_captura_to": request.args.get("data_captura_to"),
            "tipo_cupom": request.args.get("tipo_cupom"),
            "tipo_loja": request.args.get("tipo_loja"),
            "local_captura": request.args.get("local_captura"),
            "latitude": request.args.get("latitude"),
            "longitude": request.args.get("longitude"),
            "nome_loja": request.args.get("nome_loja"),
            "endereco_loja": request.args.get("endereco_loja"),
            "valor_compra_min": _float(request.args.get("valor_compra_min")),
            "valor_compra_max": _float(request.args.get("valor_compra_max")),
            "valor_cupom_min": _float(request.args.get("valor_cupom_min")),
            "valor_cupom_max": _float(request.args.get("valor_cupom_max")),
        },
        cursor=_int(request.args.get("cursor")),
        limit=_limit(),
        fields=request.args.get("fields"),
        sort_by=request.args.get("sort_by","id"),
        sort_dir=request.args.get("sort_dir","asc"),
        q=request.args.get("q"),
    )
    body = stores_ctrl(**payload)
    return jsonify(body), 200

@bp.get("/transacoes")
@bp.get("/transacoes/")
def transactions():
    payload = dict(
        filters={
            "celular": request.args.get("celular"),
            "data_from": request.args.get("data_from"),
            "data_to": request.args.get("data_to"),
            "hora_from": request.args.get("hora_from"),
            "hora_to": request.args.get("hora_to"),
            "nome_estabelecimento": request.args.get("nome_estabelecimento"),
            "bairro_estabelecimento": request.args.get("bairro_estabelecimento"),
            "categoria_estabelecimento": request.args.get("categoria_estabelecimento"),
            "id_campanha": request.args.get("id_campanha"),
            "id_cupom": request.args.get("id_cupom"),
            "tipo_cupom": request.args.get("tipo_cupom"),
            "produto": request.args.get("produto"),
            "valor_cupom_min": _float(request.args.get("valor_cupom_min")),
            "valor_cupom_max": _float(request.args.get("valor_cupom_max")),
            "repasse_picmoney_min": _float(request.args.get("repasse_picmoney_min")),
            "repasse_picmoney_max": _float(request.args.get("repasse_picmoney_max")),
        },
        cursor=_int(request.args.get("cursor")),
        limit=_limit(),
        fields=request.args.get("fields"),
        sort_by=request.args.get("sort_by","id"),
        sort_dir=request.args.get("sort_dir","asc"),
        q=request.args.get("q"),
    )
    body = transactions_ctrl(**payload)
    return jsonify(body), 200
