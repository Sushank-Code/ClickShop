import os
from pathlib import Path
import numpy as np
from PIL import Image
import onnxruntime as ort
from django.conf import settings

# Expected output dimension for MobileNetV3 Small
VECTOR_DIM = 576

# ImageNet normalisation constants
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(3, 1, 1)
_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(3, 1, 1)

_session: ort.InferenceSession | None = None


def _get_session() -> ort.InferenceSession:
    """Initializes and returns the singleton ONNX inference session."""
    global _session
    if _session is None:
        model_path = None
        if settings.configured:
            model_path = getattr(settings, "VISUAL_SEARCH_MODEL_PATH", None)
        if not model_path:
            model_path = Path(__file__).resolve().parent / "mobilenetv3_small.onnx"

        if not os.path.exists(str(model_path)):
            raise FileNotFoundError(
                f"ONNX model file not found at '{model_path}'. "
                "Run `python -m visual_search.convert_to_onnx` first."
            )

        # Configure session options for lightweight CPU inference and lower RAM
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        opts.inter_op_num_threads = 1
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        _session = ort.InferenceSession(
            str(model_path),
            sess_options=opts,
            providers=["CPUExecutionProvider"],
        )
    return _session


def _preprocess_image(pil_image: Image.Image) -> np.ndarray:
    """Preprocesses a PIL image to match torchvision MobileNetV3 ImageNet pipeline:
    1. Convert to RGB
    2. Resize smaller edge to 256 (preserving aspect ratio)
    3. Center crop to 224x224
    4. Rescale pixel values to [0.0, 1.0]
    5. Normalize with ImageNet mean and std
    6. Return float32 array with shape (1, 3, 224, 224)
    """
    img = pil_image.convert("RGB")
    w, h = img.size

    # Resize smaller edge to 256 (Bilinear interpolation)
    if h < w:
        new_h = 256
        new_w = int(round(w * 256 / h))
    else:
        new_w = 256
        new_h = int(round(h * 256 / w))
    img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)

    # Center crop to 224x224
    left = (new_w - 224) // 2
    top = (new_h - 224) // 2
    img = img.crop((left, top, left + 224, top + 224))

    # Convert to float32 array in range [0, 1] with shape (3, 224, 224)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = np.transpose(arr, (2, 0, 1))

    # Normalize
    arr = (arr - _MEAN) / _STD

    # Add batch dimension -> (1, 3, 224, 224)
    return np.expand_dims(arr, axis=0).astype(np.float32)


def extract_features(pil_image: Image.Image) -> np.ndarray:
    """Extracts a 576-dimensional L2-normalized feature vector from a PIL image
    using the ONNX MobileNetV3-Small model.
    """
    tensor = _preprocess_image(pil_image)
    session = _get_session()

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: tensor})
    features = outputs[0]  # shape: (1, 576)

    vec = features.squeeze().astype(np.float32)  # (576,)

    # L2 normalise so that inner-product search is equivalent to cosine similarity
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec
