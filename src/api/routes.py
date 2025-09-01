from fastapi import APIRouter
from src.services.training import run_training_pipeline

router = APIRouter()

@router.post("/train")
def train():
    result = run_training_pipeline()
    return {"status": "success", "processed": len(result)}