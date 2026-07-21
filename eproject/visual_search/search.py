import json
from django.conf import settings

from .extractor import extract_features

_faiss_index = None
_id_map = None      

def _load_index():
    global _faiss_index, _id_map

    if _faiss_index is not None:
        return  

    import faiss  

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
    
    global _faiss_index, _id_map
    _faiss_index = None
    _id_map = None
    _load_index()


def search_similar(pil_image, top_k: int | None = None):
   
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
