import argparse
import os
import re
import sqlite3
import unicodedata
import pandas as pd

# ---------- Config ----------
DEFAULT_TABLES = {
    "players": "base_de_dados/Base_Cadastral_de_Players.csv",
    "transactions": "base_de_dados/Base_de_Transacoes_e_Cupons_Capturados.csv",
    "stores": "base_de_dados/Base_Massa_de_Teste_com_Lojas_e_Valores.csv",
    "simulations": "base_de_dados/Base_Simulada_-_Pedestres_Av__Paulista.csv",
}

# Padrões brasileiros
DEFAULT_SEP = ";"       # separador mais comum no BR
DEFAULT_DECIMAL = ","   # vírgula decimal
DEFAULT_ENCODING = "auto"  # tenta detectar automaticamente

# ---------- Utils ----------
def snake_case(s: str) -> str:
    if not s:
        return s
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def map_dtype_to_sql(dtype) -> str:
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    if pd.api.types.is_float_dtype(dtype):
        return "REAL"
    if pd.api.types.is_bool_dtype(dtype):
        return "INTEGER"  # 0/1
    return "TEXT"  # datas e strings ficam TEXT

def read_csv_smart(path: str, encoding: str, sep: str, decimal: str) -> pd.DataFrame:
    """
    Lê CSV tentando encodings comuns no BR. Se encoding != 'auto', usa exatamente o informado.
    """
    tried = []
    if encoding and encoding.lower() != "auto":
        return pd.read_csv(path, encoding=encoding, sep=sep, decimal=decimal)

    # ordem de tentativa cobre >95% dos casos
    candidates = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
    last_err = None
    for enc in candidates:
        try:
            df = pd.read_csv(path, encoding=enc, sep=sep, decimal=decimal)
            # sanity check: se o cabeçalho tem mojibake óbvio, continue tentando
            header = " ".join(map(str, df.columns.tolist()))
            if "Ã" in header or "�" in header:
                tried.append((enc, "mojibake no header"))
                continue
            return df
        except Exception as e:
            last_err = e
            tried.append((enc, str(e)))
    raise RuntimeError(f"Falha ao ler '{path}' com encodings {tried}. Último erro: {last_err}")

def maybe_fix_mojibake(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tenta corrigir mojibake clássico (texto UTF-8 lido como Latin-1).
    Só mexe em colunas 'object' (strings).
    """
    def fix_cell(x):
        if not isinstance(x, str):
            return x
        try:
            y = x.encode("latin1").decode("utf-8")
            # aplica fix apenas se realmente mudou
            return y if y != x else x
        except Exception:
            return x

    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            # atalho: se quase não há 'Ã' na coluna, pula
            sample = " ".join(map(lambda v: v if isinstance(v, str) else "", df[col].head(50).tolist()))
            if "Ã" in sample or "�" in sample:
                df[col] = df[col].map(fix_cell)
    return df

def create_table_from_df(conn, table_name: str, df: pd.DataFrame):
    df = df.copy()
    df.columns = [snake_case(str(c)) for c in df.columns]

    has_id = "id" in df.columns
    col_defs = []

    for col in df.columns:
        if col == "id":
            # se a coluna id for inteira => INTEGER PRIMARY KEY; senão TEXT PRIMARY KEY
            if pd.api.types.is_integer_dtype(df[col].dtype):
                col_defs.append('"id" INTEGER PRIMARY KEY')
            else:
                col_defs.append('"id" TEXT PRIMARY KEY')
        else:
            sqltype = map_dtype_to_sql(df[col].dtype)
            col_defs.append(f'"{col}" {sqltype}')

    if not has_id:
        col_defs.insert(0, 'id INTEGER PRIMARY KEY AUTOINCREMENT')

    ddl = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n  ' + ",\n  ".join(col_defs) + "\n);"
    cur = conn.cursor()
    cur.execute(f'DROP TABLE IF EXISTS "{table_name}";')
    cur.execute(ddl)
    conn.commit()
    return df, has_id

def insert_df(conn, table_name: str, df: pd.DataFrame, has_id: bool):
    cols = list(df.columns)  # insere todas as colunas do DF (id incluso se existir)
    placeholders = ", ".join(["?"] * len(cols))
    colnames_sql = ", ".join(f'"{c}"' for c in cols)
    sql = f'INSERT INTO "{table_name}" ({colnames_sql}) VALUES ({placeholders})'

    # normaliza NaN -> None para virarem NULL no SQLite
    values = [
        tuple(None if pd.isna(v) else v for v in row)
        for row in df[cols].itertuples(index=False, name=None)
    ]
    cur = conn.cursor()
    cur.executemany(sql, values)
    conn.commit()

def load_csv_to_table(conn, table_name: str, csv_path: str, encoding: str, sep: str, decimal: str, fix_mojibake: bool):
    print(f"[INFO] Tabela '{table_name}' <- CSV '{csv_path}'")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV não encontrado: {csv_path}")

    df = read_csv_smart(csv_path, encoding=encoding, sep=sep, decimal=decimal)
    # remove colunas Unnamed
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

    # correção opcional de mojibake
    if fix_mojibake:
        df = maybe_fix_mojibake(df)

    # DDL + INSERT
    df, has_id = create_table_from_df(conn, table_name, df)
    insert_df(conn, table_name, df, has_id)

def main():
    parser = argparse.ArgumentParser(description="Importa múltiplos CSVs para um único SQLite .db com 4 tabelas.")
    parser.add_argument("--db", default="picmoney.db", help="arquivo .db de saída (default: picmoney.db)")
    parser.add_argument("--encoding", default=DEFAULT_ENCODING, help="encoding dos CSVs (ex.: utf-8, utf-8-sig, cp1252, latin-1, auto)")
    parser.add_argument("--sep", default=DEFAULT_SEP, help=f"separador dos CSVs (default: '{DEFAULT_SEP}')")
    parser.add_argument("--decimal", default=DEFAULT_DECIMAL, help=f"separador decimal (default: '{DEFAULT_DECIMAL}')")
    parser.add_argument("--fix-mojibake", action="store_true", help="tenta corrigir texto corrompido (Ã©/Ã£ etc.)")
    parser.add_argument("--players", help="caminho players.csv")
    parser.add_argument("--transactions", help="caminho transactions.csv")
    parser.add_argument("--stores", help="caminho stores.csv")
    parser.add_argument("--simulations", help="caminho simulations.csv")
    args = parser.parse_args()

    tables = DEFAULT_TABLES.copy()
    if args.players: tables["players"] = args.players
    if args.transactions: tables["transactions"] = args.transactions
    if args.stores: tables["stores"] = args.stores
    if args.simulations: tables["simulations"] = args.simulations

    os.makedirs(os.path.dirname(args.db) or ".", exist_ok=True)

    conn = sqlite3.connect(args.db)
    try:
        for tname, csv_path in tables.items():
            load_csv_to_table(conn, tname, csv_path, args.encoding, args.sep, args.decimal, args.fix_mojibake)
        print(f"[OK] Importação concluída em '{args.db}'")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
