# 💰 Sunset Wallet — Personal Expense & Budget Tracker

A full-stack **Flask** web application that lets you record daily expenses,
organise them into categories, define monthly budgets, and see spending
summaries — built for the "Personal Expense & Budget Tracker" internship
project brief (Day 2/4).

> Live preview: run it locally in under 2 minutes — see **Run Locally** below.

---

## 1. What is this project, in plain words?

Think of it as a mini "Google Pay statement + budgeting app" that you host
yourself:

- Every time you spend money, you **log it** — date, category (Food,
  Transport, Bills, etc.), amount, how you paid, and an optional note.
- You can set a **monthly budget**, either as one overall limit or a
  separate limit per category (e.g. "₹1500 for Food in September").
- The app automatically works out how much you've spent, breaks it down by
  category, and shows you — with animated progress rings and bars — how
  close you are to each budget limit.
- A **Summary** page gives you charts: a pie chart of where your money went
  this month, and a 6-month trend line of total spending.

There is **no external database** — everything is stored in two simple
JSON files (`data/expenses.json` and `data/budgets.json`), which satisfies
the brief's "CSV or JSON data storage" requirement and makes the project
easy to inspect, back up, or move anywhere with zero setup.

---

## 2. How it was built — the short version

1. **Backend first.** I designed two plain Python classes, `Expense` and
   `Budget` (in `models.py`), each responsible for validating its own data
   (correct date format, amount > 0, category from a fixed list, etc.) and
   converting itself to/from a dictionary for storage.
2. **Storage layer.** A single reusable `JSONRepository` class
   (`repository.py`) handles reading/writing a list of records to a JSON
   file, generating new IDs, and basic CRUD (create, read, update, delete).
   Both `Expense` and `Budget` data use the *same* repository class — no
   duplicated file-handling code.
3. **Web layer.** `app.py` wires everything together with Flask routes:
   pages to list/add/edit/delete expenses and budgets, a dashboard, and a
   summary/report page, plus a small JSON API endpoint (`/api/summary`)
   that returns the same numbers the dashboard uses.
4. **Front end.** Each page is a Jinja2 template extending a shared
   `base.html` (top navbar, flash-message toasts, footer). The visual
   design — "Sunset Wallet" — uses a warm peach→coral→purple gradient
   background, frosted-glass ("glassmorphism") cards, animated SVG budget
   rings, Chart.js charts, scroll-reveal animations, button ripple
   effects, and a confetti burst when you successfully log an expense.
5. **Testing.** Before packaging, every route and form was exercised with
   Flask's built-in test client (`app.test_client()`) — including invalid
   input rejection, duplicate-budget rejection, search/filter, and 404
   handling — to make sure nothing was broken.

---

## 3. Architecture

### 3.1 High-level diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser (Client)                     │
│  HTML + CSS (Sunset Wallet theme) + Vanilla JS + Chart.js     │
└───────────────▲───────────────────────────────┬──────────────┘
                 │ renders                        │ HTTP requests
                 │ templates                       │ (GET / POST forms)
┌────────────────┴───────────────────────────────▼──────────────┐
│                         Flask Application (app.py)              │
│  Routes: /  /expenses  /expenses/add  /expenses/<id>/edit       │
│          /expenses/<id>/delete  /budgets  /budgets/add  ...     │
│          /summary   /api/summary                                │
└────────────────▲───────────────────────────────┬──────────────┘
                 │ validate()                      │ to_dict()/from dict
┌────────────────┴───────────────────────────────▼──────────────┐
│              Domain Models (models.py)                          │
│  Expense(date, category, amount, description, payment_method)   │
│  Budget(month, category, limit_amount)                          │
└────────────────▲───────────────────────────────┬──────────────┘
                 │ add()/update()/delete()/search()│
┌────────────────┴───────────────────────────────▼──────────────┐
│          JSONRepository (repository.py)                         │
│  Thread-safe read/write of a list of dict records to disk        │
└────────────────▲───────────────────────────────┬──────────────┘
                 │                                 │
        data/expenses.json                 data/budgets.json
```

### 3.2 Backend

| Layer | File | Responsibility |
|---|---|---|
| Entry point | `app.py` | Flask routes, request handling, flash messages, aggregation (totals, category breakdown, budget % used) |
| Domain models | `models.py` | `Expense` / `Budget` classes — field validation, fixed category list, `to_dict()` |
| Persistence | `repository.py` | Generic `JSONRepository` — CRUD against a JSON file, auto-incrementing IDs, thread lock for safe writes |
| Data | `data/expenses.json`, `data/budgets.json` | The actual stored records (comes pre-seeded with sample data) |

Key backend design decisions:

- **Why a generic `JSONRepository` instead of two separate storage
  classes?** Both `Expense` and `Budget` need the exact same operations
  (list all, get by id, add, update, delete, search). Writing one generic,
  well-tested class and reusing it for both avoids duplicated bugs and
  follows the **DRY** principle and the **Repository design pattern**
  (separating "how data is stored" from "what the data means").
- **Why JSON and not SQLite/a real database?** The brief explicitly asks
  for CSV/JSON storage to practice **file handling**. JSON also keeps
  numbers as real numbers and nested structures intact (unlike CSV), and
  the whole dataset can be opened and read by a human in any text editor.
- **Validation lives in the model, not the route.** `Expense.validate()`
  and `Budget.validate()` raise a `ValueError` with a clear message if
  something is wrong (bad date, negative amount, invalid category). The
  Flask route just catches that error and flashes it to the user — this
  keeps business rules in one place instead of scattered across routes.
- **Thread safety.** `JSONRepository` wraps every write in a
  `threading.Lock()` so two near-simultaneous requests can't corrupt the
  JSON file.

### 3.3 Frontend

| Element | Technology |
|---|---|
| Templating | Jinja2 (`{% extends %}` / `{% block %}` inheritance from `base.html`) |
| Styling | Hand-written CSS3 — CSS custom properties, gradients, `backdrop-filter` glassmorphism, keyframe animations |
| Charts | Chart.js (doughnut chart, pie chart, line chart) |
| Icons | Font Awesome 6 |
| Fonts | Google Fonts — Poppins (body) + Fraunces (headings) |
| Interactivity | Vanilla JavaScript — no frontend framework |

Visual/animation features (all implemented in plain CSS/JS, no external
animation library):

- Animated gradient blob background with floating coin icons
- Frosted-glass ("glassmorphism") cards with soft shadows
- Scroll-reveal animation using `IntersectionObserver`
- Animated count-up numbers on the dashboard stat cards
- Animated circular **SVG budget progress ring** (`stroke-dashoffset`
  transition) and animated horizontal progress bars per category
- Toast-style flash messages that slide in, auto-dismiss with a shrinking
  progress bar, and can be closed manually
- Button ripple-click effect
- A **confetti burst** when an expense is added successfully
- Responsive top navbar that collapses into a hamburger menu on mobile

---

## 4. Folder structure

```
expense_budget_tracker/
├── app.py                  # Flask routes & aggregation logic
├── models.py                # Expense & Budget classes + validation
├── repository.py             # Generic JSON repository (CRUD)
├── requirements.txt
├── .gitignore
├── .gitattributes            # Makes GitHub show "Python" as the main language
├── data/
│   ├── expenses.json          # Seeded sample expense records
│   └── budgets.json           # Seeded sample budget records
├── static/
│   ├── css/style.css          # "Sunset Wallet" theme
│   └── js/script.js           # Animations, charts, counters, confetti
└── templates/
    ├── base.html               # Shared layout: navbar, flashes, footer
    ├── dashboard.html
    ├── expenses.html
    ├── add_expense.html
    ├── edit_expense.html
    ├── budgets.html
    ├── add_budget.html
    ├── edit_budget.html
    ├── summary.html
    └── 404.html
```

---

## 5. Features checklist (mapped to the brief)

| Brief requirement | Where it's implemented |
|---|---|
| Record daily expenses | `add_expense` route + form |
| Organise into categories | Fixed `EXPENSE_CATEGORIES` list in `models.py`, shown as colour-coded pills |
| Define monthly budgets | `Budget` model — per month + category (or "Overall") |
| Generate spending summaries | `/summary` page + `/api/summary` endpoint + dashboard |
| Functions | Helper functions (`compute_month_summary`, `_require_*` validators) |
| Collections | Lists/dicts throughout (`defaultdict` for category totals) |
| File handling | `JSONRepository` reads/writes JSON files |
| datetime operations | `datetime.strptime`/`strftime` for date & month validation and filtering |
| Exception handling | `ValueError` for validation, custom `RecordNotFoundError` for missing records |
| Search and filtering | `/expenses?q=...&category=...&month=...&payment_method=...` |
| Category-wise / monthly totals | `compute_month_summary()` |
| Validation (amount/date/category) | `models.py` validators |
| README documentation | This file |

---

## 6. Run locally

### Prerequisites
- Python 3.9+
- pip

### Steps

```bash
# 1. Extract the zip and move into the folder
cd expense_budget_tracker

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py

# 5. Open your browser at:
http://127.0.0.1:5000
```

The app comes pre-loaded with sample September 2026 data so the dashboard
and charts aren't empty on first run — feel free to delete the contents of
`data/expenses.json` / `data/budgets.json` (reset to `[]`) if you want to
start fresh.

---

## 7. Upload to GitHub

```bash
cd expense_budget_tracker
git init
git add .
git commit -m "Personal Expense & Budget Tracker - Flask app"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Because of the included **`.gitattributes`** file, GitHub's language
detector (Linguist) is told to treat the `templates/`, `static/`, and
`data/` folders as "vendored" (and `.md` files as documentation), so they
are excluded from the language statistics. The result: your repository's
language bar on GitHub shows **Python** as the dominant/primary language,
even though the project also contains HTML, CSS, JS and JSON files.

---

## 8. Deploy for free

### Option A — Render.com
1. Push the project to GitHub (see above).
2. Create a free account at render.com → **New Web Service** → connect
   your repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Deploy — Render gives you a public URL.

### Option B — PythonAnywhere
1. Upload the project (or clone from GitHub) in a Bash console.
2. Create a virtualenv and `pip install -r requirements.txt`.
3. Add a new **Web App** → Flask → point the WSGI file to import `app`
   from `app.py`.
4. Reload the web app.

### Option C — Railway.app
1. New Project → Deploy from GitHub repo.
2. Railway auto-detects Python; set the start command to
   `gunicorn app:app`.
3. Deploy — Railway gives you a public URL.

---

## 9. Interview Questions & Answers

**Q1. Why did you choose Flask over Django for this project?**
Flask is a micro-framework — it gives you routing and templating without
imposing a large project structure, an ORM, or admin panel you don't need
for a small CRUD app. For a project of this size (handful of routes, no
complex auth/permissions), Flask keeps the codebase small and easy to
read end-to-end, which also makes it easier to explain in an interview.

**Q2. Why JSON files instead of a database like SQLite or PostgreSQL?**
The brief specifically asks for CSV/JSON-based storage to practice file
handling, not database/SQL skills. JSON also preserves Python-native
types (floats, nested structures) without the string-only limitation of
CSV, so amounts and IDs don't need extra type-casting when read back.

**Q3. What are the trade-offs of using JSON files instead of a real
database?**
JSON files are simple and portable but don't scale well: every write
rewrites the entire file, there's no built-in indexing, and concurrent
writes from multiple processes (not just threads) could still conflict.
For a personal, single-user tool this is an acceptable trade-off; for a
multi-user production system, I'd migrate the same `Expense`/`Budget`
model classes to use SQLAlchemy with a real database, since the
repository pattern makes this swap localized to one file.

**Q4. What is the Repository design pattern, and why did you use it
here?**
The Repository pattern separates "what the data means" (the `Expense`
and `Budget` model classes) from "how the data is stored and retrieved"
(the `JSONRepository` class). This means the rest of the app talks to
`expense_repo.add(...)` without knowing or caring that it's backed by a
JSON file — if I later swapped JSON for SQLite, only `repository.py`
would need to change.

**Q5. How do you ensure data isn't corrupted if two requests write at the
same time?**
`JSONRepository` wraps every write operation in a `threading.Lock()`, so
only one write happens at a time within the same process. Writes are also
done atomically by writing to a temporary file and then using `os.replace()`
to swap it into place, so a crash mid-write can't leave a half-written,
corrupted JSON file.

**Q6. How are expense categories and payment methods validated?**
Both are restricted to fixed lists (`EXPENSE_CATEGORIES`,
`PAYMENT_METHODS` in `models.py`). The `_require_choice()` helper checks
that a submitted value is one of the allowed options and raises a
`ValueError` with a clear message if not — this prevents typos or
unexpected categories from polluting the summary calculations.

**Q7. How is the date/month validated, and why use `datetime`?**
`_require_date()` and `_require_month()` call
`datetime.strptime(value, "%Y-%m-%d")` / `"%Y-%m"` inside a `try/except`.
If the string doesn't match the expected format, `strptime` raises a
`ValueError`, which is caught and re-raised with a friendlier message.
Using `datetime` instead of manual string checks correctly rejects
invalid dates like `2026-02-30`.

**Q8. How do you compute the "percentage of budget used"?**
`compute_month_summary()` sums all expenses for the selected month (by
filtering on `date[:7] == month`), groups them by category using a
`collections.defaultdict(float)`, then divides each category's spend by
its budget limit (if one exists) to get a percentage. The dashboard then
animates an SVG ring/bar to that percentage using `stroke-dashoffset` /
CSS `width` transitions.

**Q9. What happens if there's no budget set for a category?**
The category still appears in reports with its spend total, but its
"limit" is `None` and no progress bar/ring is shown for it — the UI shows
"No budget" instead of guessing or defaulting to a value, so the user
isn't misled.

**Q10. How does search/filtering work on the Expenses page?**
It's implemented with plain Python — `request.args` reads the
querystring (`q`, `category`, `month`, `payment_method`), and the record
list is filtered with simple list comprehensions (e.g. case-insensitive
substring match on the description, equality checks on category/month/
method). No database query language is needed since the whole dataset is
already in memory as a Python list.

**Q11. How is duplicate-budget entry prevented?**
Before adding a new budget, the app searches existing budgets for one
with the same `(month, category)` pair and raises a `ValueError` if found,
asking the user to edit the existing budget instead — this keeps exactly
one budget per category per month.

**Q12. What custom exception did you define, and why?**
`RecordNotFoundError` (in `repository.py`) is raised when `update()` or
`delete()` is called with an ID that doesn't exist. This is more
descriptive than a generic `KeyError`/`IndexError` and lets routes handle
"record not found" distinctly from "validation failed" with a clear,
readable `except` block.

**Q13. Why does the edit route pass `record_id` and `created_at`
explicitly when rebuilding the model object?**
Because a fresh `Expense(...)` or `Budget(...)` without those arguments
would default `id` to `None` and `created_at` to "now" — overwriting the
original record's identity and creation time when saved back to the
repository. Explicitly passing the existing `id` and `created_at`
preserves the record's original identity across edits.

**Q14. How would you add user accounts/authentication to this project?**
I'd add a `User` model and a `users.json` (or a real database once
multi-user support is needed), use Flask-Login for session management,
and scope each repository's data by a `user_id` field so each user only
sees their own expenses/budgets. The repository pattern already used here
would just need an extra filter argument.

**Q15. How would this scale if thousands of users used it?**
At that point JSON files stop being appropriate — I'd replace
`JSONRepository` with a SQLAlchemy-backed repository (same public
methods: `add`, `get`, `update`, `delete`, `search`), add proper indexing
on `date`/`category`/`user_id`, and move aggregation (totals, category
breakdowns) into SQL queries instead of Python loops, so the database does
the heavy lifting.

**Q16. Why is validation logic placed inside the model classes instead of
the Flask routes?**
Keeping `validate()` on the model means the same rules apply no matter
where the model is created — whether from a web form, a future API
client, or a test script — rather than duplicating checks in every route
that touches `Expense` or `Budget`.

**Q17. How did you test the application before packaging it?**
Using Flask's built-in `app.test_client()`, I exercised every route: page
loads, adding/editing/deleting expenses and budgets, rejecting invalid
input (negative amounts, bad dates, invalid categories), rejecting
duplicate budgets, search/filter query parameters, and the 404 handler —
all without needing a browser or a running server.

**Q18. What does the `.gitattributes` file do and why is it needed?**
GitHub's language statistics (Linguist) count lines of code per file
type. Since this project has many HTML/CSS/JS/JSON files alongside
Python, GitHub might otherwise show "HTML" or "CSS" as the dominant
language. The `.gitattributes` file marks `templates/`, `static/`, and
`data/` as `linguist-vendored` (excluded from stats) so the repository
accurately reflects that the application logic is written in Python.

---

## 10. Tech stack summary

| Category | Technology |
|---|---|
| Backend framework | Flask (Python) |
| Data storage | JSON files |
| Templating | Jinja2 |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Chart.js |
| Icons/Fonts | Font Awesome, Google Fonts |
| Testing | Flask test client |
| Deployment target | Render / PythonAnywhere / Railway (via gunicorn) |

---

Built as part of a Python internship project series. 🧡
