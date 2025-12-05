# build_nutrition_json.py
import json
import math
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent

MANUAL_FOOD_NAME = {
    # 영어 클래스 이름: CSV에 있는 정확한 식품명
    "Dried_Pollack_Soup": "북어국",
    "Fried_Chicken": "닭튀김_황금올리브 치킨",
    "Gochujang_Stir_Fried_Dried_Pollack": "오징어채볶음",
    "Ricecake_Dumpling_Soup": "떡만두국",
    "Stir_Fried_Potato": "감자볶음_채소",
    "Young_Radish_Cold_Noodles": "국수_열무김치",
    "Bossam": "제육(돼지고기 수육)",
    "Bulgogi": "돼지불고기_간장",
    "Dumplings": "고기만두",
    "Fish_Pancake": "생선전_동태",
    "Kimchi_Fried_Rice": "볶음밥_김치_돼지고기",
    "Seasoned_Chicken": "닭튀김_양념 치킨",
    "Stir_Fried_Zucchini": "애호박 볶음",
}

# 1) 경로 설정: CSV + 클래스 이름들
CSV_PATH = DATA_DIR / "식품의약품안전처_통합식품영양성분정보(음식)_20250408.csv"
CLASS_EN_PATH = DATA_DIR / "class_names_en.json"
CLASS_KO_PATH = DATA_DIR / "class_names_ko.json"
OUTPUT_PATH = DATA_DIR / "nutrition.json"

print("CSV:", CSV_PATH)
print("class_names_en:", CLASS_EN_PATH)
print("class_names_ko:", CLASS_KO_PATH)
print("-> will write nutrition.json to:", OUTPUT_PATH)

# 2) 로드
df = pd.read_csv(CSV_PATH, encoding="utf-8")

with open(CLASS_EN_PATH, "r", encoding="utf-8") as f:
    class_names_en = json.load(f)

with open(CLASS_KO_PATH, "r", encoding="utf-8") as f:
    class_names_ko = json.load(f)  # {en_name: ko_name}

# 3) 영양정보에서 필요한 컬럼만 추리기
#   (네가 준 24개 성분 전부 + 식품명, 기준량)
df_small = df[[
    "식품명",
    "영양성분함량기준량",
    "에너지(kcal)",
    "수분(g)",
    "단백질(g)",
    "지방(g)",
    "회분(g)",
    "탄수화물(g)",
    "당류(g)",
    "식이섬유(g)",
    "칼슘(mg)",
    "철(mg)",
    "인(mg)",
    "칼륨(mg)",
    "나트륨(mg)",
    "비타민 A(μg RAE)",
    "레티놀(μg)",
    "베타카로틴(μg)",
    "티아민(mg)",
    "리보플라빈(mg)",
    "니아신(mg)",
    "비타민 C(mg)",
    "비타민 D(μg)",
    "콜레스테롤(mg)",
    "포화지방산(g)",
    "트랜스지방산(g)",
]]

# 4) Name 매칭을 위한 간단한 규칙들
SUFFIXES = ["무침", "볶음", "구이", "조림", "국", "탕", "찜", "덮밥",
            "죽", "전골", "전", "튀김", "볶음밥", "김밥", "나물"]


def choose_row_for(food_ko: str):
    """한글 음식명으로 CSV에서 best row 하나 뽑기."""
    if not isinstance(food_ko, str) or not food_ko:
        return None

    # 1) 그대로 포함 검색
    subset = df_small[df_small["식품명"].str.contains(food_ko, na=False)]
    if subset.empty:
        # 2) 접미사(무침/볶음/국...) 떼고 다시 검색
        base = food_ko
        for suf in SUFFIXES:
            if base.endswith(suf):
                base = base[:-len(suf)]
                break
        # 너무 짧으면 패스
        if len(base) >= 2:
            subset = df_small[df_small["식품명"].str.contains(base, na=False)]

    if subset.empty:
        return None

    # 3) 완전 일치가 있으면 그걸 우선
    exact = subset[subset["식품명"] == food_ko]
    if not exact.empty:
        return exact.iloc[0]

    # 4) 아니면 첫 번째 후보 (추후 수동 보정 가능)
    return subset.iloc[0]


def _num(x):
    """NaN / 공백 / '-' 등을 None으로 처리 후 float 변환."""
    if pd.isna(x):
        return None
    s = str(x).strip()
    if s in ("", "-", "NaN", "nan"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


nutrition_map = {}
missing = []

for en_name in class_names_en:
    ko_name = class_names_ko.get(en_name)
    row = choose_row_for(ko_name)

    # 수동 매핑 우선 적용
    if row is None and en_name in MANUAL_FOOD_NAME:
        manual_name = MANUAL_FOOD_NAME[en_name]
        cand = df_small[df_small["식품명"] == manual_name]
        if not cand.empty:
            row = cand.iloc[0]

    if row is None:
        missing.append((en_name, ko_name))
        nutrition_map[en_name] = {
            "ko_name": ko_name,
            "source_food_name": None,
            "unit": None,
            # 기본 6개
            "calories_kcal": None,
            "carbs_g": None,
            "protein_g": None,
            "fat_g": None,
            "sugars_g": None,
            "sodium_mg": None,
            # 상세 18개
            "moisture_g": None,
            "ash_g": None,
            "dietary_fiber_g": None,
            "calcium_mg": None,
            "iron_mg": None,
            "phosphorus_mg": None,
            "potassium_mg": None,
            "vitamin_a_ug_rae": None,
            "retinol_ug": None,
            "beta_carotene_ug": None,
            "thiamin_mg": None,
            "riboflavin_mg": None,
            "niacin_mg": None,
            "vitamin_c_mg": None,
            "vitamin_d_ug": None,
            "cholesterol_mg": None,
            "saturated_fatty_acids_g": None,
            "trans_fatty_acids_g": None,
            # 알레르기는 별도 파일에서 관리하지만, 형식 맞추고 싶으면 유지
            "allergens": [],
        }
        continue

    nutrition_map[en_name] = {
        "ko_name": ko_name,
        "source_food_name": str(row["식품명"]),
        "unit": str(row["영양성분함량기준량"]),

        # --- 기본 세트 6개 ---
        "calories_kcal": _num(row["에너지(kcal)"]),
        "carbs_g": _num(row["탄수화물(g)"]),
        "protein_g": _num(row["단백질(g)"]),
        "fat_g": _num(row["지방(g)"]),
        "sugars_g": _num(row["당류(g)"]),
        "sodium_mg": _num(row["나트륨(mg)"]),

        # --- 상세 세트 18개 ---
        "moisture_g": _num(row["수분(g)"]),
        "ash_g": _num(row["회분(g)"]),
        "dietary_fiber_g": _num(row["식이섬유(g)"]),
        "calcium_mg": _num(row["칼슘(mg)"]),
        "iron_mg": _num(row["철(mg)"]),
        "phosphorus_mg": _num(row["인(mg)"]),
        "potassium_mg": _num(row["칼륨(mg)"]),
        "vitamin_a_ug_rae": _num(row["비타민 A(μg RAE)"]),
        "retinol_ug": _num(row["레티놀(μg)"]),
        "beta_carotene_ug": _num(row["베타카로틴(μg)"]),
        "thiamin_mg": _num(row["티아민(mg)"]),
        "riboflavin_mg": _num(row["리보플라빈(mg)"]),
        "niacin_mg": _num(row["니아신(mg)"]),
        "vitamin_c_mg": _num(row["비타민 C(mg)"]),
        "vitamin_d_ug": _num(row["비타민 D(μg)"]),
        "cholesterol_mg": _num(row["콜레스테롤(mg)"]),
        "saturated_fatty_acids_g": _num(row["포화지방산(g)"]),
        "trans_fatty_acids_g": _num(row["트랜스지방산(g)"]),

        # 알레르기는 별도 allergens.json에서 관리할 거라, 여기선 비워둠
        "allergens": [],
    }

# 5) JSON으로 저장
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(nutrition_map, f, ensure_ascii=False, indent=2)

print(f"✅ nutrition.json saved to {OUTPUT_PATH}")
print("자동 매칭되지 않은 항목 (수동 확인 필요):")
for en, ko in missing:
    print(f" - {en} / {ko}")
