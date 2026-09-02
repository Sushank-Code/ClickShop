"""
One-time script to convert the PyTorch MobileNetV3-Small feature extractor
to ONNX format.

Usage (run from the project root):
    python -m visual_search.convert_to_onnx

Produces:
    visual_search/mobilenetv3_small.onnx

After this file is generated and committed to Git, torch and torchvision
are no longer needed at runtime — onnxruntime replaces them.
"""

import os
import sys
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import torch
import torch.nn as nn
from torchvision import models


def main():
    # ── 1. Build the same model used in the original extractor ──────────
    print("[convert] Loading MobileNetV3-Small with ImageNet weights ...")
    model = models.mobilenet_v3_small(
        weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1,
    )
    model.classifier = nn.Identity()   # remove classification head
    model.eval()

    # ── 2. Create a dummy input matching the preprocessing pipeline ─────
    #       (batch=1, channels=3, height=224, width=224)
    dummy_input = torch.randn(1, 3, 224, 224)

    # ── 3. Export to ONNX ───────────────────────────────────────────────
    onnx_path = os.path.join(os.path.dirname(__file__), "mobilenetv3_small.onnx")

    print(f"[convert] Exporting to ONNX -> {onnx_path}")
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input":  {0: "batch"},
            "output": {0: "batch"},
        },
        opset_version=18,
    )

    # ── 4. Verify: compare PyTorch vs ONNX outputs ─────────────────────
    import onnxruntime as ort

    session = ort.InferenceSession(onnx_path)

    with torch.no_grad():
        pt_out = model(dummy_input).numpy()

    ort_out = session.run(None, {"input": dummy_input.numpy()})[0]

    max_diff = np.max(np.abs(pt_out - ort_out))
    print(f"[convert] Max absolute difference (PyTorch vs ONNX): {max_diff:.2e}")

    if max_diff < 1e-5:
        print("[convert] [SUCCESS] Outputs match. ONNX model is ready.")
    else:
        print("[convert] [WARNING] Outputs differ - inspect manually before using.")

    file_size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
    print(f"[convert] ONNX model size: {file_size_mb:.1f} MB")
    print(f"[convert] Saved to: {onnx_path}")


if __name__ == "__main__":
    main()
