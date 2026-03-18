import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from db import connect
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Finance Tracker")
        self.root.geometry("1100x650")

        # Sidebar
        sidebar = ttk.Frame(root, width=200, bootstyle="dark")
        sidebar.pack(side=LEFT, fill=Y)

        ttk.Label(sidebar, text="Finance App", font=("Segoe UI", 16, "bold")).pack(pady=20)

        ttk.Button(sidebar, text="Add", command=self.show_add, bootstyle="primary").pack(fill=X, pady=5, padx=10)
        ttk.Button(sidebar, text="View", command=self.show_view, bootstyle="primary").pack(fill=X, pady=5, padx=10)
        ttk.Button(sidebar, text="Analytics", command=self.show_analytics, bootstyle="primary").pack(fill=X, pady=5, padx=10)

        # Main area
        self.container = ttk.Frame(root)
        self.container.pack(side=RIGHT, fill=BOTH, expand=True)

        self.frames = {}
        for F in (AddPage, ViewPage, AnalyticsPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_add()

    def show_add(self):
        self.frames[AddPage].tkraise()

    def show_view(self):
        self.frames[ViewPage].refresh()
        self.frames[ViewPage].tkraise()

    def show_analytics(self):
        self.frames[AnalyticsPage].refresh()
        self.frames[AnalyticsPage].tkraise()

class AddPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Add Transaction", font=("Segoe UI", 18, "bold")).pack(pady=20)

        form = ttk.Frame(self, padding=20)
        form.pack()

        self.user_combo = ttk.Combobox(form)
        self.amount = ttk.Entry(form)
        self.category = ttk.Entry(form)
        self.date = ttk.Entry(form)
        self.desc = ttk.Entry(form)

        labels = ["User", "Amount", "Category", "Date", "Description"]
        widgets = [self.user_combo, self.amount, self.category, self.date, self.desc]

        for i, (l, w) in enumerate(zip(labels, widgets)):
            ttk.Label(form, text=l).grid(row=i, column=0, pady=8)
            w.grid(row=i, column=1, pady=8, padx=10)

        ttk.Button(self, text="Submit", bootstyle="success", command=self.add).pack(pady=10)

        self.load_users()

    def load_users(self):
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name FROM users")
        users = cursor.fetchall()
        conn.close()

        self.user_combo['values'] = [f"{u[0]} - {u[1]}" for u in users]

    def add(self):
        try:
            user_id = int(self.user_combo.get().split(" - ")[0])
            amount = float(self.amount.get())

            conn = connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO transactions (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                           (user_id, amount, self.category.get(), self.date.get(), self.desc.get()))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Transaction added!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

class ViewPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Transactions", font=("Segoe UI", 18, "bold")).pack(pady=10)

        self.search = ttk.Entry(self)
        self.search.pack(pady=5)

        ttk.Button(self, text="Search", command=self.refresh).pack()

        columns = ("ID", "User", "Amount", "Category", "Date", "Description")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(fill=BOTH, expand=True)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = connect()
        cursor = conn.cursor()

        query = """
        SELECT t.transaction_id, u.name, t.amount, t.category, t.date, t.description
        FROM transactions t
        JOIN users u ON t.user_id = u.user_id
        """

        term = self.search.get()
        if term:
            query += " WHERE t.category LIKE ?"
            cursor.execute(query, (f"%{term}%",))
        else:
            cursor.execute(query)

        for row in cursor.fetchall():
            self.tree.insert("", END, values=row)

        conn.close()

class AnalyticsPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Analytics", font=("Segoe UI", 18, "bold")).pack(pady=10)

        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=BOTH, expand=True)

    def refresh(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
        data = cursor.fetchall()
        conn.close()

        categories = [d[0] for d in data]
        amounts = [d[1] for d in data]

        fig = plt.Figure()
        ax = fig.add_subplot(111)
        ax.bar(categories, amounts)
        ax.set_title("Spending by Category")

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

if __name__ == "__main__":
    app = ttk.Window(themename="darkly")
    FinanceApp(app)
    app.mainloop()