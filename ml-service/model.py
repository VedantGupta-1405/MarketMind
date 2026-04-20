# ml-service/model.py

import os
import numpy as np
from preprocess import preprocess_data
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense

MODEL_PATH = "model.h5"

# =========================
# CREATE MODEL ARCHITECTURE
# =========================
def build_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


# =========================
# LOAD OR TRAIN MODEL
# =========================
def get_model():
    if os.path.exists(MODEL_PATH):
        print("Loading existing model...")
        return load_model(MODEL_PATH)
    else:
        print("Training new model...")

        X, y, scaler = preprocess_data(stock_id=1)

        model = build_model((X.shape[1], 1))
        model.fit(X, y, epochs=3, batch_size=32, verbose=1)

        model.save(MODEL_PATH)
        print("Model saved!")

        return model


# Load model once (important)
model = get_model()


# =========================
# PREDICTION FUNCTION
# =========================
def predict_stock(stock_id):
    X, y, scaler = preprocess_data(stock_id)

    last_sequence = X[-1:]

    prediction = model.predict(last_sequence, verbose=0)
    prediction = scaler.inverse_transform(prediction)

    current_price = scaler.inverse_transform(
        y[-1].reshape(-1, 1)
    )[0][0]

    predicted_price = prediction[0][0]

    # 🔥 Direction
    if predicted_price > current_price:
        direction = "UP"
    else:
        direction = "DOWN"

    # 🔥 REAL CONFIDENCE (based on % change)
    diff = abs(predicted_price - current_price)
    confidence = diff / current_price

    # clamp to reasonable range
    confidence = max(0.1, min(confidence, 1.0))

    return direction, float(round(confidence, 2))