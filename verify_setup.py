"""
Environment Verification Script
Project: Smart Gate-Entry Attendance System with Confidence-Aware Multi-Face Recognition
Ramdeobaba University - IDEA Lab (2026-27)
"""

import sys
import platform

def print_header(title):
    print("=" * 65)
    print(f" {title}")
    print("=" * 65)

def main():
    print_header("RAMDEOBABA UNIVERSITY - IDEA LAB PROJECT SETUP VERIFICATION")
    print(f"Operating System : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version   : {sys.version.split()[0]} ({'64-bit' if sys.maxsize > 2**32 else '32-bit'})\n")

    required_packages = [
        ("cv2", "OpenCV (Computer Vision)", "cv2.__version__"),
        ("numpy", "NumPy (Numerical Vector Operations)", "numpy.__version__"),
        ("onnxruntime", "ONNX Runtime (Model Inference Engine)", "onnxruntime.__version__"),
        ("insightface", "InsightFace (RetinaFace & ArcFace)", "insightface.__version__"),
        ("flask", "Flask (Backend Web Framework)", "flask.__version__"),
        ("sqlite3", "SQLite3 (Transactional Database Engine)", "sqlite3.sqlite_version"),
        ("cryptography", "Cryptography (Fernet AES Encryption)", "cryptography.__version__"),
        ("bcrypt", "Bcrypt (Password Hashing for RBAC)", "bcrypt.__version__"),
        ("pypdf", "PyPDF (Timetable & PDF Ingestion)", "pypdf.__version__"),
        ("matplotlib", "Matplotlib (Evaluation & Scientific Plots)", "matplotlib.__version__"),
    ]

    all_passed = True
    print_header("CHECKING INSTALLED LIBRARIES")

    for module_name, display_name, version_attr in required_packages:
        try:
            mod = __import__(module_name)
            ver = eval(version_attr, {module_name: mod})
            print(f" [PASS] {display_name:<44} : Version {ver}")
        except ImportError as e:
            print(f" [FAIL] {display_name:<44} : NOT INSTALLED ({e})")
            all_passed = False
        except Exception as e:
            print(f" [PASS] {display_name:<44} : Installed")

    print_header("CHECKING DATABASE & TIMETABLE")
    try:
        from database.database import init_db, fetch_one
        init_db()
        student_count = fetch_one("SELECT COUNT(*) as c FROM students")["c"]
        print(f" [PASS] SQLite Attendance Database Initialized! Total Students: {student_count}")
    except Exception as e:
        print(f" [FAIL] Database verification failed: {e}")
        all_passed = False

    try:
        from attendance.timetable import TimetableManager
        tm = TimetableManager()
        print(f" [PASS] Ramdeobaba V Sem AIML Timetable Loaded! Scheduled Classes: {len(tm.schedule)}")
    except Exception as e:
        print(f" [FAIL] Timetable verification failed: {e}")
        all_passed = False

    print_header("SETUP VERIFICATION SUMMARY")
    if all_passed:
        print(" SUCCESS: All core libraries, database tables, and timetable schedules are verified!")
        print(" You can start the server with: python app.py")
    else:
        print(" ACTION NEEDED: Please resolve the failed checks above.")
    print("=" * 65)

if __name__ == "__main__":
    main()
