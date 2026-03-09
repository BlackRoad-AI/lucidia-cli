"""GitHub indexer for Lucidia CLI"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

DB_PATH = Path.home() / ".blackroad" / "index" / "blackroad.db"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ORGS = ["BlackRoad-OS", "blackroadio"]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_repos(org):
    if not requests:
        print("pip install requests")
        return []
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Error fetching {org}: {resp.status_code}")
            break
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def index_github():
    conn = get_db()
    conn.execute("DELETE FROM resources WHERE type = 'repo'")
    
    total = 0
    for org in ORGS:
        print(f"Indexing {org}...")
        repos = fetch_repos(org)
        for repo in repos:
            conn.execute('''
                INSERT INTO resources (type, name, url, description, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'repo',
                f"{org}/{repo['name']}",
                repo['html_url'],
                repo.get('description', ''),
                json.dumps({
                    'stars': repo['stargazers_count'],
                    'language': repo.get('language'),
                    'updated': repo['updated_at']
                })
            ))
        total += len(repos)
        print(f"  {len(repos)} repos")
    
    conn.commit()
    conn.close()
    print(f"✓ Indexed {total} repos")

if __name__ == '__main__':
    index_github()
