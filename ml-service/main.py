from fastapi import FastAPI
from pydantic import BaseModel
from model import predict_stock

app = FastAPI()


class PredictionRequest(BaseModel):
    stockId: int
    newsTitle: str = ""
    newsContent: str = ""


class PredictionResponse(BaseModel):
    prediction: str
    probability: float


@app.get("/")
def root():
    return {"message": "ML Service Running"}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):

    prediction, probability = predict_stock(
        request.stockId,
        request.newsTitle,
        request.newsContent
    )

    return PredictionResponse(
        prediction=prediction,
        probability=probability
    )