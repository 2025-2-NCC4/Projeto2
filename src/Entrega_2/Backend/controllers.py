from models import buscar_base_lojas, buscar_base_simulacao, buscar_base_players, buscar_base_transacoes


def listar_base_players():
    dados = buscar_base_players()
    return dados, 200

def listar_base_simulacao():
    dados = buscar_base_simulacao()
    return dados, 200

def listar_base_transacoes():
    dados = buscar_base_transacoes()
    return dados, 200

def listar_base_lojas():
    dados = buscar_base_lojas()
    return dados, 200