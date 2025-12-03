# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class NutritionInfo(BaseModel):
    unit: Optional[str] = None
    calories_kcal: Optional[float] = None
    carbs_g: Optional[float] = None
    protein_g: Optional[float] = None
    fat_g: Optional[float] = None

class PredictionResponse(BaseModel):
    en_name: str
    ko_name: str
    probability: float
    nutrition: NutritionInfo
    allergens: List[str]
