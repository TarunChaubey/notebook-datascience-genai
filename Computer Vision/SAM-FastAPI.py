import io
import time
import uuid
import logging
import asyncio
import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from PIL import Image
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from osam._models.yoloworld.clip import tokenize

# LOGGING
logging.basicConfig(
    filename="sam3_api_logs.txt",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("SAM3_API")

# FASTAPI APP
app = FastAPI(title="SAM3 Segmentation API")

# THREAD POOL (CPU-bound inference)
INFERENCE_POOL = ThreadPoolExecutor(max_workers=10)

# ONNX SESSION OPTIONS (Prevent CPU Oversubscription)
sess_opts = ort.SessionOptions()
sess_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
sess_opts.intra_op_num_threads = 1
sess_opts.inter_op_num_threads = 1

# LOAD MODELS (Once at Startup)
try:
    sess_image = ort.InferenceSession(
        "models/sam3_image_encoder.onnx",
        sess_options=sess_opts,
        providers=["CPUExecutionProvider"],
    )

    sess_language = ort.InferenceSession(
        "models/sam3_language_encoder.onnx",
        sess_options=sess_opts,
        providers=["CPUExecutionProvider"],
    )

    sess_decode = ort.InferenceSession(
        "models/sam3_decoder.onnx",
        sess_options=sess_opts,
        providers=["CPUExecutionProvider"],
    )

    logger.info("SAM3 ONNX models loaded successfully")

except Exception as e:
    logger.exception("Failed to load ONNX models")
    raise RuntimeError("Model loading failed") from e


# WARMUP (Removes Cold Start Latency)
def warmup():
    try:
        dummy_img = np.zeros((3, 1008, 1008), dtype=np.uint8)
        sess_image.run(None, {"image": dummy_img})
        logger.info("Warmup completed")
    except Exception:
        logger.warning("Warmup failed (non-critical)")

warmup()
# UTILITIES
def preprocess_image(image: Image.Image):
    """Preprocess image for SAM3 (uint8, CHW)."""
    img = image.convert("RGB")
    img_resized = img.resize((1008, 1008))
    tensor = np.asarray(img_resized, dtype=np.uint8).transpose(2, 0, 1)
    return img, tensor

@lru_cache(maxsize=128)
def encode_text(text: str):
    """Cached language encoding."""
    tokens = tokenize([text], context_length=32)
    return sess_language.run(None, {"tokens": tokens})

def prepare_prompt_inputs(
    text_prompt: Optional[str],
    box_prompt: Optional[List[float]],
    point_prompt: Optional[List[float]],
):
    """Prepare spatial and language prompts."""
    # Spatial prompt
    if box_prompt is not None:
        box_coords = np.array(box_prompt, dtype=np.float32).reshape(1, 1, 4)
        box_masks = np.array([[False]], dtype=np.bool_)

    elif point_prompt is not None:
        px, py = point_prompt
        eps = 0.001
        box_coords = np.array([px, py, eps, eps], dtype=np.float32).reshape(1, 1, 4)
        box_masks = np.array([[False]], dtype=np.bool_)

    else:
        box_coords = np.zeros((1, 1, 4), dtype=np.float32)
        box_masks = np.array([[True]], dtype=np.bool_)

    box_labels = np.array([[1]], dtype=np.int64)

    # Language prompt
    text = text_prompt or "visual"
    language_mask, language_features, _ = encode_text(text)

    return box_coords, box_labels, box_masks, language_mask, language_features


def run_inference(image_tensor, original_image, prompt_inputs):
    """Run SAM3 inference inside thread pool."""
    box_coords, box_labels, box_masks, language_mask, language_features = prompt_inputs

    # Image encoder
    vision_out = sess_image.run(None, {"image": image_tensor})
    vision_pos_enc = vision_out[:3]
    backbone_fpn = vision_out[3:]

    # Decoder
    boxes, scores, masks = sess_decode.run(
        None,
        {
            "original_height": np.array(original_image.height, dtype=np.int64),
            "original_width": np.array(original_image.width, dtype=np.int64),
            "backbone_fpn_0": backbone_fpn[0],
            "backbone_fpn_1": backbone_fpn[1],
            "backbone_fpn_2": backbone_fpn[2],
            "vision_pos_enc_2": vision_pos_enc[2],
            "language_mask": language_mask,
            "language_features": language_features,
            "box_coords": box_coords,
            "box_labels": box_labels,
            "box_masks": box_masks,
        },
    )
    return boxes, scores, masks


# API ENDPOINT
@app.post("/segment")
async def segment(
    request: Request,
    file: UploadFile = File(...),
    text_prompt: Optional[str] = Form(None),
    box_prompt: Optional[str] = Form(None),
    point_prompt: Optional[str] = Form(None),
):
    request_id = str(uuid.uuid4())
    start_total = time.perf_counter()

    try:
        # Validate box prompt
        box_vals = None
        if box_prompt:
            parts = box_prompt.split(",")
            if len(parts) != 4:
                raise HTTPException(
                    status_code=400,
                    detail="box_prompt must contain 4 comma-separated values",
                )
            box_vals = [float(x) for x in parts]

        # Validate point prompt
        point_vals = None
        if point_prompt:
            parts = point_prompt.split(",")
            if len(parts) != 2:
                raise HTTPException(
                    status_code=400,
                    detail="point_prompt must contain 2 comma-separated values",
                )
            point_vals = [float(x) for x in parts]

        # Load image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Preprocess
        original_image, image_tensor = preprocess_image(image)

        # Prepare prompts
        prompt_inputs = prepare_prompt_inputs(text_prompt, box_vals, point_vals)

        # Run inference in thread pool
        loop = asyncio.get_running_loop()
        start_infer = time.perf_counter()

        boxes, scores, masks = await loop.run_in_executor(
            INFERENCE_POOL,
            run_inference,
            image_tensor,
            original_image,
            prompt_inputs,
        )

        infer_latency = time.perf_counter() - start_infer
        total_latency = time.perf_counter() - start_total

        logger.info(
            "[%s] Completed | Inference: %.3fs | Total: %.3fs",
            request_id,
            infer_latency,
            total_latency,
        )

        return {
            "request_id": request_id,
            "latency_sec": round(infer_latency, 3),
            "boxes": boxes.tolist(),
            "scores": scores.tolist(),
            "masks": masks.astype(np.uint8).tolist(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[%s] Request failed", request_id)
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")
