# visual_search/management/commands/build_index.py
# Django management command to trigger visual search index building.
# Run with: python manage.py build_index

from django.core.management.base import BaseCommand
from visual_search.indexer import build_index
from visual_search.search import reload_index

class Command(BaseCommand):
    help = "Builds the FAISS index and product ID mapping for visual search."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting FAISS visual search index build..."))
        try:
            build_index()
            # Force search module to reload the new index from disk
            try:
                reload_index()
            except FileNotFoundError:
                # Should not happen if build_index succeeds, but ignore if it does
                pass
            self.stdout.write(self.style.SUCCESS("Successfully built visual search index."))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Error building index: {exc}"))
