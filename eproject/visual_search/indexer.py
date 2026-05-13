# visual_search/indexer.py
# Iterates over all Products in the database, extracts a 576-d feature vector
# for each product image using MobileNetV3 Small, and builds a FAISS
# IndexFlatIP (inner-product / cosine similarity) index stored as a flat file.
# A companion JSON file maps each FAISS position → Product primary key.

import json
import os
import numpy as np
import faiss
from PIL import Image
from django.conf import settings

from .extractor import extract_features, VECTOR_DIM


def build_index():
    """
    Build (or rebuild) the FAISS index from all Product objects currently
    in the database.

    Files written:
        VISUAL_SEARCH_INDEX_PATH  → FAISS binary index
        VISUAL_SEARCH_MAP_PATH    → JSON list mapping position → product_id
    """
    # Import here to avoid circular imports at module load time
    from store.models import Product

    index_path = settings.VISUAL_SEARCH_INDEX_PATH
    map_path = settings.VISUAL_SEARCH_MAP_PATH

    # Ensure parent directories exist
    index_path.parent.mkdir(parents=True, exist_ok=True)

    products = Product.objects.filter(is_available=True).order_by('id')
    total = products.count()

    if total == 0:
        print("[build_index] No products found in the database. Index not created.")
        return

    print(f"[build_index] Indexing {total} product(s)…")

    index = faiss.IndexFlatIP(VECTOR_DIM)   # Inner-product index (cosine on unit vecs)
    id_map = []                              # position in FAISS → Product.pk

    skipped = 0
    for i, product in enumerate(products, start=1):
        try:
            # Build the absolute path to the image from MEDIA_ROOT
            img_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
            pil_image = Image.open(img_path).convert("RGB")
            vec = extract_features(pil_image)                       # (576,) float32
            index.add(vec.reshape(1, -1))                           # add row
            id_map.append(product.pk)
            if i % 50 == 0 or i == total:
                print(f"[build_index]  {i}/{total} indexed")
        except Exception as exc:
            print(f"[build_index]  SKIP product id={product.pk}: {exc}")
            skipped += 1

    # Persist index
    faiss.write_index(index, str(index_path))

    # Persist position → product_id mapping
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(id_map, f)

    print(
        f"[build_index] Done. Indexed {len(id_map)} products "
        f"(skipped {skipped}). "
        f"Index saved to: {index_path}"
    )
