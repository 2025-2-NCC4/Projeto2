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