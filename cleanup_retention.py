"""
Data Retention & Privacy Cleanup Utility
Project: Smart Gate-Entry Attendance System with Confidence-Aware Multi-Face Recognition
Ramdeobaba University - IDEA Lab (2026-27)

Purges face crop images and resolved manual review records older than the retention threshold
(default 30 days) to comply with biometric privacy policies.
"""

import os
import time
import argparse
from datetime import datetime, timedelta
import config
from database.database import execute_query, fetch_all, log_audit

def cleanup_old_crops(retention_days: int = None, dry_run: bool = False):
    days = retention_days if retention_days is not None else config.RETENTION_DAYS
    cutoff_time = time.time() - (days * 86400)
    cutoff_date_str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    print(f"[RETENTION] Running cleanup for data older than {days} days (Cutoff: {cutoff_date_str})")

    purged_files = 0
    # Scan manual review crops directory
    if os.path.exists(config.MANUAL_REVIEWS_DIR):
        for fname in os.listdir(config.MANUAL_REVIEWS_DIR):
            fpath = os.path.join(config.MANUAL_REVIEWS_DIR, fname)
            if os.path.isfile(fpath):
                mtime = os.path.getmtime(fpath)
                if mtime < cutoff_time:
                    if not dry_run:
                        try:
                            os.remove(fpath)
                            purged_files += 1
                        except Exception as e:
                            print(f"[WARN] Failed to delete {fpath}: {e}")
                    else:
                        print(f"[DRY-RUN] Would delete {fpath}")
                        purged_files += 1

    # Purge old resolved reviews from database
    if not dry_run:
        deleted_reviews = execute_query(
            "DELETE FROM manual_reviews WHERE status IN ('CONFIRMED', 'REJECTED', 'REASSIGNED') AND created_at < ?",
            (cutoff_date_str,)
        )
        deleted_logs = execute_query(
            "DELETE FROM juno_sync_logs WHERE synced_at < ?",
            (cutoff_date_str,)
        )
        log_audit(
            action="DATA_RETENTION_CLEANUP",
            details=f"Purged {purged_files} crop files, {deleted_reviews} resolved review records, and {deleted_logs} sync logs past {days}-day retention",
            actor="CRON_MAINTENANCE"
        )
        print(f"[SUCCESS] Retention cleanup complete: {purged_files} files, {deleted_reviews} reviews, {deleted_logs} logs purged.")
    else:
        print(f"[DRY-RUN] Retention check: {purged_files} files eligible for deletion.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up biometric data older than retention limit")
    parser.add_argument("--days", "-d", type=int, default=config.RETENTION_DAYS, help="Retention period in days")
    parser.add_argument("--dry-run", action="store_true", help="Inspect without deleting")
    args = parser.parse_args()
    cleanup_old_crops(retention_days=args.days, dry_run=args.dry_run)
