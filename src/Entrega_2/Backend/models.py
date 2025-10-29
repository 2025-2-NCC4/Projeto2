from data.db import get_connection

PLAYER_FIELDS = {"id","celular","data_nascimento","idade","sexo","cidade_residencial","bairro_residencial","cidade_trabalho","bairro_trabalho","cidade_escola","bairro_escola","categoria_frequentada"}
SIM_FIELDS = {"id","celular","data","horario","local","latitude","longitude","tipo_celular","modelo_celular","possui_app_picmoney","data_ultima_compra","ultimo_tipo_cupom","ultimo_valor_capturado","ultimo_tipo_loja","idade","sexo"}
STORE_FIELDS = {"id","numero_celular","data_captura","tipo_cupom","tipo_loja","local_captura","latitude","longitude","nome_loja","endereco_loja","valor_compra","valor_cupom"}
TX_FIELDS = {"id","celular","data","hora","nome_estabelecimento","bairro_estabelecimento","categoria_estabelecimento","id_campanha","id_cupom","tipo_cupom","produto","valor_cupom","repasse_picmoney"}

def _select_clause(req_fields, allowed):
    if not req_fields:
        return "*"
    cols = [c for c in req_fields.split(",") if c in allowed]
    return ",".join(cols) if cols else "*"

def _order_clause(sort_by, sort_dir, allowed):
    if sort_by not in allowed:
        return ""
    d = "DESC" if str(sort_dir).lower() == "desc" else "ASC"
    return f" ORDER BY {sort_by} {d}"

def _paginate_and_return(rows, limit):
    data = [dict(r) for r in rows[:limit]]
    next_cursor = data[-1]["id"] if len(rows) > limit and data else None
    return data, next_cursor

def list_players(filters, cursor=None, limit=100, fields=None, sort_by="id", sort_dir="asc", q=None):
    conn = get_connection()
    sel = _select_clause(fields, PLAYER_FIELDS)
    where, params = [], []
    for k, v in filters.items():
        if k in PLAYER_FIELDS and v is not None and v != "":
            where.append(f"{k} = ?"); params.append(v)
    if q:
        where.append("(celular LIKE ? OR sexo LIKE ? OR cidade_residencial LIKE ? OR cidade_trabalho LIKE ? OR cidade_escola LIKE ? OR categoria_frequentada LIKE ?)")
        params += [f"%{q}%"]*6
    if "idade_min" in filters and filters["idade_min"] is not None:
        where.append("idade >= ?"); params.append(filters["idade_min"])
    if "idade_max" in filters and filters["idade_max"] is not None:
        where.append("idade <= ?"); params.append(filters["idade_max"])
    if "data_nascimento_from" in filters and filters["data_nascimento_from"]:
        where.append("data_nascimento >= ?"); params.append(filters["data_nascimento_from"])
    if "data_nascimento_to" in filters and filters["data_nascimento_to"]:
        where.append("data_nascimento <= ?"); params.append(filters["data_nascimento_to"])
    if cursor is not None:
        where.append("id > ?"); params.append(cursor)
    sql = f"SELECT {sel} FROM players"
    if where: sql += " WHERE " + " AND ".join(where)
    sql += _order_clause(sort_by, sort_dir, PLAYER_FIELDS | {"id"})
    params.append(limit + 1); sql += " LIMIT ?"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return _paginate_and_return(rows, limit)

def list_simulations(filters, cursor=None, limit=100, fields=None, sort_by="id", sort_dir="asc", q=None):
    conn = get_connection()
    sel = _select_clause(fields, SIM_FIELDS)
    where, params = [], []
    for k, v in filters.items():
        if k in SIM_FIELDS and v is not None and v != "":
            where.append(f"{k} = ?"); params.append(v)
    if "data_from" in filters and filters["data_from"]:
        where.append("data >= ?"); params.append(filters["data_from"])
    if "data_to" in filters and filters["data_to"]:
        where.append("data <= ?"); params.append(filters["data_to"])
    if "data_ultima_compra_from" in filters and filters["data_ultima_compra_from"]:
        where.append("data_ultima_compra >= ?"); params.append(filters["data_ultima_compra_from"])
    if "data_ultima_compra_to" in filters and filters["data_ultima_compra_to"]:
        where.append("data_ultima_compra <= ?"); params.append(filters["data_ultima_compra_to"])
    if "ultimo_valor_capturado_min" in filters and filters["ultimo_valor_capturado_min"] is not None:
        where.append("CAST(ultimo_valor_capturado AS REAL) >= ?"); params.append(filters["ultimo_valor_capturado_min"])
    if "ultimo_valor_capturado_max" in filters and filters["ultimo_valor_capturado_max"] is not None:
        where.append("CAST(ultimo_valor_capturado AS REAL) <= ?"); params.append(filters["ultimo_valor_capturado_max"])
    if "idade_min" in filters and filters["idade_min"] is not None:
        where.append("idade >= ?"); params.append(filters["idade_min"])
    if "idade_max" in filters and filters["idade_max"] is not None:
        where.append("idade <= ?"); params.append(filters["idade_max"])
    if q:
        where.append("(celular LIKE ? OR local LIKE ? OR tipo_celular LIKE ? OR modelo_celular LIKE ? OR ultimo_tipo_cupom LIKE ? OR ultimo_tipo_loja LIKE ?)")
        params += [f"%{q}%"]*6
    if cursor is not None:
        where.append("id > ?"); params.append(cursor)
    sql = f"SELECT {sel} FROM simulations"
    if where: sql += " WHERE " + " AND ".join(where)
    sql += _order_clause(sort_by, sort_dir, SIM_FIELDS | {"id"})
    params.append(limit + 1); sql += " LIMIT ?"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return _paginate_and_return(rows, limit)

def list_stores(filters, cursor=None, limit=100, fields=None, sort_by="id", sort_dir="asc", q=None):
    conn = get_connection()
    sel = _select_clause(fields, STORE_FIELDS)
    where, params = [], []
    for k, v in filters.items():
        if k in STORE_FIELDS and v is not None and v != "":
            where.append(f"{k} = ?"); params.append(v)
    if "data_captura_from" in filters and filters["data_captura_from"]:
        where.append("data_captura >= ?"); params.append(filters["data_captura_from"])
    if "data_captura_to" in filters and filters["data_captura_to"]:
        where.append("data_captura <= ?"); params.append(filters["data_captura_to"])
    for k_min, col in [("valor_compra_min","valor_compra"),("valor_cupom_min","valor_cupom")]:
        if k_min in filters and filters[k_min] is not None:
            where.append(f"CAST({col} AS REAL) >= ?"); params.append(filters[k_min])
    for k_max, col in [("valor_compra_max","valor_compra"),("valor_cupom_max","valor_cupom")]:
        if k_max in filters and filters[k_max] is not None:
            where.append(f"CAST({col} AS REAL) <= ?"); params.append(filters[k_max])
    if q:
        where.append("(nome_loja LIKE ? OR endereco_loja LIKE ? OR tipo_loja LIKE ? OR tipo_cupom LIKE ? OR local_captura LIKE ?)")
        params += [f"%{q}%"]*5
    if cursor is not None:
        where.append("id > ?"); params.append(cursor)
    sql = f"SELECT {sel} FROM stores"
    if where: sql += " WHERE " + " AND ".join(where)
    sql += _order_clause(sort_by, sort_dir, STORE_FIELDS | {"id"})
    params.append(limit + 1); sql += " LIMIT ?"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return _paginate_and_return(rows, limit)

def list_transactions(filters, cursor=None, limit=100, fields=None, sort_by="id", sort_dir="asc", q=None):
    conn = get_connection()
    sel = _select_clause(fields, TX_FIELDS)
    where, params = [], []
    for k, v in filters.items():
        if k in TX_FIELDS and v is not None and v != "":
            where.append(f"{k} = ?"); params.append(v)
    if "data_from" in filters and filters["data_from"]:
        where.append("data >= ?"); params.append(filters["data_from"])
    if "data_to" in filters and filters["data_to"]:
        where.append("data <= ?"); params.append(filters["data_to"])
    if "hora_from" in filters and filters["hora_from"]:
        where.append("hora >= ?"); params.append(filters["hora_from"])
    if "hora_to" in filters and filters["hora_to"]:
        where.append("hora <= ?"); params.append(filters["hora_to"])
    if "valor_cupom_min" in filters and filters["valor_cupom_min"] is not None:
        where.append("CAST(valor_cupom AS REAL) >= ?"); params.append(filters["valor_cupom_min"])
    if "valor_cupom_max" in filters and filters["valor_cupom_max"] is not None:
        where.append("CAST(valor_cupom AS REAL) <= ?"); params.append(filters["valor_cupom_max"])
    if "repasse_picmoney_min" in filters and filters["repasse_picmoney_min"] is not None:
        where.append("CAST(repasse_picmoney AS REAL) >= ?"); params.append(filters["repasse_picmoney_min"])
    if "repasse_picmoney_max" in filters and filters["repasse_picmoney_max"] is not None:
        where.append("CAST(repasse_picmoney AS REAL) <= ?"); params.append(filters["repasse_picmoney_max"])
    if q:
        where.append("(nome_estabelecimento LIKE ? OR categoria_estabelecimento LIKE ? OR tipo_cupom LIKE ? OR produto LIKE ?)")
        params += [f"%{q}%"]*4
    if cursor is not None:
        where.append("id > ?"); params.append(cursor)
    sql = f"SELECT {sel} FROM transactions"
    if where: sql += " WHERE " + " AND ".join(where)
    sql += _order_clause(sort_by, sort_dir, TX_FIELDS | {"id","data","hora"})
    params.append(limit + 1); sql += " LIMIT ?"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return _paginate_and_return(rows, limit)
