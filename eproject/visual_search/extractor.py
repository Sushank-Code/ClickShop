import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# ImageNet normalisation transform 
_TRANSFORM = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

# Expected output dimension for MobileNetV3 Small 
VECTOR_DIM = 576


def _build_model() -> nn.Module:

    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    model.classifier = nn.Identity()
    model.eval()
    return model

_model: nn.Module = _build_model()


def extract_features(pil_image: Image.Image) -> np.ndarray:

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
