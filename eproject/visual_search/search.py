# visual_search/search.py
# Loads the FAISS index and position→product_id map from disk at module level
# (singleton). Exposes search_similar() which accepts a PIL image and returns
# an ordered list of Product IDs that are visually similar to the query image.

import json
import numpy as np
from django.conf import settings

from .extractor import extract_features

# ── Module-level singletons ──────────────────────────────────────────────────
_faiss_index = None
_id_map = None       # list: FAISS position → Product.pk


def _load_index():
    """Load the FAISS index and id map from disk (called lazily on first search)."""
    global _faiss_index, _id_map

    if _faiss_index is not None:
        return  # Already loaded

    import faiss  # imported here so Django starts even if faiss is missing

    index_path = settings.VISUAL_SEARCH_INDEX_PATH
    map_path = settings.VISUAL_SEARCH_MAP_PATH

    if not index_path.exists() or not map_path.exists():
        print(f"[visual_search] WARNING: FAISS index or map not found at '{index_path}'. "
              "Search will return empty results until products are indexed.")
        return

    _faiss_index = faiss.read_index(str(index_path))

    with open(map_path, "r", encoding="utf-8") as f:
        _id_map = json.load(f)


def reload_index():
    """Force a reload of the FAISS index from disk (call after re-indexing)."""
    global _faiss_index, _id_map
    _faiss_index = None
    _id_map = None
    _load_index()


def search_similar(pil_image, top_k: int | None = None):
    """
    Find the top-k most visually similar products to the given image.

    Args:
        pil_image: PIL.Image.Image query image (any mode).
        top_k: Number of results to return. Defaults to VISUAL_SEARCH_TOP_K.

    Returns:
        List of Product primary keys ordered by descending similarity score.

    Raises:
        FileNotFoundError: If the FAISS index has not been built yet.
    """
    if top_k is None:
        top_k = getattr(settings, "VISUAL_SEARCH_TOP_K", 10)

    _load_index()

    if _faiss_index is None:
        return []

    vec = extract_features(pil_image).reshape(1, -1)  # (1, 576) float32

    k = min(top_k, _faiss_index.ntotal)
    if k == 0:
        return []

    _scores, indices = _faiss_index.search(vec, k)   # indices shape: (1, k)

    product_ids = []
    for idx in indices[0]:
        if idx == -1:                   # FAISS returns -1 for empty slots
            continue
        product_ids.append(_id_map[int(idx)])

    return product_ids
