#!/usr/bin/env python3
"""Lucidia CLI - Terminal OS for BlackRoad"""

import click
import sqlite3
import os
from pathlib import Path

DB_PATH = Path.home() / ".blackroad" / "index" / "blackroad.db"

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            url TEXT,
            description TEXT,
            metadata TEXT,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_type ON resources(type)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_name ON resources(name)')
    conn.commit()
    conn.close()

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Lucidia CLI - Terminal OS for BlackRoad"""
    init_db()
    if ctx.invoked_subcommand is None:
        click.echo("🌙 Lucidia interactive mode coming soon...")
        click.echo("Run 'lucidia --help' for commands")

@cli.command()
def chat():
    """Agent chat interface"""
    click.echo("💬 Lucidia chat coming soon...")

@cli.group()
def index():
    """Index BlackRoad ecosystem"""
    pass

@index.command('status')
def index_status():
    """Show index stats"""
    conn = get_db()
    counts = conn.execute('''
        SELECT type, COUNT(*) as count 
        FROM resources 
        GROUP BY type
    ''').fetchall()
    conn.close()
    
    if not counts:
        click.echo("Index empty. Run 'lucidia index github' to start.")
        return
    
    click.echo("📊 Index Status:")
    for row in counts:
        click.echo(f"  {row['type']}: {row['count']}")

if __name__ == '__main__':
    cli()

# Add to index group
#from index_github import index_github as do_index_github

@index.command('github')
def index_github_cmd():
    """Index GitHub repos"""
    do_index_github()

@index.command('search')
@click.argument('query')
def index_search(query):
    """Search indexed resources"""
    conn = get_db()
    results = conn.execute('''
        SELECT type, name, url, description 
        FROM resources 
        WHERE name LIKE ? OR description LIKE ?
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    
    if not results:
        click.echo("No results found.")
        return
    
    for row in results:
        click.echo(f"[{row['type']}] {row['name']}")
        if row['description']:
            click.echo(f"  {row['description'][:60]}")
        click.echo(f"  {row['url']}")
