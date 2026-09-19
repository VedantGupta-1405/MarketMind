DROP TABLE IF EXISTS sentiment;
DROP TABLE IF EXISTS decisions;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS news;
DROP TABLE IF EXISTS price_history;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS portfolio;
DROP TABLE IF EXISTS stocks;

CREATE TABLE stocks (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    price DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO stocks (id, name, symbol, price)
VALUES
    (1, 'Apple Inc.', 'AAPL', 150.00),
    (4, 'Alphabet Inc.', 'GOOGL', NULL),
    (5, 'Microsoft Corp.', 'MSFT', NULL),
    (6, 'Amazon.com Inc.', 'AMZN', NULL);

SELECT setval(
    pg_get_serial_sequence('stocks', 'id'),
    (SELECT MAX(id) FROM stocks)
);

CREATE TABLE portfolio (
    id BIGSERIAL PRIMARY KEY,
    stock_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    average_price DOUBLE PRECISION NOT NULL,
    CONSTRAINT fk_portfolio_stock
        FOREIGN KEY (stock_id)
        REFERENCES stocks(id)
);

CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    stock_id BIGINT NOT NULL,
    type VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transaction_stock
        FOREIGN KEY (stock_id)
        REFERENCES stocks(id)
);

CREATE TABLE price_history (
    id BIGSERIAL PRIMARY KEY,
    stock_id BIGINT NOT NULL,
    date DATE NOT NULL,
    open_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    volume BIGINT,
    CONSTRAINT fk_price_history_stock
        FOREIGN KEY (stock_id)
        REFERENCES stocks(id)
        ON DELETE CASCADE
);

CREATE TABLE news (
    id BIGSERIAL PRIMARY KEY,
    stock_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    published_at TIMESTAMP,
    url TEXT NOT NULL UNIQUE,
    CONSTRAINT fk_news_stock
        FOREIGN KEY (stock_id)
        REFERENCES stocks(id)
        ON DELETE CASCADE
);

CREATE TABLE sentiment (
    id BIGSERIAL PRIMARY KEY,
    score DOUBLE PRECISION NOT NULL,
    news_id BIGINT NOT NULL UNIQUE,
    CONSTRAINT fk_sentiment_news
        FOREIGN KEY (news_id)
        REFERENCES news(id)
        ON DELETE CASCADE
);

CREATE TABLE predictions (
    id BIGSERIAL PRIMARY KEY,
    stock_id BIGINT NOT NULL,
    prediction VARCHAR(255),
    probability DOUBLE PRECISION,
    created_at TIMESTAMP,
    CONSTRAINT fk_prediction_stock
        FOREIGN KEY (stock_id)
        REFERENCES stocks(id)
        ON DELETE CASCADE
);

CREATE TABLE decisions (
    id BIGSERIAL PRIMARY KEY,
    stock_id BIGINT NOT NULL,
    decision VARCHAR(255),
    confidence DOUBLE PRECISION,
    reason VARCHAR(255),
    created_at TIMESTAMP,
    CONSTRAINT fk_decision_stock
        FOREIGN KEY (stock_id)
        REFERENCES stocks(id)
        ON DELETE CASCADE
);

SELECT * FROM stocks;