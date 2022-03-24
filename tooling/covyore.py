#!/usr/bin/python3

from pathlib import Path
import sqlite3
from typing import Optional
import subprocess
import json
import click


class DiminishingCoverageError(Exception):
    pass
class DB:
    def __init__(self, datafile: str = "covyore.db") -> None:
        file_ = Path(__file__).parent.parent / Path(datafile)
        new_db = not file_.exists()
        
        self.con = sqlite3.connect(file_)
        if new_db:
            self.init_table()

    def init_table(self):
        
        connection = self.con
        connection.execute("CREATE TABLE hashes (hashid TEXT PRIMARY KEY, coverage REAL)")
        
    def insert_coverage(self, hashid: str, coverage: float):
        with self.con as con:
            cursor = con.cursor()
            
            cursor.execute(
                """
                INSERT OR REPLACE INTO hashes
                (hashid, coverage)
                VALUES (?,?)
                """,
                (hashid, coverage))
    
    def select_coverage(self, hashid: str):
        with self.con as con:
            cursor = con.cursor()
            
            return cursor.execute("SELECT coverage FROM hashes WHERE hashid=?", [hashid]).fetchone()[0]
    def __enter__(self):
        self.con = self.con.__enter__()
        return self
    
    def __exit__(self, *args, **kwargs):
        self.con.__exit__(*args, **kwargs)

def get_commit_count(revision: str = "HEAD"):
    output = subprocess.run(["git", "rev-list", "--count", revision], capture_output=True)
    
    return int(output.stdout.decode(encoding="utf8"))

def get_commit_hash(level: Optional[int] = None):
    if level and level > 0:
        head = f"head^{level}"
    else:
        head = "head"
    
    output = subprocess.run(["git", "rev-parse", head], capture_output=True)
    result = output.stdout.decode(encoding="utf8").strip()
    return result

def get_total_coverage():
    output = subprocess.run(["coverage", "json", "-o", "/dev/stdout"], capture_output=True)
    data = output.stdout.decode(encoding="utf8")[:-33]
    if data == b"No data to report.\n":
        return 0.0
    data_dict = json.loads(data)
    return round(float(data_dict["totals"]["percent_covered"]),6)


def calc_change(new: float, old: float):
    if old < 1e-5:
        return new
    if new > old:
        return (new - old) / old
    else:
        return (old - new) / new


@click.group()
def cli():
    pass

@cli.command("check")
def check_coverage():
    count = get_commit_count()
    
    if count > 1:
        db = DB()
        
        current_hash = get_commit_hash()
        previous_hash = get_commit_hash(level=1)
        current_coverage = float(db.select_coverage(current_hash) or 0)
        previous_coverage = float(db.select_coverage(previous_hash) or 0)
        change = calc_change(current_coverage, previous_coverage)
        
        if current_coverage < previous_coverage:
            click.echo(f"Current code coverage has decreased. Loss: {change}%")
            raise DiminishingCoverageError
        if current_coverage > previous_coverage:
            click.echo(f"Current code coverage has increased. Win: {change}%")
        else:
            click.echo(f"Current code coverage is: {current_coverage}%")
        
@cli.command("update")
def insert_coverage():
    
    db = DB()
    
    current_hash = get_commit_hash().strip()
    
    current_coverage = get_total_coverage()
    
    db.insert_coverage(current_hash, current_coverage)
    res = {current_hash:current_coverage}
    click.echo(res)

if __name__ == '__main__':
    cli()
