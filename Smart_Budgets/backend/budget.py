from backend.database import get_connection

# Category groups for UX
ESSENTIALS = [
    "Groceries",
    "Rent/Mortgage",
    "Utilities (Electric/Water)",
    "Transportation (Fuel+Maint+Insur+Instal.)",
    "Education/Tuition",
]
LIFESTYLE = [
    "Entertainment & Subscriptions",
    "Dining Out",
    "Shopping/Leisure",
]
SAVINGS_CAT = "Savings/Investments"

def replace_income(user_id, incomes_dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM income WHERE user_id=?", (user_id,))
    for name, amt in incomes_dict.items():
        cur.execute("INSERT INTO income (user_id, stream_name, amount) VALUES (?,?,?)",
                    (user_id, name, float(amt)))
    conn.commit()
    conn.close()

def replace_expenses(user_id, expenses_dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE user_id=?", (user_id,))
    for cat, amt in expenses_dict.items():
        cur.execute("INSERT INTO expenses (user_id, category, amount) VALUES (?,?,?)",
                    (user_id, cat, float(amt)))
    conn.commit()
    conn.close()

def upsert_profile(user_id, dependents=0, savings_percent=0.0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM profile WHERE user_id=?", (user_id,))
    exists = cur.fetchone()
    if exists:
        cur.execute("UPDATE profile SET dependents=?, savings_percent=? WHERE user_id=?",
                    (int(dependents), float(savings_percent), user_id))
    else:
        cur.execute("INSERT INTO profile (user_id, dependents, savings_percent) VALUES (?,?,?)",
                    (user_id, int(dependents), float(savings_percent)))
    conn.commit()
    conn.close()

def get_profile(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT dependents, savings_percent FROM profile WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"dependents": 0, "savings_percent": 0.0}
    return {"dependents": row[0], "savings_percent": row[1]}

def get_income(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT stream_name, amount FROM income WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {name: amt for (name, amt) in rows}

def get_expenses(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT category, amount FROM expenses WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {cat: amt for (cat, amt) in rows}

def user_has_setup(user_id):
    return bool(get_income(user_id)) or bool(get_expenses(user_id))

def calculate_totals(user_id):
    income = get_income(user_id)
    expenses = get_expenses(user_id)
    total_income = sum(income.values())
    total_expense = sum(expenses.values())
    balance = total_income - total_expense
    return total_income, total_expense, balance

def split_expenses(expenses: dict):
    essentials = {k: v for k, v in expenses.items() if k in ESSENTIALS}
    lifestyle  = {k: v for k, v in expenses.items() if k in LIFESTYLE}
    savings    = {k: v for k, v in expenses.items() if k == SAVINGS_CAT}
    other      = {k: v for k, v in expenses.items() if k not in ESSENTIALS + LIFESTYLE + [SAVINGS_CAT]}
    return essentials, lifestyle, savings, other

def recommendations(user_id):
    tips = []
    profile = get_profile(user_id)
    dependents = profile.get("dependents", 0)
    target_savings_pct = profile.get("savings_percent", 0.0)

    income = get_income(user_id)
    expenses = get_expenses(user_id)
    total_income = sum(income.values()) or 1  # avoid zero division

    rent = expenses.get("Rent/Mortgage", 0)
    groceries = expenses.get("Groceries", 0)
    transport = expenses.get("Transportation (Fuel+Maint+Insur+Instal.)", 0)
    entertainment = expenses.get("Entertainment & Subscriptions", 0)
    savings_amt = expenses.get(SAVINGS_CAT, 0)

    rent_ratio = rent / total_income
    groceries_ratio = groceries / total_income
    transport_ratio = transport / total_income
    ent_ratio = entertainment / total_income
    savings_ratio = savings_amt / total_income

    if rent_ratio > 0.30:
        tips.append("Housing exceeds 30% of income. Consider downsizing or negotiating.")
    if groceries_ratio > 0.15 + 0.03*dependents:
        tips.append("Groceries look high; try weekly planning and bulk buys.")
    if transport_ratio > 0.15:
        tips.append("Transport is high; consider carpooling or optimizing trips.")
    if ent_ratio > 0.10:
        tips.append("Entertainment over 10%; audit your subscriptions.")
    if savings_ratio < max(0.10, target_savings_pct/100.0):
        tips.append(f"Try saving at least {max(10,int(target_savings_pct))}% of income monthly.")

    balance = sum(income.values()) - sum(expenses.values())
    if balance < 0:
        tips.append("You're overspending. Reduce non-essentials first.")
    elif balance > 0:
        tips.append(f"You can still allocate R{balance:.2f} to savings or debt repayment.")

    if not tips:
        tips.append("Your budget looks balanced. Keep tracking monthly to stay on target.")
    return tips
