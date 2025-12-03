# app/nutrition.py
import json
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

with open(DATA_DIR / "nutrition.json", "r", encoding="utf-8") as f:
    _nutrition_db: Dict[str, Any] = json.load(f)

def get_nutrition_by_en_name(en_name: str) -> Dict[str, Any]:
    """
    영어 음식 이름(en_name)을 받아서 nutrition.json에서 정보 반환.
    없으면 빈 dict 반환.
    """
    return _nutrition_db.get(en_name, {})