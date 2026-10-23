"""
Database Seeding Script
Project: Smart Gate-Entry Attendance System with Confidence-Aware Multi-Face Recognition
Ramdeobaba University - IDEA Lab (2026-27)
"""

import sys
from database.database import init_db, get_db_connection, execute_insert, fetch_one

def seed_students():
    """
    Seeds the classroom roster for Section A with 60 students.
    Notice: In strict compliance with privacy guidelines, biometric embeddings are NOT
    synthesized here. Student records are created with is_enrolled = 0.
    Biometric embeddings must be registered via the enrollment webcam interface.
    """
    print("[SEED] Initializing database schema...")
    init_db()

    students_data = [
        ("1", "Aarav Sharma", "Section A", "A1", "sharmaa@rknec.edu"),
        ("2", "Aditi Deshmukh", "Section A", "A1", "deshmukha@rknec.edu"),
        ("3", "Aditya Joshi", "Section A", "A1", "joshia@rknec.edu"),
        ("4", "Akash Verma", "Section A", "A1", "vermaa@rknec.edu"),
        ("5", "Ananya Kulkarni", "Section A", "A1", "kulkarnia@rknec.edu"),
        ("6", "Aniket Patil", "Section A", "A1", "patila@rknec.edu"),
        ("7", "Anushka Mehta", "Section A", "A1", "mehtaa@rknec.edu"),
        ("8", "Atharva Wagh", "Section A", "A1", "wagha@rknec.edu"),
        ("9", "Ayush Agrawal", "Section A", "A1", "agrawala@rknec.edu"),
        ("10", "Bhavik Jain", "Section A", "A1", "jainb@rknec.edu"),
        ("11", "Chetan Kale", "Section A", "A1", "kalec@rknec.edu"),
        ("12", "Devendra Singh", "Section A", "A1", "singhd@rknec.edu"),
        ("13", "Divya Shinde", "Section A", "A1", "shinded@rknec.edu"),
        ("14", "Gaurav Raut", "Section A", "A1", "rautg@rknec.edu"),
        ("15", "Harsh Tambe", "Section A", "A1", "tambeh@rknec.edu"),

        ("16", "Ishaan Roy", "Section A", "A2", "royi@rknec.edu"),
        ("17", "Isha Kapse", "Section A", "A2", "kapsei@rknec.edu"),
        ("18", "Jayesh Gokhale", "Section A", "A2", "gokhalej@rknec.edu"),
        ("19", "Karan Malhotra", "Section A", "A2", "malhotrak@rknec.edu"),
        ("20", "Khushi Tiwari", "Section A", "A2", "tiwarik@rknec.edu"),
        ("21", "Aryan Dixit", "Section A", "A2", "dixita@rknec.edu"), # Team Member
        ("22", "Kunal Bhave", "Section A", "A2", "bhavek@rknec.edu"),
        ("23", "Madhura Gadre", "Section A", "A2", "gadrem@rknec.edu"),
        ("24", "Manish Chopde", "Section A", "A2", "chopdem@rknec.edu"),
        ("25", "Mayur Bondre", "Section A", "A2", "bondrem@rknec.edu"),
        ("26", "Neha Mohod", "Section A", "A2", "mohodn@rknec.edu"),
        ("27", "Nikhil Dhande", "Section A", "A2", "dhanden@rknec.edu"),
        ("28", "Nishant Bobde", "Section A", "A2", "bobden@rknec.edu"),
        ("29", "Omkar Date", "Section A", "A2", "dateo@rknec.edu"),
        ("30", "Pooja Bapat", "Section A", "A2", "bapatp@rknec.edu"),

        ("31", "Pranav Shelke", "Section A", "A3", "shelkep@rknec.edu"),
        ("32", "Prasad Pande", "Section A", "A3", "pandep@rknec.edu"),
        ("33", "Pratiksha Mule", "Section A", "A3", "mulep@rknec.edu"),
        ("34", "Priyanka Soni", "Section A", "A3", "sonip@rknec.edu"),
        ("35", "Rahul Sen", "Section A", "A3", "senr@rknec.edu"),
        ("36", "Riya Agashe", "Section A", "A3", "agasher@rknec.edu"),
        ("37", "Rohan Sawant", "Section A", "A3", "sawantr@rknec.edu"),
        ("38", "Rohit Bhise", "Section A", "A3", "bhiser@rknec.edu"),
        ("39", "Rucha Dani", "Section A", "A3", "danir@rknec.edu"),
        ("40", "Sahil Dongre", "Section A", "A3", "dongres@rknec.edu"),
        ("41", "Samiksha Ghate", "Section A", "A3", "ghates@rknec.edu"),
        ("42", "Sanket Warghane", "Section A", "A3", "warghanes@rknec.edu"),
        ("43", "Sarang Moghe", "Section A", "A3", "moghes@rknec.edu"),
        ("44", "Sayali Dhote", "Section A", "A3", "dhotes@rknec.edu"),
        ("45", "Sharvari Bodke", "Section A", "A3", "bodkes@rknec.edu"),

        ("46", "Shivam Kakde", "Section A", "A4", "kakdes@rknec.edu"),
        ("47", "Shreya Gade", "Section A", "A4", "gades@rknec.edu"),
        ("48", "Shubham Nimje", "Section A", "A4", "nimjes@rknec.edu"),
        ("49", "Siddhant Lad", "Section A", "A4", "lads@rknec.edu"),
        ("50", "Snehal Pimpale", "Section A", "A4", "pimpales@rknec.edu"),
        ("51", "Pushkar Kolhe", "Section A", "A4", "kolhep@rknec.edu"), # Team Member
        ("52", "Suraj Gawande", "Section A", "A4", "gawandes@rknec.edu"),
        ("53", "Jaheed Pathan", "Section A", "A4", "pathanjaheed@rknec.edu"), # Team Member
        ("54", "Tanmay Phalke", "Section A", "A4", "phalket@rknec.edu"),
        ("55", "Arpit Kadwe", "Section A", "A4", "kadwea@rknec.edu"), # Team Member
        ("56", "Tejas Thakre", "Section A", "A4", "thakret@rknec.edu"),
        ("57", "Utkarsh Khare", "Section A", "A4", "khareu@rknec.edu"),
        ("58", "Vaibhav Zade", "Section A", "A4", "zadev@rknec.edu"),
        ("59", "Vedant Karale", "Section A", "A4", "karalev@rknec.edu"),
        ("60", "Swara Bhandwalkar", "Section A", "A4", "bhandwalkars@rknec.edu") # Team Member
    ]

    inserted_count = 0
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for roll, name, sec, batch, email in students_data:
            existing = fetch_one("SELECT id FROM students WHERE roll_number = ?", (roll,))
            if not existing:
                cursor.execute("""
                    INSERT INTO students (roll_number, name, section, batch, email, is_enrolled)
                    VALUES (?, ?, ?, ?, ?, 0)
                """, (roll, name, sec, batch, email))
                inserted_count += 1

    print(f"[SEED SUCCESS] Seeded {inserted_count} student records for Section A (Total Class: 60 students).")
    print("      Biometric face profiles can now be enrolled via the dashboard!")

    # Seed default RBAC users
    try:
        from manage_users import seed_default_admin
        seed_default_admin()
    except Exception as e:
        print(f"[WARN] User seeding skipped: {e}")

if __name__ == "__main__":
    seed_students()
