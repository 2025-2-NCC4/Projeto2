from data.db import get_connection

def buscar_base_players():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM playeres")
    dados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return dados

def buscar_base_simulacao():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM simulations")
    dados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return dados

def buscar_base_transacoes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    dados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return dados

def buscar_base_lojas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stores")
    dados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return dados