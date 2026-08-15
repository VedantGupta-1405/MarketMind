from fastapi import FastAPI
from pydantic import BaseModel
from model import predict_stock
from sentiment import analyze_sentiment

app = FastAPI()


class PredictionRequest(BaseModel):
    stockId: int
    newsTitle: str = ""
    newsContent: str = ""


class PredictionResponse(BaseModel):
    prediction: str
    probability: float


class SentimentResponse(BaseModel):
    sentiment: float


@app.get("/")
def root():
    return {"message": "ML Service Running"}


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