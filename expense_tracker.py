#!/usr/bin/env python3
"""Expense Tracker CLI - track spending from the terminal.

Uses only the Python standard library (argparse, sqlite3, csv).
"""
import argparse
import csv
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

DEFAULT_DB = Path.home() / ".expense_tracker.db"


class ExpenseDB:
    """Thin wrapper around a SQLite database of expenses."""

    def __init__(self, path=DEFAULT_DB):
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL CHECK (amount > 0),
                category TEXT NOT NULL,
                note TEXT DEFAULT '',
                spent_on TEXT NOT NULL
            )"""
        )
        self.conn.commit()

    def add(self, amount, category, note="", spent_on=None):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        spent_on = spent_on or date.today().isoformat()
        datetime.strptime(spent_on, "%Y-%m-%d")  # validate format
        cur = self.conn.execute(
            "INSERT INTO expenses (amount, category, note, spent_on) VALUES (?, ?, ?, ?)",
            (amount, category.lower().strip(), note, spent_on),
        )
        self.conn.commit()
        return cur.lastrowid

    def list(self, category=None, month=None):
        query, params = "SELECT * FROM expenses WHERE 1=1", []
        if category:
            query += " AND category = ?"
            params.append(category.lower().strip())
        if month:  # format YYYY-MM
            query += " AND substr(spent_on, 1, 7) = ?"
            params.append(month)
        query += " ORDER BY spent_on DESC, id DESC"
        return self.conn.execute(query, params).fetchall()

    def delete(self, expense_id):
        cur = self.conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def summary(self, month=None):
        query = "SELECT category, SUM(amount) AS total, COUNT(*) AS n FROM expenses"
        params = []
        if month:
            query += " WHERE substr(spent_on, 1, 7) = ?"
            params.append(month)
        query += " GROUP BY category ORDER BY total DESC"
        return self.conn.execute(query, params).fetchall()

    def export_csv(self, filename):
        rows = self.list()
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "amount", "category", "note", "date"])
            for r in rows:
                writer.writerow([r["id"], r["amount"], r["category"], r["note"], r["spent_on"]])
        return len(rows)


def print_table(rows):
    if not rows:
        print("No expenses found.")
        return
    print(f"{'ID':<4} {'Date':<11} {'Category':<12} {'Amount':>10}  Note")
    print("-" * 55)
    for r in rows:
        print(f"{r['id']:<4} {r['spent_on']:<11} {r['category']:<12} {r['amount']:>10.2f}  {r['note']}")
    print("-" * 55)
    print(f"{'Total':<28} {sum(r['amount'] for r in rows):>10.2f}")


def build_parser():
    p = argparse.ArgumentParser(description="Simple CLI expense tracker")
    p.add_argument("--db", default=str(DEFAULT_DB), help="path to database file")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add", help="add an expense")
    a.add_argument("amount", type=float)
    a.add_argument("category")
    a.add_argument("-n", "--note", default="")
    a.add_argument("-d", "--date", help="YYYY-MM-DD (default: today)")

    l = sub.add_parser("list", help="list expenses")
    l.add_argument("-c", "--category")
    l.add_argument("-m", "--month", help="YYYY-MM")

    d = sub.add_parser("delete", help="delete an expense by id")
    d.add_argument("id", type=int)

    s = sub.add_parser("summary", help="spending per category")
    s.add_argument("-m", "--month", help="YYYY-MM")

    e = sub.add_parser("export", help="export all expenses to CSV")
    e.add_argument("filename", nargs="?", default="expenses.csv")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    db = ExpenseDB(args.db)
    try:
        if args.command == "add":
            new_id = db.add(args.amount, args.category, args.note, args.date)
            print(f"Added expense #{new_id}")
        elif args.command == "list":
            print_table(db.list(args.category, args.month))
        elif args.command == "delete":
            print("Deleted." if db.delete(args.id) else "No expense with that id.")
        elif args.command == "summary":
            rows = db.summary(args.month)
            if not rows:
                print("No expenses found.")
            for r in rows:
                print(f"{r['category']:<12} {r['total']:>10.2f}  ({r['n']} expenses)")
        elif args.command == "export":
            print(f"Exported {db.export_csv(args.filename)} expenses to {args.filename}")
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
