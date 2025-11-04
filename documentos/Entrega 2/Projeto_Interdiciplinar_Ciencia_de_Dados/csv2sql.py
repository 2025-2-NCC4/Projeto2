# -*- coding: utf-8 -*-
import argparse
import sqlite3
import pandas as pd
from pathlib import Path
import re
import csv

# ========================
# Configuração de caminhos
# ========================
SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_TABLES = {
    "players":      SCRIPT_DIR / "base_players.csv",
    "transactions": SCRIPT_DIR / "base_transacoes.csv",
    "stores":       SCRIPT_DIR / "base_lojas.csv",
    "simulations":  SCRIPT_DIR / "base_simulacao.csv",
}

# Uso: "auto" para detecção; ou force com valores explícitos
DEFAULT_ENCODING = "auto"   # utf-8-sig, utf-8, cp1252, latin-1, auto
DEFAULT_SEP = "auto"        # ; , \t |, auto
DEFAULT_DECIMAL = "auto"    # , . auto


# ========================
# Utilitários
# ========================
def map_dtype_to_sql(dtype) -> str:
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    if pd.api.types.is_float_dtype(dtype):
        return "REAL"
    if pd.api.types.is_bool_dtype(dtype):
        return "INTEGER"
    return "TEXT"


def quote_ident(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def sniff_delimiter_and_decimal(sample_txt: str):
    candidates = [",", ";", "\t", "|"]

    try:
        dialect = csv.Sniffer().sniff(sample_txt, delimiters="".join(candidates))
        delimiter = dialect.delimiter
    except Exception:
        first_line = sample_txt.splitlines()[0] if sample_txt else ""
        counts = {c: first_line.count(c) for c in candidates}
        delimiter = max(counts, key=counts.get) if counts else ","

    comma_dec = len(re.findall(r"\d,\d", sample_txt))
    dot_dec = len(re.findall(r"\d\.\d", sample_txt))
    decimal = "," if comma_dec > dot_dec else "."

    return delimiter, decimal


def read_csv_smart(path: str, encoding: str, sep: str, decimal: str) -> pd.DataFrame:
    enc_candidates = (
        ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
        if (not encoding or str(encoding).lower() == "auto")
        else [encoding]
    )

    last_err = None
    for enc in enc_candidates:
        try:
            with open(path, "r", encoding=enc, errors="strict") as fh:
                sample = fh.read(64 * 1024)

            sniff_sep, sniff_dec = sniff_delimiter_and_decimal(sample)
            use_sep = sniff_sep if (not sep or str(sep).lower() == "auto") else sep
            use_dec = sniff_dec if (not decimal or str(decimal).lower() == "auto") else decimal

            df = pd.read_csv(path, encoding=enc, sep=use_sep, decimal=use_dec, engine="python")

            # Fallback se veio tudo numa coluna
            if df.shape[1] == 1:
                for alt in [";", ",", "\t", "|"]:
                    if alt == use_sep:
                        continue
                    try_alt = pd.read_csv(path, encoding=enc, sep=alt, decimal=use_dec, engine="python")
                    if try_alt.shape[1] > df.shape[1]:
                        df = try_alt
                        break

            # Remove "Unnamed"
            df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
            return df
        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(f"Falha ao ler '{path}'. Último erro: {last_err}")


def maybe_fix_mojibake(df: pd.DataFrame) -> pd.DataFrame:
    def fix_cell(x):
        if not isinstance(x, str):
            return x
        try:
            y = x.encode("latin1").decode("utf-8")
            return y if y != x else x
        except Exception:
            return x

    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            sample = " ".join(map(lambda v: v if isinstance(v, str) else "", df[col].head(50).tolist()))
            if "Ã" in sample or "�" in sample:
                df[col] = df[col].map(fix_cell)
    return df


# ========================
# DDL + INSERT
# ========================
def create_table_from_df(conn, table_name: str, df: pd.DataFrame):
    """
    Cria a tabela preservando nomes originais do CSV.
    Se não houver 'id', cria 'id INTEGER PRIMARY KEY AUTOINCREMENT'.
    Derruba a tabela se existir.
    """
    df = df.copy()

    cols = list(df.columns)
    has_id = any(str(c).lower() == "id" for c in cols)

    col_defs = []
    if not has_id:
        col_defs.append('"id" INTEGER PRIMARY KEY AUTOINCREMENT')

    for col in cols:
        sqltype = map_dtype_to_sql(df[col].dtype)
        col_defs.append(f'{quote_ident(col)} {sqltype}')

    ddl = f'CREATE TABLE IF NOT EXISTS {quote_ident(table_name)} (\n  ' + ",\n  ".join(col_defs) + "\n);"
    cur = conn.cursor()
    cur.execute(f'DROP TABLE IF EXISTS {quote_ident(table_name)};')
    cur.execute(ddl)
    conn.commit()
    return df, has_id


def insert_df(conn, table_name: str, df: pd.DataFrame, has_id: bool):
    """
    Insere registros. Se 'id' não existia no CSV, a coluna será autogerada e não entra no INSERT.
    """
    cols = list(df.columns)  # apenas colunas do CSV
    placeholders = ", ".join(["?"] * len(cols))
    colnames_sql = ", ".join(quote_ident(c) for c in cols)
    sql = f'INSERT INTO {quote_ident(table_name)} ({colnames_sql}) VALUES ({placeholders})'

    values = [
        tuple(None if pd.isna(v) else v for v in row)
        for row in df[cols].itertuples(index=False, name=None)
    ]
    cur = conn.cursor()
    cur.executemany(sql, values)
    conn.commit()


def load_csv_to_table(conn, table_name: str, csv_path: str, encoding: str, sep: str, decimal: str, fix_mojibake: bool):
    csv_abs = Path(csv_path)
    if not csv_abs.is_absolute():
        csv_abs = (SCRIPT_DIR / csv_abs).resolve()

    print(f"[INFO] Tabela '{table_name}' <- CSV '{csv_abs}'")
    if not csv_abs.exists():
        raise FileNotFoundError(f"CSV não encontrado: {csv_abs}")

    df = read_csv_smart(str(csv_abs), encoding=encoding, sep=sep, decimal=decimal)

    if fix_mojibake:
        df = maybe_fix_mojibake(df)

    df, has_id = create_table_from_df(conn, table_name, df)
    insert_df(conn, table_name, df, has_id)


# ========================
# CLI
# ========================
def main():
    parser = argparse.ArgumentParser(
        description="Importa múltiplos CSVs para um SQLite .db (players, transactions, stores, simulations)."
    )
    parser.add_argument("--db", default="picmoney.db", help="Arquivo .db de saída (default: picmoney.db)")
    parser.add_argument("--encoding", default=DEFAULT_ENCODING, help="utf-8-sig, utf-8, cp1252, latin-1, auto")
    parser.add_argument("--sep", default=DEFAULT_SEP, help="Delimitador: ',', ';', '\\t', '|', ou 'auto'")
    parser.add_argument("--decimal", default=DEFAULT_DECIMAL, help="Separador decimal: '.', ',', ou 'auto'")
    parser.add_argument("--fix-mojibake", action="store_true", help="Tenta corrigir texto corrompido (Ã©/Ã£ etc.)")

    parser.add_argument("--players", help="Caminho para players.csv")
    parser.add_argument("--transactions", help="Caminho para transactions.csv")
    parser.add_argument("--stores", help="Caminho para stores.csv")
    parser.add_argument("--simulations", help="Caminho para simulations.csv")
    args = parser.parse_args()

    tables = DEFAULT_TABLES.copy()
    if args.players:      tables["players"] = args.players
    if args.transactions: tables["transactions"] = args.transactions
    if args.stores:       tables["stores"] = args.stores
    if args.simulations:  tables["simulations"] = args.simulations

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = (Path.cwd() / db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    try:
        for tname, csv_path in tables.items():
            load_csv_to_table(conn, tname, csv_path, args.encoding, args.sep, args.decimal, args.fix_mojibake)
        print(f"[OK] Importação concluída em '{db_path}'")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
