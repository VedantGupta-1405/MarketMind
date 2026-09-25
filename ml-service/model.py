import os

from preprocess import preprocess_data

from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Input


MODEL_PATH = "model.h5"


def build_model(input_shape):
    model = Sequential()

    model.add(
        Input(
            shape=input_shape
        )
    )

    model.add(
        LSTM(
            50,
            return_sequences=True
        )
    )

    model.add(
        LSTM(50)
    )

    model.add(
        Dense(
            1,
            activation="sigmoid"
        )
    )

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    return model


def get_model():
    if os.path.exists(MODEL_PATH):
        print("Loading existing model...")
        return load_model(MODEL_PATH)

    print("Training new model...")

    X, y, scaler = preprocess_data(
        stock_id=1
    )

    model = build_model(
        (
            X.shape[1],
            X.shape[2]
        )
    )

    model.fit(
        X,
        y,
        epochs=10,
        batch_size=32,
        verbose=1
    )

    model.save(
        MODEL_PATH
    )

    print("Model saved!")

    return model


model = get_model()


def predict_stock(stock_id):
    X, y, scaler = preprocess_data(
        stock_id
    )

    last_sequence = X[-1:]

    probability = model.predict(
        last_sequence,
        verbose=0
    )[0][0]

    if probability >= 0.5:
        direction = "UP"
    else:
        direction = "DOWN"

    return direction, float(round(probability, 4))