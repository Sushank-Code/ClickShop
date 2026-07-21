from django.apps import AppConfig

class VisualSearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "visual_search"
    verbose_name = "Visual Search"

    def ready(self):
        # Pre-load the feature extractor model when Django starts.
        try:
            from . import extractor  
            print("[visual_search] MobileNetV3 feature extractor loaded successfully.")
        except Exception as exc:
            print(
                f"[visual_search] WARNING: Could not pre-load feature extractor: {exc}. "
                "Visual search will be unavailable."
            )