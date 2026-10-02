from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional
from model import predict_stock
from sentiment import analyze_sentiment

app = FastAPI(title="MarketMind ML & Multimodal Prediction Service")

# Lazily initialized multimodal service
_multimodal_service = None

def get_multimodal_service():
    global _multimodal_service
    if _multimodal_service is None:
        from multimodal_service import MultimodalPredictionService
        _multimodal_service = MultimodalPredictionService()
    return _multimodal_service


class PredictionRequest(BaseModel):
    stockId: int
    newsTitle: str = ""
    newsContent: str = ""
    confidenceThreshold: Optional[float] = 0.55


class PredictionResponse(BaseModel):
    prediction: str
    probability: float


class SentimentResponse(BaseModel):
    sentiment: float


@app.get("/")
def root():
    return {
        "message": "MarketMind Multimodal ML Service Running",
        "supported_stocks": ["AAPL (1)", "GOOGL (4)", "MSFT (5)", "AMZN (6)"],
        "endpoints": ["/predict", "/sentiment", "/predict/multimodal"]
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    prediction, probability = predict_stock(request.stockId)
    return PredictionResponse(
        prediction=prediction,
        probability=probability
    )


@app.post("/sentiment", response_model=SentimentResponse)
def sentiment(request: PredictionRequest):
    score = analyze_sentiment(
        request.newsTitle,
        request.newsContent
    )
    return SentimentResponse(
        sentiment=score
    )


@app.post("/predict/multimodal")
def predict_multimodal(request: PredictionRequest):
    service = get_multimodal_service()
    result = service.predict_multimodal(
        stock_id=request.stockId,
        news_title=request.newsTitle,
        news_content=request.newsContent,
        confidence_threshold=request.confidenceThreshold or 0.55
    )
    return result