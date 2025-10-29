# ler_collun.py
import sqlite3, json, os

DB_PATH = r"C:\Users\dudal\OneDrive\Documentos\GitHub\Projeto2\src\Entrega_2\Backend\data\picmoney.db"
INCLUDE_VIEWS = False
OUTPUT_FORMAT = "json"  # opções: "text" ou "json"

def get_conn(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"DB não encontrado: {path}")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def list_tables(conn, include_views=False):
    if include_views:
        rows = conn.execute("""
            SELECT name, type FROM sqlite_master 
            WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'
            ORDER BY type, name
        """).fetchall()
    else:
        rows = conn.execute("""
            SELECT name, type FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()
    return [(r["name"], r["type"]) for r in rows]

def table_info(conn, table):
    rows = conn.execute(f"PRAGMA table_info('{table}')").fetchall()
    return [{"cid": r["cid"], "name": r["name"], "type": r["type"], "notnull": r["notnull"], 
             "dflt_value": r["dflt_value"], "pk": r["pk"]} for r in rows]

def as_text(schema):
    lines = []
    for t in schema:
        lines.append(f"[{t['type'].upper()}] {t['name']}")
        for c in t["columns"]:
            nn = "NOT NULL" if c["notnull"] else "NULL"
            pk = " PK" if c["pk"] else ""
            dv = f" DEFAULT {c['dflt_value']}" if c["dflt_value"] is not None else ""
            lines.append(f"  - {c['name']} : {c['type']} {nn}{pk}{dv}")
        lines.append("")
    return "\n".join(lines).strip()

def main():
    conn = get_conn(DB_PATH)
    try:
        objs = list_tables(conn, include_views=INCLUDE_VIEWS)
        schema = []
        for name, typ in objs:
            cols = table_info(conn, name)
            schema.append({"name": name, "type": typ, "columns": cols})
        if OUTPUT_FORMAT == "json":
            print(json.dumps(schema, ensure_ascii=False, indent=2))
        else:
            print(as_text(schema))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
