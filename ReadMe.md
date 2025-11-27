# CyBank

Lightweight Python banking application providing CLI tools and backend services for managing users, accounts, and transactions.

**Status:** Minimal CLI-based project. Core modules live under `backend/`, CLI tools under `cli/`, and shared helpers in `utils/`.

**Quick Start**

- **Python version:** 3.8+ recommended
- Create a virtual environment and activate it (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- If you add third-party dependencies, install them with:

```
pip install -r requirements.txt
```

**Database**

This project uses a simple SQLite backend. The database schema is in `backend/schema.sql` and database access helpers are in `backend/db.py`.

To initialize the database, apply `backend/schema.sql` (for example using the `sqlite3` CLI or a small Python script that imports `backend/db.py`).

Project structure

- `backend/`
	- `db.py` — database connection and helper functions
	- `schema.sql` — SQL schema to create required tables
	- `models/` — data model classes
		- `account.py` — account model
		- `transaction.py` — transaction model
		- `user.py` — user model
	- `services/` — business logic / data access services
		- `account_service.py` — account-related operations
		- `admin_service.py` — admin utilities and operations
		- `category_service.py` — categorization helpers for transactions
		- `transaction_service.py` — create/query transactions
		- `user_service.py` — user creation and lookup

- `cli/`
	- `main.py` — application entrypoint (runs CLI)
	- `user_cli.py` — commands for user management
	- `account_cli.py` — commands for account management
	- `transaction_cli.py` — commands for transaction operations
	- `admin_cli.py` — admin utilities

- `utils/`
	- `auth.py` — authentication helpers
	- `config.py` — configuration values
	- `helpers.py` — shared utility functions

Usage

- Run the CLI entrypoint:

```
python -m cli.main
```

- Or run specific CLI scripts directly (examples):

```
python cli/user_cli.py create --name "Alice"
python cli/account_cli.py open --user-id 1 --type checking
python cli/transaction_cli.py add --account-id 1 --amount -25.00 --category groceries
```

(Replace the above commands with the exact flags used by each script — these are example invocations.)

Components

- Models: simple domain objects representing `User`, `Account`, and `Transaction`.
- Services: encapsulate business logic and data access — use these from the CLI or future GUI code.
- Utils: configuration and auth helpers that are reused across the project.

Developing & Extending

- If you plan to add a GUI (Tkinter or other), the current structure keeps logic in services/models so a GUI can be added without changing core business code.
- Consider adding a `requirements.txt` if you introduce third-party packages (e.g., `click` for CLI, `sqlalchemy` for DB ORM, or `tkinter` wrappers).

Testing & Linting

- There are no tests included yet. Add tests under a `tests/` folder and use `pytest` for running them.
- Optionally add `pre-commit` hooks or `black`/`flake8` for consistent formatting.

Contributing

- Fork the repo, create a branch for your feature or bugfix, then open a pull request describing your change.

License

Add a license file if you intend to publish this project (for example `LICENSE` with an MIT or Apache 2.0 license).

Contact / Notes

- This README was generated from the repository layout. If you'd like, I can:
	- add a `requirements.txt` based on imports,
	- initialize the SQLite DB with `backend/schema.sql`, or
	- create a short usage guide showing the actual CLI flags by inspecting the CLI scripts.

**Progress**

- **Fixed:** `backend/models/account.py` and `backend/models/transaction.py` had dataclass field-order issues (default-valued fields before non-defaults). Those were reordered so dataclasses initialize correctly.
- **Updated CLI:** `cli/main.py` was updated to access `User`, `Account`, and `Transaction` objects via attributes (e.g., `user.full_name`, `acct.account_id`, `txn.amount`) instead of dict-style subscripting.
- **Verified:** I ran the CLI end-to-end (register → login → create account → deposit → withdraw → list transactions) using PowerShell and confirmed the flow works and balances update correctly.
- **Files touched:** `backend/models/account.py`, `backend/models/transaction.py`, and `cli/main.py`.