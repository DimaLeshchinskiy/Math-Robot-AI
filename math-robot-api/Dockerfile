FROM python:3.12

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# 🔥 IMPORTANT PART: Bake Pix2Text model into the Docker image
# ---------------------------------------------------------------------------
# HuggingFace cache path is inside the image → persists forever
ENV HF_HOME=/root/.cache/huggingface

RUN python3 - <<EOF
from transformers import TrOCRProcessor
from optimum.onnxruntime import ORTModelForVision2Seq

MODEL = "breezedeus/pix2text-mfr-1.5"

print("📥 Downloading TrOCR processor...")
TrOCRProcessor.from_pretrained(MODEL)

print("📥 Downloading ONNX model...")
ORTModelForVision2Seq.from_pretrained(MODEL, use_cache=False)

print("✅ Pix2Text ONNX model cached in Docker image.")
EOF
# ---------------------------------------------------------------------------

# Copy application code
COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]