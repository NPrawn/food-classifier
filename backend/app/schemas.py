# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class NutritionInfo(BaseModel):
    unit: Optional[str] = None  # 기준량 (예: "100 g")

    # --- 기본 세트(6개) ---
    calories_kcal: Optional[float] = None   # 에너지(kcal)
    carbs_g: Optional[float] = None         # 탄수화물(g)
    protein_g: Optional[float] = None       # 단백질(g)
    fat_g: Optional[float] = None           # 지방(g)
    sugars_g: Optional[float] = None        # 당류(g)
    sodium_mg: Optional[float] = None       # 나트륨(mg)

    # --- 상세 영역(나머지 18개) ---
    moisture_g: Optional[float] = None              # 수분(g)
    ash_g: Optional[float] = None                   # 회분(g)
    dietary_fiber_g: Optional[float] = None         # 식이섬유(g)
    calcium_mg: Optional[float] = None              # 칼슘(mg)
    iron_mg: Optional[float] = None                 # 철(mg)
    phosphorus_mg: Optional[float] = None           # 인(mg)
    potassium_mg: Optional[float] = None            # 칼륨(mg)
    vitamin_a_ug_rae: Optional[float] = None        # 비타민 A(μg RAE)
    retinol_ug: Optional[float] = None              # 레티놀(μg)
    beta_carotene_ug: Optional[float] = None        # 베타카로틴(μg)
    thiamin_mg: Optional[float] = None              # 티아민(mg)
    riboflavin_mg: Optional[float] = None           # 리보플라빈(mg)
    niacin_mg: Optional[float] = None               # 니아신(mg)
    vitamin_c_mg: Optional[float] = None            # 비타민 C(mg)
    vitamin_d_ug: Optional[float] = None            # 비타민 D(μg)
    cholesterol_mg: Optional[float] = None          # 콜레스테롤(mg)
    saturated_fatty_acids_g: Optional[float] = None # 포화지방산(g)
    trans_fatty_acids_g: Optional[float] = None     # 트랜스지방산(g)

class PredictionResponse(BaseModel):
    en_name: str
    ko_name: str
    probability: float
    nutrition: NutritionInfo
    allergens: List[str]
