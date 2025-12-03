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
        calories_kcal=info.get("calories_kcal"),
        carbs_g=info.get("carbs_g"),
        protein_g=info.get("protein_g"),
        fat_g=info.get("fat_g"),
    )
    allergens = get_allergens_by_en_name(en_name)

    return PredictionResponse(
        en_name=en_name,
        ko_name=ko_name,
        probability=prob,
        nutrition=nutrition,
        allergens=allergens,
    )
