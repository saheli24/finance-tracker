from db import connect
import csv


def add_transaction():
    #opens connection to finance.db
    conn = connect()
    #creates a pointer to database
    cursor = conn.cursor()

    # List users first
    list_users()
    user_id = input("Enter your user ID from the list above: ")

    print("\n--- Add a New Transaction ---")
    amount = input("Enter amount: ")
    category = input("Enter category: ")
    date = input("Enter date (YYYY-MM-DD): ")
    description = input("Enter description: ")

    # Convert amount to float and user_id to int
    try:
        user_id = int(user_id)
        amount = float(amount)
    except ValueError:
        print("Invalid number input. Transaction cancelled.")
        conn.close()
        return

    #The ? are placeholders → Python fills them safely from the tuple (1, 20.5, "Food", ...)
    cursor.execute("""
    INSERT INTO transactions (user_id, amount, category, date, description)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, amount, category, date, description))

    #make changes permanent and close the connection --> free memory
    conn.commit()
    conn.close()

    print("Transaction added!")

def view_transactions():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")    #puts all the results into a python list
    rows = cursor.fetchall()

    if not rows:
        print("\nNo transactions found.\n")
    else:
        print("\n--- All Transactions ---")
        # Print headers
        print(f"{'ID':<3} {'User':<5} {'Amount':<10} {'Category':<10} {'Date':<12} {'Description'}")
        print("-" * 60)

        # Print each row nicely formatted
        for row in rows:
            transaction_id, user_id, amount, category, date, description = row
            print(f"{transaction_id:<3} {user_id:<5} {amount:<10.2f} {category:<10} {date:<12} {description}")

        print()
    conn.close()


def total_spending_per_user():
    conn = connect()
    cursor = conn.cursor()

    # SQL query: sum all amounts per user
    #SUM(amount) → adds up all transactions per user
    # GROUP BY user_id → calculates per user
    cursor.execute("""
    SELECT user_id, SUM(amount) as total
    FROM transactions
    GROUP BY user_id
    """)
    rows = cursor.fetchall()

    if not rows:
        print("\nNo transactions found.\n")
    else:
        print("\n--- Total Spending per User ---")
        print(f"{'User':<5} {'Total Spending'}")
        print("-" * 25)
        for row in rows:
            user_id, total = row
            #<5 = fixed width column
            # :.2f = 2 decimal points
            print(f"{user_id:<5} {total:.2f}")
        print()

    conn.close()

def spending_by_category():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT category, SUM(amount) as total
    FROM transactions
    GROUP BY category
    """)
    rows = cursor.fetchall()

    if not rows:
        print("\nNo transactions found.\n")
    else:
        print("\n--- Spending by Category ---")
        print(f"{'Category':<15} {'Total Spending'}")
        print("-" * 30)
        for row in rows:
            category, total = row
            print(f"{category:<15} {total:.2f}")
        print()

    conn.close()

def monthly_spending_summary():
    conn = connect()
    cursor = conn.cursor()

    #SUBSTR(date, 1, 7) → takes first 7 characters of date → YYYY-MM
    #GROUP BY month → totals per month
    #ORDER BY month → shows months in order
    cursor.execute("""
    SELECT SUBSTR(date, 1, 7) as month, SUM(amount) as total
    FROM transactions
    GROUP BY month
    ORDER BY month
    """)
    rows = cursor.fetchall()

    if not rows:
        print("\nNo transactions found.\n")
    else:
        print("\n--- Monthly Spending ---")
        print(f"{'Month':<10} {'Total Spending'}")
        print("-" * 25)
        for row in rows:
            month, total = row
            print(f"{month:<10} {total:.2f}")
        print()

    conn.close()

def register_user():
    conn = connect()
    cursor = conn.cursor()

    print("\n--- Register New User ---")
    name = input("Enter name: ")
    email = input("Enter email: ")

    #INSERT INTO users (name, email) → adds new row
    # users table is used here
    cursor.execute("""
    INSERT INTO users (name, email)
    VALUES (?, ?)
    """, (name, email))

    conn.commit()
    conn.close()
    print(f"User {name} added successfully!\n")

def list_users():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, name FROM users")
    rows = cursor.fetchall()

    if not rows:
        print("No users found.\n")
    else:
        print("\n--- Users ---")
        print(f"{'ID':<5} {'Name'}")
        print("-" * 15)
        for user_id, name in rows:
            print(f"{user_id:<5} {name}")
        print()

    conn.close()

def view_transactions_with_users():
    conn = connect()
    cursor = conn.cursor()

    #t is an alias for transactions table
    #u is an alias for the users table
    # JOIN = INNER JOIN transactions with users to get name
    # JOIN = only keeps rows where the condition matches
    cursor.execute("""
    SELECT t.transaction_id, u.name, t.amount, t.category, t.date, t.description
    FROM transactions t
    JOIN users u ON t.user_id = u.user_id
    ORDER BY t.date
    """)

    rows = cursor.fetchall()

    if not rows:
        print("\nNo transactions found.\n")
    else:
        print("\n--- Transactions with User Names ---")
        print(f"{'ID':<3} {'User':<10} {'Amount':<10} {'Category':<10} {'Date':<12} {'Description'}")
        print("-" * 60)
        for transaction_id, name, amount, category, date, description in rows:
            print(f"{transaction_id:<3} {name:<10} {amount:<10.2f} {category:<10} {date:<12} {description}")
        print()

    conn.close()


def export_transactions_csv(filename="transactions_export.csv"):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT t.transaction_id, u.name, t.amount, t.category, t.date, t.description
    FROM transactions t
    JOIN users u ON t.user_id = u.user_id
    ORDER BY t.date
    """)
    rows = cursor.fetchall()

    if not rows:
        print("No transactions to export.\n")
    else:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "User", "Amount", "Category", "Date", "Description"])
            writer.writerows(rows)
        print(f"Transactions exported to {filename}\n")

    conn.close()


def import_transactions_csv(filename="transactions_import.csv"):
    conn = connect()
    cursor = conn.cursor()

    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Find user_id by name
                cursor.execute("SELECT user_id FROM users WHERE name = ?", (row['User'],))
                result = cursor.fetchone()
                if result:
                    user_id = result[0]
                else:
                    # If user doesn’t exist, create user
                    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (row['User'], 'unknown@example.com'))
                    conn.commit()
                    user_id = cursor.lastrowid

                cursor.execute("""
                INSERT INTO transactions (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """, (user_id, float(row['Amount']), row['Category'], row['Date'], row['Description']))

        conn.commit()
        print(f"Transactions imported from {filename}\n")

    except FileNotFoundError:
        print(f"File {filename} not found.\n")

    conn.close()

def search_by_category():
    category = input("Enter category to search: ")
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT t.transaction_id, u.name, t.amount, t.category, t.date, t.description
    FROM transactions t
    JOIN users u ON t.user_id = u.user_id
    WHERE t.category = ?
    ORDER BY t.date
    """, (category,))
    rows = cursor.fetchall()

    if not rows:
        print(f"No transactions found in category '{category}'.\n")
    else:
        print(f"\n--- Transactions in Category: {category} ---")
        print(f"{'ID':<3} {'User':<10} {'Amount':<10} {'Category':<10} {'Date':<12} {'Description'}")
        print("-"*60)
        for transaction_id, name, amount, category, date, description in rows:
            print(f"{transaction_id:<3} {name:<10} {amount:<10.2f} {category:<10} {date:<12} {description}")
        print()

    conn.close()

def search_by_date():
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT t.transaction_id, u.name, t.amount, t.category, t.date, t.description
    FROM transactions t
    JOIN users u ON t.user_id = u.user_id
    WHERE t.date BETWEEN ? AND ?
    ORDER BY t.date
    """, (start_date, end_date))
    rows = cursor.fetchall()

    if not rows:
        print(f"No transactions found between {start_date} and {end_date}.\n")
    else:
        print(f"\n--- Transactions from {start_date} to {end_date} ---")
        print(f"{'ID':<3} {'User':<10} {'Amount':<10} {'Category':<10} {'Date':<12} {'Description'}")
        print("-"*60)
        for transaction_id, name, amount, category, date, description in rows:
            print(f"{transaction_id:<3} {name:<10} {amount:<10.2f} {category:<10} {date:<12} {description}")
        print()

    conn.close()

def search_by_user():
    list_users()
    user_id = input("Enter user ID to filter: ")

    try:
        user_id = int(user_id)
    except ValueError:
        print("Invalid user ID.\n")
        return

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT t.transaction_id, u.name, t.amount, t.category, t.date, t.description
    FROM transactions t
    JOIN users u ON t.user_id = u.user_id
    WHERE t.user_id = ?
    ORDER BY t.date
    """, (user_id,))
    rows = cursor.fetchall()

    if not rows:
        print("No transactions found for this user.\n")
    else:
        print(f"\n--- Transactions for User ID: {user_id} ---")
        print(f"{'ID':<3} {'User':<10} {'Amount':<10} {'Category':<10} {'Date':<12} {'Description'}")
        print("-"*60)
        for transaction_id, name, amount, category, date, description in rows:
            print(f"{transaction_id:<3} {name:<10} {amount:<10.2f} {category:<10} {date:<12} {description}")
        print()

    conn.close()





def menu():
    print("\n--- Finance Tracker ---")
    print("1. Register new user")
    print("2. Add transaction")
    print("3. View transactions")
    print("4. Total spending per user")
    print("5. Spending by category")
    print("6. Monthly spending summary")
    print("7. Export transactions to CSV")
    print("8. Import transactions from CSV")
    print("9. Search by category")
    print("10. Search by date range")
    print("11. Search by user")
    print("12. Exit")

def run():
    while True:
        menu()
        choice = input("Enter your choice (number): ")

        if choice == "1":
            register_user()
        elif choice == "2":
            add_transaction()
        elif choice == "3":
            view_transactions_with_users()
        elif choice == "4":
            total_spending_per_user()
        elif choice == "5":
            spending_by_category()
        elif choice == "6":
            monthly_spending_summary()
        elif choice == "7":
            export_transactions_csv()
        elif choice == "8":
            import_transactions_csv()
        elif choice == "9":
            search_by_category()
        elif choice == "10":
            search_by_date()
        elif choice == "11":
            search_by_user()
        elif choice == "12":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    run()