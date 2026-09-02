import io
import json
import os
import faiss
import requests
from PIL import Image
from django.conf import settings

from .extractor import extract_features, VECTOR_DIM


def _load_product_image(product) -> Image.Image:
    """Loads a PIL Image for a product, handling both local files and remote Cloudinary URLs."""
    image_name = str(product.image.name) if product.image else ""
    if not image_name:
        raise ValueError(f"Product id={product.pk} has no image assigned.")

    # 1. Try local media disk first (fastest)
    if hasattr(settings, "MEDIA_ROOT") and settings.MEDIA_ROOT:
        local_path = os.path.join(settings.MEDIA_ROOT, image_name)
        if os.path.exists(local_path):
            return Image.open(local_path).convert("RGB")

    # 2. Try fetching from the remote storage URL (Cloudinary / S3)
    if hasattr(product.image, "url") and product.image.url:
        resp = requests.get(product.image.url, timeout=15)
        if resp.status_code == 200:
            return Image.open(io.BytesIO(resp.content)).convert("RGB")
        raise FileNotFoundError(
            f"HTTP {resp.status_code} fetching image from {product.image.url}"
        )

    # 3. Fallback to direct storage file handle
    with product.image.open("rb") as f:
        return Image.open(f).convert("RGB")


def build_index():
    from store.models import Product

    index_path = settings.VISUAL_SEARCH_INDEX_PATH
    map_path = settings.VISUAL_SEARCH_MAP_PATH

    index_path.parent.mkdir(parents=True, exist_ok=True)

    products = Product.objects.filter(is_available=True).order_by('id')
    total = products.count()

    if total == 0:
        print("[build_index] No products found in the database. Index not created.")
        return

    print(f"[build_index] Indexing {total} product(s)...")

    index = faiss.IndexFlatIP(VECTOR_DIM)
    id_map = []
    skipped = 0

    for i, product in enumerate(products, start=1):
        try:
            pil_image = _load_product_image(product)
            vec = extract_features(pil_image)
            index.add(vec.reshape(1, -1))
            id_map.append(product.pk)
            if i % 50 == 0 or i == total:
                print(f"[build_index]  {i}/{total} indexed")
        except Exception as exc:
            print(f"[build_index]  SKIP product id={product.pk}: {exc}")
            skipped += 1

    faiss.write_index(index, str(index_path))
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(id_map, f)

    print(
        f"[build_index] Done. Indexed {len(id_map)} products "
        f"(skipped {skipped}). Index saved to: {index_path}"
    )