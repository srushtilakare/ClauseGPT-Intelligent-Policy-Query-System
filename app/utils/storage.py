import os
import requests

DATA_DIR = os.path.join(os.getcwd(), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def download_blob(url: str, out_path: str) -> str:
    """Download a file from URL to out_path and return path."""
    resp = requests.get(url)
    resp.raise_for_status()
    with open(out_path, 'wb') as f:
        f.write(resp.content)
    return out_path