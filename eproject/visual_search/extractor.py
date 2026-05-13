# visual_search/extractor.py
# Loads MobileNetV3 Small with pretrained ImageNet weights and strips the
# classification head so it outputs 576-dimensional feature vectors.
# The model is loaded once at module level (singleton) to avoid reloading
# per request. Vectors are L2-normalised so inner-product == cosine similarity.

import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# ── ImageNet normalisation transform ─────────────────────────────────────────
_TRANSFORM = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

# ── Expected output dimension for MobileNetV3 Small ─────────────────────────
VECTOR_DIM = 576


def _build_model() -> nn.Module:
    """Build MobileNetV3 Small with the classifier head replaced by Identity."""
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    # Strip the final classification layers; the adaptive-avg-pool output is 576-d
    model.classifier = nn.Identity()
    model.eval()
    return model


# Module-level singleton — loaded once when this module is first imported
_model: nn.Module = _build_model()


def extract_features(pil_image: Image.Image) -> np.ndarray:
    """
    Extract a 576-d L2-normalised feature vector from a PIL image.

    Args:
        pil_image: A PIL.Image.Image object (any mode; will be converted to RGB).

    Returns:
        A float32 numpy array of shape (576,) with unit L2 norm.
    """
    img = pil_image.convert("RGB")
    tensor = _TRANSFORM(img).unsqueeze(0)  # shape: (1, 3, 224, 224)

    with torch.no_grad():
        features = _model(tensor)           # shape: (1, 576)

    vec = features.squeeze().numpy().astype(np.float32)  # (576,)

    # L2 normalise so that inner-product search is equivalent to cosine similarity
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec
