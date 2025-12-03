# app/allergens.py
from pathlib import Path
import json
from typing import List

# app/allergens.py 기준으로 data 디렉터리 찾기
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ALLERGENS_PATH = DATA_DIR / "allergens.json"

print("DEBUG ALLERGENS_PATH =", ALLERGENS_PATH)

with open(ALLERGENS_PATH, "r", encoding="utf-8") as f:
    _allergen_db = json.load(f)


def get_allergens_by_en_name(en_name: str) -> List[str]:
    """영어 음식 이름(en_name)으로 알레르기 리스트 반환. 없으면 빈 리스트."""
    value = _allergen_db.get(en_name)
    if not value:
        return []
    # JSON에 ["대두", "밀"] 형태라고 가정
    if isinstance(value, list):
        return [str(x) for x in value]
    # 혹시 "대두;밀" 이런 형식이면 대응
    if isinstance(value, str):
        return [s.strip() for s in value.split(";") if s.strip()]
    return []
