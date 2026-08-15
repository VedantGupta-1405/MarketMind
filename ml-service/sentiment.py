from transformers import pipeline


sentiment_model = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert"
)


def analyze_sentiment(news_title, news_content):

    text = f"{news_title}. {news_content}".strip()

    if not text:
        return 0.0

    result = sentiment_model(text[:2000])[0]

    label = result["label"].lower()
    confidence = result["score"]

    if label == "positive":
        return float(confidence)

    if label == "negative":
        return float(-confidence)

    return 0.0