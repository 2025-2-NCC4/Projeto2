from models import list_players, list_simulations, list_stores, list_transactions

def players_ctrl(**kw):
    data, _ = list_players(**kw)
    return data

def simulations_ctrl(**kw):
    data, _ = list_simulations(**kw)
    return data

def stores_ctrl(**kw):
    data, _ = list_stores(**kw)
    return data

def transactions_ctrl(**kw):
    data, _ = list_transactions(**kw)
    return data
