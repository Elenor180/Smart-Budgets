import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from backend import budget
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
import csv

class WelcomeWindow(tk.Frame):
    def __init__(self, master, username, user_id):
        super().__init__(master)
        self.master = master
        self.username = username
        self.user_id = user_id

        master.title(f"Welcome {username} — Dashboard")
        master.geometry("1000x700")
        master.minsize(900, 600)

        # Welcome Label
        tk.Label(master, text=f"Welcome back, {username}!", font=("Arial", 16, "bold"))\
            .pack(pady=10, anchor="w", padx=12)

        # Filters
        self.show_essentials = tk.BooleanVar(value=True)
        self.show_lifestyle = tk.BooleanVar(value=True)
        self.show_savings = tk.BooleanVar(value=True)

        filter_frame = tk.Frame(master)
        filter_frame.pack(anchor="w", padx=12, pady=4)
        tk.Label(filter_frame, text="Filter: ").pack(side="left")
        tk.Checkbutton(filter_frame, text="Essentials", variable=self.show_essentials, command=self.refresh).pack(side="left", padx=6)
        tk.Checkbutton(filter_frame, text="Lifestyle", variable=self.show_lifestyle, command=self.refresh).pack(side="left", padx=6)
        tk.Checkbutton(filter_frame, text="Savings", variable=self.show_savings, command=self.refresh).pack(side="left", padx=6)

        # Summary cards frame
        self.card_frame = tk.Frame(master)
        self.card_frame.pack(fill="x", padx=12, pady=6)

        # Notebook for Table and Visualization
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=6)

        # Table tab
        self.table_tab = tk.Frame(self.notebook)
        self.notebook.add(self.table_tab, text="Budget Table")

        # Visualization tab with scrollbar
        self.visual_tab_parent = tk.Frame(self.notebook)
        self.notebook.add(self.visual_tab_parent, text="Analytical Visualization")

        self.visual_canvas = tk.Canvas(self.visual_tab_parent)
        self.visual_scrollbar = tk.Scrollbar(self.visual_tab_parent, orient="vertical", command=self.visual_canvas.yview)
        self.visual_scrollbar.pack(side="right", fill="y")
        self.visual_canvas.pack(side="left", fill="both", expand=True)
        self.visual_canvas.configure(yscrollcommand=self.visual_scrollbar.set)
        
        self.visual_tab = tk.Frame(self.visual_canvas)
        self.visual_canvas.create_window((0, 0), window=self.visual_tab, anchor="nw")
        
        self.visual_tab.bind("<Configure>", lambda e: self.visual_canvas.configure(scrollregion=self.visual_canvas.bbox("all")))

        # Actions
        btns = tk.Frame(master)
        btns.pack(anchor="w", pady=6, padx=12)
        tk.Button(btns, text="Adjust Budget", width=16, command=self.open_wizard).pack(side="left", padx=6)
        tk.Button(btns, text="Export CSV", width=14, command=self.export_csv).pack(side="left", padx=6)
        tk.Button(btns, text="Export PDF", width=14, command=self.export_pdf).pack(side="left", padx=6)
        tk.Button(btns, text="Close", width=12, command=self.master.destroy).pack(side="left", padx=6)

        # Data containers
        self.table_box = None
        self.pie_canvas = None
        self.bar_canvas = None
        self.rec_box = None

        self.refresh()

    def refresh(self):
        # Clear summary cards
        for w in self.card_frame.winfo_children():
            w.destroy()

        incomes = budget.get_income(self.user_id)
        expenses = budget.get_expenses(self.user_id)

        # Apply filters
        exp_ess, exp_life, exp_save, exp_other = budget.split_expenses(expenses)
        filtered_expenses = {}
        if self.show_essentials.get():
            filtered_expenses.update(exp_ess)
        if self.show_lifestyle.get():
            filtered_expenses.update(exp_life)
        if self.show_savings.get():
            filtered_expenses.update(exp_save)
        filtered_expenses.update(exp_other)

        total_income = sum(incomes.values())
        total_expense = sum(filtered_expenses.values())
        balance = total_income - total_expense

        # Summary cards
        def card(parent, title, value):
            box = tk.Frame(parent, bd=1, relief="solid", padx=12, pady=8)
            tk.Label(box, text=title, font=("Arial", 11, "bold")).pack()
            tk.Label(box, text=value, font=("Arial", 12)).pack()
            return box

        c1 = card(self.card_frame, "Total Income", f"R{total_income:,.2f}")
        c2 = card(self.card_frame, "Total Expenses (filtered)", f"R{total_expense:,.2f}")
        c3 = card(self.card_frame, "Remaining Balance", f"R{balance:,.2f}")
        c1.grid(row=0, column=0, padx=8, pady=6, sticky="ew")
        c2.grid(row=0, column=1, padx=8, pady=6, sticky="ew")
        c3.grid(row=0, column=2, padx=8, pady=6, sticky="ew")

        # Table in table_tab
        if self.table_box:
            self.table_box.destroy()
        self.table_box = tk.LabelFrame(self.table_tab, text="Your Budget (Filtered)", padx=8, pady=8)
        self.table_box.pack(fill="both", expand=True, padx=12, pady=8)

        hdr = tk.Frame(self.table_box); hdr.pack(fill="x")
        tk.Label(hdr, text="Category", width=40, anchor="w", font=("Arial", 10, "bold")).pack(side="left")
        tk.Label(hdr, text="Amount", width=16, anchor="e", font=("Arial", 10, "bold")).pack(side="right")

        def row(parent, k, v):
            r = tk.Frame(parent); r.pack(fill="x")
            tk.Label(r, text=k, width=40, anchor="w").pack(side="left")
            tk.Label(r, text=f"R{v:,.2f}", width=16, anchor="e").pack(side="right")

        row(self.table_box, "— Income —", 0)
        for k, v in incomes.items():
            row(self.table_box, f"  {k}", v)
        row(self.table_box, "", 0)
        row(self.table_box, "— Expenses (Filtered) —", 0)
        for k, v in filtered_expenses.items():
            row(self.table_box, f"  {k}", v)

        # Clear visualization tab
        for w in self.visual_tab.winfo_children():
            w.destroy()

        # Pie chart (stacked)
        if filtered_expenses:
            pie_frame = tk.Frame(self.visual_tab)
            pie_frame.pack(fill="both", expand=True, padx=20, pady=6) 
            
            fig = Figure(figsize=(9, 6))
            ax = fig.add_subplot(111)
            labels = list(filtered_expenses.keys())
            amounts = list(filtered_expenses.values())
            
            # Adjusted labeldistance to place labels further out, reducing overlap
            ax.pie(amounts, labels=labels, autopct="%1.1f%%", startangle=90, 
                    labeldistance=1.1, pctdistance=0.85)
            
            ax.axis('equal')
            ax.set_title("Expense Distribution")
            
            self.pie_canvas = FigureCanvasTkAgg(fig, master=pie_frame)
            self.pie_canvas.draw()
            self.pie_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Bar chart (stacked)
        bar_frame = tk.Frame(self.visual_tab)
        bar_frame.pack(fill="both", expand=True, padx=20, pady=4)
        total_savings = expenses.get(budget.SAVINGS_CAT, 0.0)
        
        fig2 = Figure(figsize=(9, 6))
        ax2 = fig2.add_subplot(111)
        ax2.bar(["Income", "Expenses", "Savings"], [total_income, total_expense, total_savings], color=['green', 'red', 'blue'])
        ax2.set_title("Income vs Expenses vs Savings")
        ax2.set_ylabel("Amount")
        self.bar_canvas = FigureCanvasTkAgg(fig2, master=bar_frame)
        self.bar_canvas.draw()
        self.bar_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Recommendations below table
        if self.rec_box:
            self.rec_box.destroy()
        self.rec_box = tk.LabelFrame(self.table_tab, text="Recommendations", padx=8, pady=8)
        self.rec_box.pack(fill="x", padx=12, pady=8)
        recs = budget.recommendations(self.user_id)
        if recs:
            for r in recs:
                tk.Label(self.rec_box, text="• " + r, anchor="w", justify="left").pack(fill="x")
        else:
            tk.Label(self.rec_box, text="No recommendations at this time.").pack()

    def export_csv(self):
        incomes = budget.get_income(self.user_id)
        expenses = budget.get_expenses(self.user_id)
        exp_ess, exp_life, exp_save, exp_other = budget.split_expenses(expenses)
        
        filtered_expenses = {}
        if self.show_essentials.get():
            filtered_expenses.update(exp_ess)
        if self.show_lifestyle.get():
            filtered_expenses.update(exp_life)
        if self.show_savings.get():
            filtered_expenses.update(exp_save)
        filtered_expenses.update(exp_other)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Budget as CSV"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Category", "Amount"])
                writer.writerow(["— Income —", ""])
                for k, v in incomes.items():
                    writer.writerow([k, v])
                writer.writerow(["", ""])
                writer.writerow(["— Expenses (Filtered) —", ""])
                for k, v in filtered_expenses.items():
                    writer.writerow([k, v])
            messagebox.showinfo("Exported", f"Budget successfully exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export CSV.\n{e}")

    def export_pdf(self):
        incomes = budget.get_income(self.user_id)
        expenses = budget.get_expenses(self.user_id)
        exp_ess, exp_life, exp_save, exp_other = budget.split_expenses(expenses)
        
        filtered_expenses = {}
        if self.show_essentials.get():
            filtered_expenses.update(exp_ess)
        if self.show_lifestyle.get():
            filtered_expenses.update(exp_life)
        if self.show_savings.get():
            filtered_expenses.update(exp_save)
        filtered_expenses.update(exp_other)

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Budget as PDF"
        )
        if not file_path:
            return

        try:
            with PdfPages(file_path) as pdf:
                # Page 1: Table & Recommendations
                fig1 = Figure(figsize=(8, 10))
                ax1 = fig1.add_subplot(111)
                ax1.axis("off")
                text = "BUDGET REPORT\n\n— Income —\n"
                for k, v in incomes.items():
                    text += f"{k}: R{v:,.2f}\n"
                text += "\n— Expenses (Filtered) —\n"
                for k, v in filtered_expenses.items():
                    text += f"{k}: R{v:,.2f}\n"
                text += "\nRecommendations:\n"
                recs = budget.recommendations(self.user_id)
                if recs:
                    for r in recs:
                        text += f"• {r}\n"
                else:
                    text += "No recommendations at this time.\n"
                ax1.text(0, 1, text, fontsize=12, va="top", ha="left")
                pdf.savefig(fig1)

                # Page 2: Pie chart
                if filtered_expenses:
                    # Updated figsize for PDF chart
                    fig2 = Figure(figsize=(9, 6))
                    ax2 = fig2.add_subplot(111)
                    labels = list(filtered_expenses.keys())
                    amounts = list(filtered_expenses.values())
                    ax2.pie(amounts, labels=labels, autopct="%1.1f%%", startangle=90,
                            labeldistance=1.1, pctdistance=0.85)
                    ax2.set_title("Expense Distribution")
                    pdf.savefig(fig2)

                # Page 3: Bar chart
                # Updated figsize for PDF chart
                fig3 = Figure(figsize=(9, 6))
                ax3 = fig3.add_subplot(111)
                total_income = sum(incomes.values())
                total_expense = sum(filtered_expenses.values())
                total_savings = expenses.get(budget.SAVINGS_CAT, 0.0)
                ax3.bar(["Income", "Expenses", "Savings"], [total_income, total_expense, total_savings], color=['green', 'red', 'blue'])
                ax3.set_title("Income vs Expenses vs Savings")
                ax3.set_ylabel("Amount")
                pdf.savefig(fig3)

            messagebox.showinfo("Exported", f"Budget successfully exported to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export PDF.\n{e}")

    def open_wizard(self):
        from gui.setup_wizard import SetupWizard
        for w in self.master.winfo_children():
            w.destroy()
        SetupWizard(self.master, self.username, self.user_id)