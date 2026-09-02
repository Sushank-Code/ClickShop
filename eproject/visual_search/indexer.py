import json, faiss
from PIL import Image
from django.conf import settings

from .extractor import extract_features, VECTOR_DIM


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

    print(f"[build_index] Indexing {total} product(s)…")

    index = faiss.IndexFlatIP(VECTOR_DIM)
    id_map = []
    skipped = 0

    for i, product in enumerate(products, start=1):
        try:
            with product.image.open("rb") as f:
                pil_image = Image.open(f).convert("RGB")
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

    print(f"[build_index] Done. Indexed {len(id_map)} products (skipped {skipped}). Index saved to: {index_path}")