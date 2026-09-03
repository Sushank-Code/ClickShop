# store/management/commands/sync_cloudinary_images.py
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings

from kartapp.models import Category
from store.models import Product, ProductGallery
from accounts.models import UserProfile


# model label as it appears in data.json -> (Django model, image field name)
MODEL_MAP = {
    "kartapp.category": (Category, "cat_image"),
    "store.product": (Product, "image"),
    "store.productgallery": (ProductGallery, "image"),
    "accounts.userprofile": (UserProfile, "profile_picture"),
}


class Command(BaseCommand):
    help = "Recovers original local image paths from data.json and syncs them to Cloudinary with deterministic names."

    def add_arguments(self, parser):
        parser.add_argument("data_json_path", type=str)

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        data_path = Path(options["data_json_path"])

        with open(data_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        synced, failed, not_found = 0, 0, 0

        for record in records:
            model_label = record["model"]
            if model_label not in MODEL_MAP:
                continue

            model_cls, field_name = MODEL_MAP[model_label]
            pk = record["pk"]
            original_path = record["fields"].get(field_name)

            if not original_path:
                continue  # no image on this record originally

            local_path = media_root / original_path
            if not local_path.exists():
                self.stdout.write(self.style.WARNING(f"[NOT FOUND] {model_label} pk={pk}: {original_path}"))
                not_found += 1
                continue

            try:
                obj = model_cls.objects.get(pk=pk)
            except model_cls.DoesNotExist:
                continue

            folder = original_path.split("/")[0]  # e.g. "categories", "products"
            ext = local_path.suffix
            unique_name = f"{folder.rstrip('s')}_{pk}{ext}"

            try:
                with open(local_path, "rb") as f:
                    getattr(obj, field_name).save(unique_name, File(f), save=True)
                self.stdout.write(self.style.SUCCESS(f"[OK] {model_label} pk={pk}: {getattr(obj, field_name).url}"))
                synced += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"[FAILED] {model_label} pk={pk}: {exc}"))
                failed += 1

        self.stdout.write(self.style.SUCCESS(f"\nDone. Synced: {synced}, Failed: {failed}, Not found locally: {not_found}"))