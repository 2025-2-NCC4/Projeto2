import os
import requests
import pandas as pd
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:5000/api")

def build_url(path, params=None):
    if params:
        query = urlencode({k: v for k, v in params.items() if v not in (None, '')})
        return f"{API_BASE}{path}?{query}"
    return f"{API_BASE}{path}"


def get_json_df(path, params=None, timeout=60):
    url = build_url(path, params)
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        return pd.DataFrame([data])
    else:
        return pd.DataFrame()
    
def get_all_json_df(
    path,
    base_params=None,
    limit=10000,
    offset_param="offset",
    limit_param="limit",
    timeout=60,
    max_pages=None,
):
    
    base_params = dict(base_params or {})
    dfs = []
    page = 0
    total_rows = 0

    while True:
        if max_pages is not None and page >= max_pages:
            break

        params = {**base_params, limit_param: limit, offset_param: page * limit}
        df_page = get_json_df(path, params=params, timeout=timeout)

        if df_page.empty:
            break

        dfs.append(df_page)
        total_rows += len(df_page)
        if len(df_page) < limit:
            break

        page += 1

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()