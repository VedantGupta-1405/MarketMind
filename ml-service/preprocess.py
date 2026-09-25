import numpy as np
from data_loader import fetch_stock_data
from sklearn.preprocessing import MinMaxScaler


FEATURE_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume"
]


FUTURE_DAYS = 5


def create_sequences(
    data,
    target,
    window_size=60,
    future_days=5
):
    X, y = [], []

    for i in range(
        window_size,
        len(data) - future_days
    ):
        X.append(
            data[
                i - window_size:i
            ]
        )

        y.append(
            target[i]
        )

    return np.array(X), np.array(y)


def preprocess_data(
    stock_id,
    window_size=60
):
    df = fetch_stock_data(
        stock_id
    )

    missing_columns = [
        column
        for column in FEATURE_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    data = df[
        FEATURE_COLUMNS
    ].copy()

    data = data.dropna()

    if len(data) <= (
        window_size + FUTURE_DAYS
    ):
        raise ValueError(
            f"Not enough data for sequence creation. "
            f"Required > "
            f"{window_size + FUTURE_DAYS}, "
            f"got {len(data)}"
        )

    close_prices = data[
        "Close"
    ].values

    target = (
        close_prices[
            FUTURE_DAYS:
        ] >
        close_prices[
            :-FUTURE_DAYS
        ]
    ).astype(
        np.float32
    )

    scaler = MinMaxScaler(
        feature_range=(0, 1)
    )

    scaled_data = scaler.fit_transform(
        data
    )

    usable_data = scaled_data[
        :-FUTURE_DAYS
    ]

    X, y = create_sequences(
        usable_data,
        target,
        window_size,
        FUTURE_DAYS
    )

    if len(X) == 0 or len(y) == 0:
        raise ValueError(
            "Sequence generation failed — empty dataset"
        )

    return X, y, scaler