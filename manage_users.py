"""
User & Access Management CLI
Project: Smart Gate-Entry Attendance System with Confidence-Aware Multi-Face Recognition
Ramdeobaba University - IDEA Lab (2026-27)
"""

import sys
import argparse
from database.database import init_db, execute_insert, fetch_one, fetch_all, log_audit
from recognition.crypto_utils import hash_password

def create_user(username, password, role="ADMIN", full_name="", email=""):
    init_db()
    role = role.upper()
    if role not in ("ADMIN", "FACULTY", "STUDENT"):
        print(f"[ERROR] Invalid role: {role}. Must be ADMIN, FACULTY, or STUDENT.")
        return False

    existing = fetch_one("SELECT id FROM users WHERE username = ?", (username,))
    if existing:
        print(f"[ERROR] User '{username}' already exists.")
        return False

    pwd_hash = hash_password(password)
    uid = execute_insert("""
        INSERT INTO users (username, password_hash, role, full_name, email)
        VALUES (?, ?, ?, ?, ?)
    """, (username, pwd_hash, role, full_name, email))

    log_audit("CREATE_USER", f"Created {role} user '{username}'", actor="CLI")
    print(f"[SUCCESS] User '{username}' created successfully with role '{role}' (ID: {uid}).")
    return True

def list_users():
    init_db()
    users = fetch_all("SELECT id, username, role, full_name, email, created_at FROM users")
    print("\n--- Registered Users ---")
    if not users:
        print("No users found.")
        return
    for u in users:
        print(f"ID: {u['id']} | Username: {u['username']} | Role: {u['role']} | Name: {u['full_name']} | Email: {u['email']}")
    print("------------------------\n")

def seed_default_admin():
    init_db()
    admin = fetch_one("SELECT id FROM users WHERE role = 'ADMIN'")
    if not admin:
        create_user("admin", "Admin@123", role="ADMIN", full_name="System Administrator", email="admin@rknec.edu")
        create_user("faculty", "Faculty@123", role="FACULTY", full_name="Faculty Coordinator", email="faculty@rknec.edu")
        print("[INFO] Default admin and faculty accounts initialized.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Users & RBAC for Smart Attendance System")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create_admin", help="Create an admin user")
    create_parser.add_argument("--username", "-u", default="admin", help="Username")
    create_parser.add_argument("--password", "-p", required=True, help="Password")
    create_parser.add_argument("--name", "-n", default="System Administrator", help="Full name")
    create_parser.add_argument("--email", "-e", default="admin@rknec.edu", help="Email")

    create_user_parser = subparsers.add_parser("create_user", help="Create a user with specified role")
    create_user_parser.add_argument("--username", "-u", required=True)
    create_user_parser.add_argument("--password", "-p", required=True)
    create_user_parser.add_argument("--role", "-r", default="FACULTY", choices=["ADMIN", "FACULTY", "STUDENT"])
    create_user_parser.add_argument("--name", "-n", default="")
    create_user_parser.add_argument("--email", "-e", default="")

    subparsers.add_parser("list", help="List all users")
    subparsers.add_parser("seed", help="Seed default admin & faculty users")

    args = parser.parse_args()
    if args.command == "create_admin":
        create_user(args.username, args.password, role="ADMIN", full_name=args.name, email=args.email)
    elif args.command == "create_user":
        create_user(args.username, args.password, role=args.role, full_name=args.name, email=args.email)
    elif args.command == "list":
        list_users()
    elif args.command == "seed":
        seed_default_admin()
    else:
        parser.print_help()
