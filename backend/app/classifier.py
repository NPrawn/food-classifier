# app/classifier.py
import io
import json
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = DATA_DIR / "models"

# 클래스 이름 로드
with open(DATA_DIR / "class_names_en.json", "r", encoding="utf-8") as f:
    CLASS_NAMES_EN = json.load(f)

with open(DATA_DIR / "class_names_ko.json", "r", encoding="utf-8") as f:
    CLASS_NAMES_KO = json.load(f)

# 모델 로드 (서버 시작 시 1번만)
MODEL = load_model(MODEL_DIR / "food100_v6_effb0.keras")

# app/classifier.py

IMG_SIZE = 224

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    업로드된 이미지 bytes -> 모델 입력 텐서로 변환
    EfficientNetB0: 입력은 0~255 float32, 정규화는 모델 안에서 수행된다고 가정.
    """
    # 1) bytes -> PIL 이미지
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # 2) 224x224 리사이즈
    image = image.resize((IMG_SIZE, IMG_SIZE))

    # 3) float32 배열 (0~255 그대로)
    img_array = np.array(image).astype("float32")

    # 4) 배치 차원 추가: (1, 224, 224, 3)
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


def predict(image_bytes: bytes) -> Tuple[str, str, float]:
    """
    이미지 bytes를 받아서
    - 영어 음식 이름
    - 한글 음식 이름
    - 확률(top-1)
    을 반환.
    """
    input_tensor = preprocess_image(image_bytes)
    preds = MODEL.predict(input_tensor)
    probs = preds[0]

    num_model_classes = len(probs)
    num_label_classes = len(CLASS_NAMES_EN)

    if num_model_classes == num_label_classes + 1:
        probs = probs[:num_label_classes]
    elif num_model_classes != num_label_classes:
        raise ValueError(
            f"Model output length ({num_model_classes}) "
            f"!= number of class names ({num_label_classes})"
        )

    top_idx = int(np.argmax(probs))
    top_prob = float(probs[top_idx])

    en_name = CLASS_NAMES_EN[top_idx]
    ko_name = CLASS_NAMES_KO.get(en_name, en_name)

    return en_name, ko_name, top_prob