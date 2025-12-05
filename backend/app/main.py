# app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from .schemas import PredictionResponse, NutritionInfo
from .classifier import predict
from .nutrition import get_nutrition_by_en_name
from .allergens import get_allergens_by_en_name

app = FastAPI(
    title="Food Classification API",
    description="음식 사진 업로드 → 음식 이름 + 영양/알레르기 정보 반환",
    version="0.1.0",
)

# CORS (나중에 프론트 붙일 때 필요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시 도메인 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Food Classification API 서버 작동 중"}

@app.post("/predict", response_model=PredictionResponse)
async def predict_food(file: UploadFile = File(...)):
    # 업로드된 파일 읽기
    image_bytes = await file.read()

    # 1) 모델로 음식 분류
    en_name, ko_name, prob = predict(image_bytes)

    # 2) 영양/알레르기 정보 조회
    info = get_nutrition_by_en_name(en_name)
    nutrition = NutritionInfo(
        unit=info.get("unit"),

        # 기본 6개
        calories_kcal=info.get("calories_kcal"),
        carbs_g=info.get("carbs_g"),
        protein_g=info.get("protein_g"),
        fat_g=info.get("fat_g"),
        sugars_g=info.get("sugars_g"),
        sodium_mg=info.get("sodium_mg"),

        # 상세 18개
        moisture_g=info.get("moisture_g"),
        ash_g=info.get("ash_g"),
        dietary_fiber_g=info.get("dietary_fiber_g"),
        calcium_mg=info.get("calcium_mg"),
        iron_mg=info.get("iron_mg"),
        phosphorus_mg=info.get("phosphorus_mg"),
        potassium_mg=info.get("potassium_mg"),
        vitamin_a_ug_rae=info.get("vitamin_a_ug_rae"),
        retinol_ug=info.get("retinol_ug"),
        beta_carotene_ug=info.get("beta_carotene_ug"),
        thiamin_mg=info.get("thiamin_mg"),
        riboflavin_mg=info.get("riboflavin_mg"),
        niacin_mg=info.get("niacin_mg"),
        vitamin_c_mg=info.get("vitamin_c_mg"),
        vitamin_d_ug=info.get("vitamin_d_ug"),
        cholesterol_mg=info.get("cholesterol_mg"),
        saturated_fatty_acids_g=info.get("saturated_fatty_acids_g"),
        trans_fatty_acids_g=info.get("trans_fatty_acids_g"),
    )
    allergens = get_allergens_by_en_name(en_name)

    return PredictionResponse(
        en_name=en_name,
        ko_name=ko_name,
        probability=prob,
        nutrition=nutrition,
        allergens=allergens,
    )
