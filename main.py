from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sqlite3
from urllib.parse import urlparse

DB_FILE = "budget.db"

HTML_UI = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FinTrack | Expense & Budget Manager</title>
    <style>
        :root {
            --bg: #f8fafc;
            --surface: #ffffff;
            --primary: #0f172a;
            --accent: #2563eb;
            --accent-hover: #1d4ed8;
            --text: #1e293b;
            --muted: #64748b;
            --border: #e2e8f0;
            --danger: #ef4444;
            --success: #10b981;
            --warning: #f59e0b;
        }
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 16px;
            line-height: 1.5;
        }
        .app {
            max-width: 640px;
            margin: 0 auto;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .brand {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
            letter-spacing: -0.02em;
        }
        .brand span { color: var(--accent); }
        .badge-status {
            font-size: 0.75rem;
            background: #dcfce7;
            color: #166534;
            padding: 4px 10px;
            border-radius: 999px;
            font-weight: 600;
        }
        .metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 16px;
        }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .card-label {
            font-size: 0.8rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-weight: 600;
        }
        .card-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--primary);
            margin-top: 4px;
        }
        .budget-card { margin-bottom: 20px; }
        .budget-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .edit-budget-btn {
            background: none;
            border: 1px solid var(--border);
            color: var(--text);
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 6px;
            cursor: pointer;
        }
        .progress-track {
            width: 100%;
            height: 10px;
            background: #e2e8f0;
            border-radius: 999px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            width: 0%;
            background: var(--success);
            transition: width 0.3s ease, background 0.3s ease;
        }
        .budget-meta {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--muted);
            margin-top: 6px;
        }
        .section-title {
            font-size: 0.95rem;
            font-weight: 600;
            margin: 0 0 12px 0;
            color: var(--primary);
        }
        form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .full-width { grid-column: span 2; }
        input, select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 0.95rem;
            background: var(--surface);
            color: var(--text);
        }
        input:focus, select:focus {
            outline: none;
            border-color: var(--accent);
        }
        .btn-primary {
            grid-column: span 2;
            background: var(--accent);
            color: #fff;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-primary:active { background: var(--accent-hover); }
        .filters {
            display: flex;
            gap: 6px;
            overflow-x: auto;
            padding-bottom: 8px;
            margin: 20px 0 12px 0;
        }
        .filter-btn {
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--muted);
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            white-space: nowrap;
        }
        .filter-btn.active {
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }
        .tx-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .tx-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-bottom: 8px;
        }
        .tx-info { display: flex; flex-direction: column; }
        .tx-title { font-weight: 600; font-size: 0.95rem; }
        .tx-sub {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 4px;
            font-size: 0.8rem;
            color: var(--muted);
        }
        .cat-pill {
            background: #eff6ff;
            color: var(--accent);
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.72rem;
        }
        .tx-right {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .tx-amount {
            font-weight: 700;
            color: var(--primary);
            font-size: 1rem;
        }
        .btn-del {
            background: #fee2e2;
            color: var(--danger);
            border: none;
            width: 28px;
            height: 28px;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
        }
        .empty-state {
            text-align: center;
            padding: 32px 16px;
            color: var(--muted);
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
<div class="app">
    <header>
        <div class="brand">Fin<span>Track</span></div>
        <div class="badge-status">API Connected</div>
    </header>

    <div class="metrics">
        <div class="card">
            <div class="card-label">Total Spent</div>
            <div class="card-value" id="total-spent">$0.00</div>
        </div>
        <div class="card">
            <div class="card-label">Transactions</div>
            <div class="card-value" id="tx-count">0</div>
        </div>
    </div>

    <div class="card budget-card">
        <div class="budget-header">
            <span class="card-label">Monthly Budget Limit</span>
            <button class="edit-budget-btn" onclick="updateBudget()">Set Budget</button>
        </div>
        <div class="progress-track">
            <div class="progress-fill" id="progress-fill"></div>
        </div>
        <div class="budget-meta">
            <span id="budget-used-pct">0% used</span>
            <span id="budget-remaining">$500.00 remaining</span>
        </div>
    </div>

    <div class="card">
        <h2 class="section-title">New Expense</h2>
        <form id="expense-form">
            <input class="full-width" type="text" id="title" placeholder="Description (e.g., Cloud Hosting, Groceries)" required>
            <input type="number" id="amount" step="0.01" min="0.01" placeholder="Amount ($)" required>
            <select id="category">
                <option value="Food">Food & Dining</option>
                <option value="Transport">Transport</option>
                <option value="Utilities">Utilities & Bills</option>
                <option value="Software">Software & Tools</option>
                <option value="General">General</option>
            </select>
            <input class="full-width" type="date" id="date" required>
            <button class="btn-primary" type="submit">+ Record Expense</button>
        </form>
    </div>

    <div class="filters" id="filter-bar">
        <button class="filter-btn active" onclick="setFilter('All', this)">All</button>
        <button class="filter-btn" onclick="setFilter('Food', this)">Food</button>
        <button class="filter-btn" onclick="setFilter('Transport', this)">Transport</button>
        <button class="filter-btn" onclick="setFilter('Utilities', this)">Utilities</button>
        <button class="filter-btn" onclick="setFilter('Software', this)">Software</button>
        <button class="filter-btn" onclick="setFilter('General', this)">General</button>
    </div>

    <ul class="tx-list" id="expense-list"></ul>
</div>

<script>
    let allExpenses = [];
    let currentFilter = 'All';
    let monthlyBudget = parseFloat(localStorage.getItem('monthlyBudget')) || 500.00;

    document.getElementById('date').valueAsDate = new Date();

    function updateBudget() {
        const val = prompt('Enter your monthly budget limit ($):', monthlyBudget);
        if (val !== null && !isNaN(parseFloat(val)) && parseFloat(val) > 0) {
            monthlyBudget = parseFloat(val);
            localStorage.setItem('monthlyBudget', monthlyBudget);
            renderUI();
        }
    }

    function setFilter(category, btn) {
        currentFilter = category;
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderUI();
    }

    async function loadExpenses() {
        const res = await fetch('/expenses');
        allExpenses = await res.json();
        renderUI();
    }

    function renderUI() {
        const list = document.getElementById('expense-list');
        const totalEl = document.getElementById('total-spent');
        const countEl = document.getElementById('tx-count');
        const fillEl = document.getElementById('progress-fill');
        const pctEl = document.getElementById('budget-used-pct');
        const remEl = document.getElementById('budget-remaining');

        const total = allExpenses.reduce((sum, item) => sum + parseFloat(item.amount || 0), 0);
        totalEl.textContent = '$' + total.toFixed(2);
        countEl.textContent = allExpenses.length;

        const pct = Math.min((total / monthlyBudget) * 100, 100);
        fillEl.style.width = pct + '%';
        fillEl.style.background = pct >= 90 ? 'var(--danger)' : pct >= 70 ? 'var(--warning)' : 'var(--success)';
        pctEl.textContent = Math.round((total / monthlyBudget) * 100) + '% of $' + monthlyBudget.toFixed(2);

        const remaining = monthlyBudget - total;
        remEl.textContent = remaining >= 0
            ? '$' + remaining.toFixed(2) + ' remaining'
            : '$' + Math.abs(remaining).toFixed(2) + ' over budget';

        const filtered = currentFilter === 'All'
            ? allExpenses
            : allExpenses.filter(e => e.category === currentFilter);

        list.innerHTML = '';
        if (filtered.length === 0) {
            list.innerHTML = '<div class="empty-state">No expenses recorded in this category.</div>';
            return;
        }

        filtered.slice().reverse().forEach(item => {
            const li = document.createElement('li');
            li.className = 'tx-item';
            li.innerHTML = `
                <div class="tx-info">
                    <span class="tx-title">${escapeHtml(item.title)}</span>
                    <div class="tx-sub">
                        <span class="cat-pill">${escapeHtml(item.category)}</span>
                        <span>${escapeHtml(item.date)}</span>
                    </div>
                </div>
                <div class="tx-right">
                    <span class="tx-amount">$${parseFloat(item.amount).toFixed(2)}</span>
                    <button class="btn-del" title="Delete" onclick="deleteExpense(${item.id})">&times;</button>
                </div>
            `;
            list.appendChild(li);
        });
    }

    function escapeHtml(str) {
        return String(str).replace(/[&<>"']/g, m => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[m]));
    }

    document.getElementById('expense-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            title: document.getElementById('title').value.trim(),
            amount: parseFloat(document.getElementById('amount').value),
            category: document.getElementById('category').value,
            date: document.getElementById('date').value
        };

        const res = await fetch('/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            document.getElementById('title').value = '';
            document.getElementById('amount').value = '';
            loadExpenses();
        }
    });

    async function deleteExpense(id) {
        const res = await fetch('/expenses/' + id, { method: 'DELETE' });
        if (res.ok) loadExpenses();
    }

    loadExpenses();
</script>
</body>
</html>
"""


def init_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
  conn.commit()
  conn.close()


init_db()


class BudgetAPIHandler(BaseHTTPRequestHandler):

  def send_json(self, status_code, payload):
    self.send_response(status_code)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(payload).encode("utf-8"))

  def do_GET(self):
    parsed_url = urlparse(self.path)

    if parsed_url.path == "/":
      self.send_response(200)
      self.send_header("Content-Type", "text/html; charset=utf-8")
      self.end_headers()
      self.wfile.write(HTML_UI.encode("utf-8"))

    elif parsed_url.path == "/expenses":
      conn = sqlite3.connect(DB_FILE)
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, title, amount, category, date FROM expenses ORDER BY id"
          " ASC"
      )
      rows = cursor.fetchall()
      conn.close()

      expenses = [
          {
              "id": r[0],
              "title": r[1],
              "amount": r[2],
              "category": r[3],
              "date": r[4],
          }
          for r in rows
      ]
      self.send_json(200, expenses)

    else:
      self.send_json(404, {"error": "Endpoint not found"})

  def do_POST(self):
    parsed_url = urlparse(self.path)
    if parsed_url.path == "/expenses":
      content_length = int(self.headers.get("Content-Length", 0))
      post_data = self.rfile.read(content_length)
      try:
        data = json.loads(post_data.decode("utf-8"))
        title = str(data.get("title", "")).strip()
        amount = float(data.get("amount", 0))
        category = str(data.get("category", "General")).strip()
        date = str(data.get("date", "")).strip()

        if not title or amount <= 0 or not date:
          self.send_json(400, {"error": "Invalid title, amount, or date"})
          return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (title, amount, category, date) VALUES"
            " (?, ?, ?, ?)",
            (title, amount, category, date),
        )
        conn.commit()
        expense_id = cursor.lastrowid
        conn.close()

        self.send_json(
            201,
            {
                "id": expense_id,
                "title": title,
                "amount": amount,
                "category": category,
                "date": date,
            },
        )
      except (ValueError, json.JSONDecodeError) as e:
        self.send_json(400, {"error": f"Bad request: {str(e)}"})
    else:
      self.send_json(404, {"error": "Endpoint not found"})

  def do_DELETE(self):
    parsed_url = urlparse(self.path)
    if parsed_url.path.startswith("/expenses/"):
      try:
        expense_id = int(parsed_url.path.split("/")[-1])
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted == 0:
          self.send_json(404, {"error": "Expense not found"})
        else:
          self.send_json(200, {"deleted_id": expense_id})
      except ValueError:
        self.send_json(400, {"error": "Invalid expense ID"})
    else:
      self.send_json(404, {"error": "Endpoint not found"})


def run():
  server_address = ("127.0.0.1", 8000)
  httpd = HTTPServer(server_address, BudgetAPIHandler)
  print("FinTrack REST API & UI running on http://127.0.0.1:8000...")
  httpd.serve_forever()


if __name__ == "__main__":
    run()
    