import sqlite3

DB_NAME = "study_planner.db"

NEW_COLUMNS = {
    "phone": "VARCHAR",
    "dob": "VARCHAR",
    "gender": "VARCHAR",
    "address": "VARCHAR",
    "profile_picture_url": "VARCHAR",
    "category": "VARCHAR",
    "school_name": "VARCHAR",
    "school_board": "VARCHAR",
    "class_level": "VARCHAR",
    "college": "VARCHAR",
    "department": "VARCHAR",
    "course": "VARCHAR",
    "semester": "VARCHAR",
    "institution_name": "VARCHAR",
    "program_name": "VARCHAR",
    "study_year": "VARCHAR",
    "research_program": "VARCHAR",
    "research_area": "VARCHAR",
    "supervisor_name": "VARCHAR",
    "current_study_level": "VARCHAR",
    "academic_year": "VARCHAR",
    "roll_number": "VARCHAR",
}

connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

cursor.execute("PRAGMA table_info(student)")
existing_columns = {
    row[1] for row in cursor.fetchall()
}

if not existing_columns:
    raise RuntimeError(
        "Student table not found. Check your database location."
    )

for column, data_type in NEW_COLUMNS.items():
    if column not in existing_columns:
        cursor.execute(
            f"ALTER TABLE student ADD COLUMN {column} {data_type}"
        )
        print(f"Added: {column}")

# Add user_id to student table
cursor.execute("PRAGMA table_info(student)")
existing_columns = {
    row[1] for row in cursor.fetchall()
}

if "user_id" not in existing_columns:
    cursor.execute("""
        ALTER TABLE student
        ADD COLUMN user_id INTEGER REFERENCES user(id)
    """)
    print("Added user_id column.")

# Ensure one profile per account
cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS
    ix_student_user_id_unique
    ON student(user_id)
""")

print("User account relationship migration completed.")

connection.commit()
connection.close()

print("Profile database migration completed successfully!")