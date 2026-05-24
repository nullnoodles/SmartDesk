"""Backup and restore — package the SQLite DB and exports into a single zip."""
from __future__ import annotations

import datetime
import shutil
import zipfile
from pathlib import Path

from app.config import APP_VERSION, DATA_DIR, DB_PATH, EXPORTS_DIR
from app.data.database import Database


BACKUP_MANIFEST_NAME = "smartdesk_manifest.txt"


class BackupService:
    """Create and restore application backups (.zip)."""

    def __init__(self, db: Database):
        self.db = db

    # ------------------------------------------------------------------
    # Create backup
    # ------------------------------------------------------------------
    def create_backup(self, output_zip: Path) -> Path:
        """Write a backup zip containing the database and exported PDFs."""
        output_zip = Path(output_zip)
        output_zip.parent.mkdir(parents=True, exist_ok=True)

        # Force any pending WAL writes to disk before zipping
        try:
            conn = self.db.connect()
            conn.commit()
            conn.execute("PRAGMA wal_checkpoint(FULL)")
        except Exception:
            pass

        timestamp = datetime.datetime.now().isoformat(timespec="seconds")
        manifest = (
            f"SmartDesk Backup\n"
            f"version: {APP_VERSION}\n"
            f"created_at: {timestamp}\n"
        )

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(BACKUP_MANIFEST_NAME, manifest)

            # Database file
            if Path(DB_PATH).exists():
                zf.write(DB_PATH, arcname=f"data/{Path(DB_PATH).name}")

            # Exported PDFs
            if EXPORTS_DIR.exists():
                for pdf in EXPORTS_DIR.glob("*.pdf"):
                    zf.write(pdf, arcname=f"exports/{pdf.name}")

        return output_zip

    # ------------------------------------------------------------------
    # Restore
    # ------------------------------------------------------------------
    def restore_backup(self, zip_path: Path) -> None:
        """Restore from a backup zip. Replaces the current DB and exports."""
        zip_path = Path(zip_path)
        if not zip_path.exists():
            raise FileNotFoundError(f"Backup file not found: {zip_path}")

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            if BACKUP_MANIFEST_NAME not in names:
                raise ValueError("Not a SmartDesk backup file")

            # Close active connection before replacing the file
            try:
                self.db.close()
            except Exception:
                pass

            DATA_DIR.mkdir(parents=True, exist_ok=True)
            EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

            # Stash current DB so we can roll back on failure
            backup_old = None
            if Path(DB_PATH).exists():
                backup_old = Path(str(DB_PATH) + ".bak-restore")
                shutil.copy2(DB_PATH, backup_old)

            try:
                for member in names:
                    if member == BACKUP_MANIFEST_NAME:
                        continue
                    if member.startswith("data/"):
                        target = DATA_DIR / Path(member).name
                        with zf.open(member) as src, open(target, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                    elif member.startswith("exports/"):
                        target = EXPORTS_DIR / Path(member).name
                        with zf.open(member) as src, open(target, "wb") as dst:
                            shutil.copyfileobj(src, dst)
            except Exception:
                # Roll back DB if restore failed mid-way
                if backup_old and backup_old.exists():
                    shutil.copy2(backup_old, DB_PATH)
                raise
            finally:
                if backup_old and backup_old.exists():
                    backup_old.unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # Suggested file name
    # ------------------------------------------------------------------
    @staticmethod
    def suggested_filename() -> str:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"smartdesk-backup-{stamp}.zip"
