# Expense Tracker CLI

A command-line expense tracker built with pure Python (no external dependencies). Expenses are stored in a local SQLite database.

## Features
- Add, list, and delete expenses
- Filter by category or month
- Spending summary per category
- Export all data to CSV
- Input validation (positive amounts, date format)
- Unit tests with `unittest`

## Requirements
Python 3.8+

## Usage
```bash
python expense_tracker.py add 250 food -n "Lunch with friends"
python expense_tracker.py add 1200 travel -d 2026-11-10
python expense_tracker.py list
python expense_tracker.py list -c food -m 2026-11
python expense_tracker.py summary -m 2026-11
python expense_tracker.py delete 1
python expense_tracker.py export expenses.csv
```

Use `--db path/to/file.db` to choose a different database file.

## Run tests
```bash
python -m unittest -v
```

## Project structure
```
expense_tracker.py       # database layer + CLI
test_expense_tracker.py  # unit tests
README.md
```

## Possible improvements
- Monthly budgets and alerts
- Charts with matplotlib
- Web UI with Flask
