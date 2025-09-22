import tkinter as tk
from tkinter import messagebox
from backend import budget
from gui.welcome_window import WelcomeWindow

class SetupWizard:
    """
    Guided wizard with sliders and buttons:
      1) Number of income streams + sliders for amounts
      2) Essentials with sliders
      3) Lifestyle with sliders
      4) Dependents + Savings%
      5) Review & Save
    """
    def __init__(self, master, username, user_id):
        self.master = master
        self.username = username
        self.user_id = user_id
        master.title(f"Hello {username} — Setup Your Budget")
        master.geometry("640x520")

        self.step = 0

        # Data holders
        self.income_count_var = tk.IntVar(value=1)
        self.income_names = []
        self.income_scales = []
        self.ess_scales = {}
        self.life_scales = {}
        self.dependents_var = tk.IntVar(value=0)
        self.savings_pct_var = tk.IntVar(value=10)  # default 10%

        self.container = tk.Frame(master)
        self.container.pack(fill="both", expand=True, padx=16, pady=16)

        self.nav = tk.Frame(master)
        self.nav.pack(fill="x", pady=6)
        self.back_btn = tk.Button(self.nav, text="◀ Back", width=10, command=self.prev_step, state="disabled")
        self.next_btn = tk.Button(self.nav, text="Next ▶", width=10, command=self.next_step)
        self.back_btn.pack(side="left")
        self.next_btn.pack(side="right")

        self.show_step()

    # ---------- Step Handling ----------
    def show_step(self):
        for f in self.container.winfo_children():
            f.destroy()

        builders = [
            self._build_income_count,
            self._build_income_amounts,
            self._build_essentials,
            self._build_lifestyle,
            self._build_dependents_savings,
            self._build_review,
        ]

        frame = builders[self.step]()
        frame.pack(fill="both", expand=True)
        self.back_btn.config(state="normal" if self.step > 0 else "disabled")
        self.next_btn.config(text="Save ▶" if self.step == 5 else "Next ▶")

    def next_step(self):
        if not self.validate_step():
            return
        if self.step < 5:
            self.step += 1
            self.show_step()
        else:
            self.save_all()

    def prev_step(self):
        if self.step > 0:
            self.step -= 1
            self.show_step()

    # ---------- Individual Step UIs ----------
    def _build_title(self, parent, text):
        tk.Label(parent, text=text, font=("Arial", 14, "bold")).pack(pady=8)

    def _build_income_count(self):
        f = tk.Frame(self.container)
        self._build_title(f, "Step 1: How many income sources do you have?")
        row = tk.Frame(f)
        row.pack(pady=10)

        tk.Label(row, text="Number of sources:").pack(side="left", padx=6)
        spin = tk.Spinbox(row, from_=1, to=10, width=5, textvariable=self.income_count_var, state="readonly")
        spin.pack(side="left")

        tk.Label(f, text="Tip: We'll create sliders for each source next. You can rename them.").pack(pady=6)
        return f

    def _build_income_amounts(self):
        f = tk.Frame(self.container)
        self._build_title(f, "Step 2: Set income amounts (per month)")

        # Clear prior references
        self.income_names = []
        self.income_scales = []

        cnt = self.income_count_var.get()
        grid = tk.Frame(f)
        grid.pack(pady=6, fill="x")

        for i in range(cnt):
            row = tk.Frame(grid)
            row.pack(fill="x", pady=6)

            name_var = tk.StringVar(value=f"Income {i+1}")
            self.income_names.append(name_var)
            tk.Entry(row, width=24, textvariable=name_var).pack(side="left", padx=6)

            val_var = tk.IntVar(value=0)
            scale = tk.Scale(row, from_=0, to=100000, orient="horizontal", length=360,
                             tickinterval=25000, resolution=500, variable=val_var)
            scale.pack(side="left", padx=6)
            self.income_scales.append(val_var)

        tk.Label(f, text="Use the sliders to set monthly amounts.").pack(pady=4)
        return f

    def _build_essentials(self):
        f = tk.Frame(self.container)
        self._build_title(f, "Step 3: Essentials (Survival)")

        self.ess_scales = {}
        for cat in budget.ESSENTIALS:
            row = tk.Frame(f)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=cat, width=32, anchor="w").pack(side="left", padx=6)
            var = tk.IntVar(value=0)
            tk.Scale(row, from_=0, to=100000, orient="horizontal", length=360,
                     tickinterval=25000, resolution=500, variable=var).pack(side="left", padx=6)
            self.ess_scales[cat] = var

        tk.Label(f, text="Tip: Start with realistic essentials before non-essentials.").pack(pady=6)
        return f

    def _build_lifestyle(self):
        f = tk.Frame(self.container)
        self._build_title(f, "Step 4: Lifestyle (Non-essential)")
        self.life_scales = {}
        for cat in budget.LIFESTYLE:
            row = tk.Frame(f)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=cat, width=32, anchor="w").pack(side="left", padx=6)
            var = tk.IntVar(value=0)
            tk.Scale(row, from_=0, to=50000, orient="horizontal", length=360,
                     tickinterval=10000, resolution=250, variable=var).pack(side="left", padx=6)
            self.life_scales[cat] = var

        tk.Label(f, text="These are optional. Keep them lean if funds are tight.").pack(pady=6)
        return f

    def _build_dependents_savings(self):
        f = tk.Frame(self.container)
        self._build_title(f, "Step 5: Dependents & Savings")

        # Dependents
        dep_row = tk.Frame(f); dep_row.pack(fill="x", pady=6)
        tk.Label(dep_row, text="How many people depend on your income?", width=36, anchor="w").pack(side="left", padx=6)
        dep_scale = tk.Scale(dep_row, from_=0, to=10, orient="horizontal", length=240,
                             tickinterval=2, resolution=1, variable=self.dependents_var)
        dep_scale.pack(side="left", padx=6)

        # Savings %
        sav_row = tk.Frame(f); sav_row.pack(fill="x", pady=6)
        tk.Label(sav_row, text="Savings / Investment (% of total income):", width=36, anchor="w").pack(side="left", padx=6)
        sav_scale = tk.Scale(sav_row, from_=0, to=50, orient="horizontal", length=240,
                             tickinterval=10, resolution=1, variable=self.savings_pct_var)
        sav_scale.pack(side="left", padx=6)

        tk.Label(f, text="We will automatically allocate savings from your total income.").pack(pady=6)
        return f

    def _build_review(self):
        f = tk.Frame(self.container)
        self._build_title(f, "Review & Save")
        text = tk.Text(f, height=16, width=72)
        text.pack(pady=6)

        incomes = self._collect_incomes()
        essentials = self._collect_essentials()
        lifestyle = self._collect_lifestyle()
        dep = self.dependents_var.get()
        sav_pct = self.savings_pct_var.get()

        total_income = sum(incomes.values())
        savings_amt = round(total_income * (sav_pct / 100.0), 2)

        def line(s=""): text.insert("end", s + "\n")
        line("INCOME")
        for k, v in incomes.items(): line(f"  - {k}: R{v:,.2f}")
        line(f"  Total Income: R{total_income:,.2f}")
        line("")
        line("EXPENSES (Essentials)")
        for k, v in essentials.items(): line(f"  - {k}: R{v:,.2f}")
        line("")
        line("EXPENSES (Lifestyle)")
        for k, v in lifestyle.items(): line(f"  - {k}: R{v:,.2f}")
        line("")
        line(f"SAVINGS/INVESTMENTS: {sav_pct}% → R{savings_amt:,.2f}")
        line(f"Dependents: {dep}")
        line("")

        est_total_expenses = sum(essentials.values()) + sum(lifestyle.values()) + savings_amt
        balance = total_income - est_total_expenses
        line(f"Estimated Total Expenses: R{est_total_expenses:,.2f}")
        line(f"Estimated Remaining Balance: R{balance:,.2f}")
        text.config(state="disabled")

        tk.Label(f, text="Click 'Save ▶' to store your budget and view your dashboard.").pack(pady=4)
        return f

    # ---------- Collect & Validate ----------
    def _collect_incomes(self):
        incomes = {}
        for name_var, val_var in zip(self.income_names, self.income_scales):
            name = (name_var.get() or "").strip() or "Income"
            incomes[name] = float(val_var.get())
        return incomes

    def _collect_essentials(self):
        return {k: float(v.get()) for k, v in self.ess_scales.items()}

    def _collect_lifestyle(self):
        return {k: float(v.get()) for k, v in self.life_scales.items()}

    def validate_step(self):
        if self.step == 1:
            if all(v.get() == 0 for v in self.income_scales):
                messagebox.showerror("Income Required", "Please set at least one income above R0.")
                return False
        return True

    # ---------- Save ----------
    def save_all(self):
        incomes = self._collect_incomes()
        essentials = self._collect_essentials()
        lifestyle = self._collect_lifestyle()
        dep = self.dependents_var.get()
        sav_pct = self.savings_pct_var.get()

        total_income = sum(incomes.values())
        savings_amt = round(total_income * (sav_pct / 100.0), 2)

        expenses = {}
        expenses.update(essentials)
        expenses.update(lifestyle)
        if savings_amt > 0:
            expenses[budget.SAVINGS_CAT] = savings_amt

        try:
            budget.replace_income(self.user_id, incomes)
            budget.replace_expenses(self.user_id, expenses)
            budget.upsert_profile(self.user_id, dep, sav_pct)
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save your setup.\n{e}")
            return

        messagebox.showinfo("Saved", "Your budget has been saved.")
        self.master.destroy()
        root = tk.Tk()
        WelcomeWindow(root, self.username, self.user_id)
        root.mainloop()
