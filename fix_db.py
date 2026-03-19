import sqlite3
import os

# Find the database
db_path = 'instance/volunteering.db'

if not os.path.exists(db_path):
    print("ERROR: Could not find the database at", db_path)
    print("Make sure you are running this from your project folder.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check what columns already exist
    cursor.execute("PRAGMA table_info(event)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    print("Current event columns:", existing_columns)

    # Add missing columns safely
    if 'end_time' not in existing_columns:
        cursor.execute("ALTER TABLE event ADD COLUMN end_time DATETIME")
        print("✓ Added: end_time")
    else:
        print("- Skipped: end_time (already exists)")

    if 'created_at' not in existing_columns:
        cursor.execute("ALTER TABLE event ADD COLUMN created_at DATETIME")
        print("✓ Added: created_at")
    else:
        print("- Skipped: created_at (already exists)")

    conn.commit()
    conn.close()
    print("\nDone! You can now run python app.py")