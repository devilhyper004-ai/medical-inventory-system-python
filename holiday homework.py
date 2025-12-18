# medical_inventory.py
import mysql.connector
from datetime import datetime

# Connect to MySQL (updated with your password)
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",           # change if different
        password="12345678",   # <-- your provided password
        database="medical_store"
    )
    cursor = db.cursor()
except mysql.connector.Error as err:
    print("❌ Error connecting to the database:", err)
    exit(1)

def add_medicine():
    name = input("Enter medicine name: ").strip()
    company = input("Enter company name: ").strip()
    try:
        price = float(input("Enter price: ").strip())
        qty = int(input("Enter quantity: ").strip())
    except ValueError:
        print("❌ Invalid number entered.")
        return
    expiry = input("Enter expiry date (YYYY-MM-DD): ").strip()

    query = """
    INSERT INTO medicines (med_name, med_company, med_price, med_quantity, expiry_date)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (name, company, price, qty, expiry)
    cursor.execute(query, values)
    db.commit()
    print("✅ Medicine added successfully!\n")

def view_medicines():
    cursor.execute("SELECT * FROM medicines")
    records = cursor.fetchall()
    if not records:
        print("\nNo medicines found.\n")
        return
    print("\n--- Medicine Inventory ---")
    print("{:<5} {:<25} {:<18} {:<10} {:<8} {:<12}".format("ID", "Name", "Company", "Price", "Qty", "Expiry"))
    for row in records:
        med_id, name, comp, price, qty, expiry = row
        expiry_str = expiry.strftime("%Y-%m-%d") if expiry else ""
        print("{:<5} {:<25} {:<18} {:<10.2f} {:<8} {:<12}".format(med_id, name, comp or "", price or 0.0, qty or 0, expiry_str))
    print()

def search_medicine():
    name = input("Enter medicine name to search: ").strip()
    query = "SELECT * FROM medicines WHERE med_name LIKE %s"
    cursor.execute(query, (f"%{name}%",))
    records = cursor.fetchall()
    if records:
        print("\nSearch Results:")
        for row in records:
            med_id, name, comp, price, qty, expiry = row
            expiry_str = expiry.strftime("%Y-%m-%d") if expiry else ""
            print(f"ID: {med_id} | Name: {name} | Company: {comp} | Price: {price:.2f} | Qty: {qty} | Expiry: {expiry_str}")
    else:
        print("❌ No medicine found with that name.")
    print()

def update_medicine():
    med_id = input("Enter medicine ID to update: ").strip()
    if not med_id.isdigit():
        print("❌ Invalid ID.")
        return
    print("1. Update Name\n2. Update Price\n3. Update Quantity\n4. Update Expiry Date")
    choice = input("Choose an option: ").strip()

    if choice == '1':
        new_name = input("Enter new name: ").strip()
        cursor.execute("UPDATE medicines SET med_name=%s WHERE med_id=%s", (new_name, med_id))
    elif choice == '2':
        try:
            new_price = float(input("Enter new price: ").strip())
        except ValueError:
            print("❌ Invalid price.")
            return
        cursor.execute("UPDATE medicines SET med_price=%s WHERE med_id=%s", (new_price, med_id))
    elif choice == '3':
        try:
            new_qty = int(input("Enter new quantity: ").strip())
        except ValueError:
            print("❌ Invalid quantity.")
            return
        cursor.execute("UPDATE medicines SET med_quantity=%s WHERE med_id=%s", (new_qty, med_id))
    elif choice == '4':
        new_expiry = input("Enter new expiry date (YYYY-MM-DD): ").strip()
        cursor.execute("UPDATE medicines SET expiry_date=%s WHERE med_id=%s", (new_expiry, med_id))
    else:
        print("❌ Invalid choice.")
        return

    db.commit()
    print("✅ Medicine updated successfully!\n")

def delete_medicine():
    med_id = input("Enter medicine ID to delete: ").strip()
    if not med_id.isdigit():
        print("❌ Invalid ID.")
        return
    confirm = input(f"Are you sure you want to delete medicine ID {med_id}? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    cursor.execute("DELETE FROM medicines WHERE med_id=%s", (med_id,))
    db.commit()
    print("🗑️ Medicine deleted successfully!\n")

def low_stock_alert():
    try:
        threshold = int(input("Enter stock threshold: ").strip())
    except ValueError:
        print("❌ Invalid threshold.")
        return
    query = "SELECT med_name, med_quantity FROM medicines WHERE med_quantity <= %s"
    cursor.execute(query, (threshold,))
    records = cursor.fetchall()

    if records:
        print("\n⚠️ Low Stock Medicines:")
        for row in records:
            print(f"{row[0]} - Qty: {row[1]}")
    else:
        print("✅ All medicines are sufficiently stocked.")
    print()

def expiry_alert(days=30):
    """
    Show medicines expiring within `days` days.
    Default: 30 days
    """
    try:
        cursor.execute("SELECT med_id, med_name, expiry_date FROM medicines WHERE expiry_date IS NOT NULL")
        records = cursor.fetchall()
    except mysql.connector.Error as err:
        print("Error fetching expiry data:", err)
        return

    near = []
    today = datetime.today().date()
    for med_id, name, expiry in records:
        if expiry:
            delta = (expiry - today).days
            if delta <= days:
                near.append((med_id, name, expiry, delta))

    if near:
        print(f"\n⚠️ Medicines expiring within {days} days:")
        for med_id, name, expiry, delta in near:
            print(f"ID {med_id} | {name} | Expiry: {expiry} | In {delta} days")
    else:
        print(f"✅ No medicines expiring within {days} days.")
    print()

def main():
    while True:
        print("==== Medical Shop Inventory System ====")
        print("1. Add Medicine")
        print("2. View All Medicines")
        print("3. Search Medicine")
        print("4. Update Medicine")
        print("5. Delete Medicine")
        print("6. Low Stock Alert")
        print("7. Expiry Alert (next 30 days)")
        print("8. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            add_medicine()
        elif choice == '2':
            view_medicines()
        elif choice == '3':
            search_medicine()
        elif choice == '4':
            update_medicine()
        elif choice == '5':
            delete_medicine()
        elif choice == '6':
            low_stock_alert()
        elif choice == '7':
            expiry_alert(30)
        elif choice == '8':
            print("Exiting... Goodbye! 👋")
            break
        else:
            print("❌ Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()
