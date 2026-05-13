from django.apps import AppConfig


class VisualSearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "visual_search"
    verbose_name = "Visual Search"

    def ready(self):
        """
        Pre-load the feature extractor model when Django starts.
        Wrapped in a broad try/except so the server starts even if torch
        is not installed in the current environment.
        """
        try:
            # Importing the module triggers the module-level singleton build
            from . import extractor  # noqa: F401
            print("[visual_search] MobileNetV3 feature extractor loaded successfully.")
        except Exception as exc:
            print(
                f"[visual_search] WARNING: Could not pre-load feature extractor: {exc}. "
                "Visual search will be unavailable."
            )

