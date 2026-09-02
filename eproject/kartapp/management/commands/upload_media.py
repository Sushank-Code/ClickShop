import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings


class Command(BaseCommand):
    help = "Uploads all local media files to Cloudinary with the configured PREFIX folder."

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        
        if not media_root.exists():
            self.stdout.write(self.style.ERROR(f"Media folder not found at: {media_root}"))
            return

        self.stdout.write(self.style.NOTICE(f"Scanning media files from: {media_root} ...\n"))

        uploaded = 0
        skipped = 0
        failed = 0

        for root, _, files in os.walk(media_root):
            for file in files:
                full_path = Path(root) / file
                # Relative path used by Django (e.g. 'products/ATX-Jeans.jpg')
                rel_path = full_path.relative_to(media_root).as_posix()

                # Check if already present on Cloudinary
                if default_storage.exists(rel_path):
                    self.stdout.write(self.style.WARNING(f"[SKIP] Already exists: {rel_path}"))
                    skipped += 1
                    continue

                self.stdout.write(f"[UPLOADING] {rel_path} ...")
                try:
                    with open(full_path, "rb") as f:
                        default_storage.save(rel_path, f)
                    uploaded += 1
                    self.stdout.write(self.style.SUCCESS(f"  [OK] Success: {rel_path}"))
                except Exception as exc:
                    failed += 1
                    self.stdout.write(self.style.ERROR(f"  [FAILED] Failed: {rel_path} ({exc})"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nFinished! Uploaded: {uploaded}, Skipped: {skipped}, Failed: {failed}"
            )
        )