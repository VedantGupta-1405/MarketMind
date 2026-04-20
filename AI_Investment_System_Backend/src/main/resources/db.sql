




DROP TABLE IF EXISTS portDfolio;
DROP TABLE IF EXISTS stocks;
DROP TABLE IF EXISTS users;
----------------------------------------------------------------
-- Create users table

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
----------------------------------------------------------------
-- Insert user

INSERT INTO users(name, email)
VALUES ('Vedant', 'vedant@gmail.com');
----------------------------------------------------------------
-- Verify

SELECT * FROM users;
----------------------------------------------------------------
-- Create stocks table

CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
----------------------------------------------------------------
-- Insert stocks

INSERT INTO stocks(name, symbol, price) VALUES
('Apple', 'AAPL', 180.50),
('Tesla', 'TSLA', 250.75);
----------------------------------------------------------------
-- Verify

SELECT * FROM stocks;
----------------------------------------------------------------
-- Create portfolio table

CREATE TABLE portfolio (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    quantity INT NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);
----------------------------------------------------------------
-- Check IDs

SELECT * FROM users;
SELECT * FROM stocks;
----------------------------------------------------------------
-- Insert portfolio data

INSERT INTO portfolio(user_id, stock_id, quantity)
VALUES (1, 1, 10);
----------------------------------------------------------------
-- Verify

SELECT * FROM portfolio;
----------------------------------------------------------------
-- Create transactions table

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    type VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);
----------------------------------------------------------------
-- Insert transaction

INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'BUY', 10, 180.50);
----------------------------------------------------------------
-- Verify

SELECT * FROM transactions;
----------------------------------------------------------------
--insert transaction

INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'BUY', 5, 180.50);
----------------------------------------------------------------
-- update portfolio

UPDATE portfolio
SET quantity = quantity + 5
WHERE user_id = 1 AND stock_id = 1;
----------------------------------------------------------------
-- Verify

SELECT * FROM portfolio;
SELECT * FROM transactions;
----------------------------------------------------------------
-- insert transaction

INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 2, 'BUY', 3, 250.75);
----------------------------------------------------------------
-- insert into portfolio (NOT update)

INSERT INTO portfolio(user_id, stock_id, quantity)
VALUES (1, 2, 3);
----------------------------------------------------------------
-- Verify

SELECT * FROM portfolio;
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'SELL', 5, 180.50);

UPDATE portfolio
SET quantity = quantity - 5
WHERE user_id = 1 AND stock_id = 1;

SELECT * FROM portfolio;
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 2, 'SELL', 3, 250.75);

UPDATE portfolio
SET quantity = quantity - 3
WHERE user_id = 1 AND stock_id = 2;

SELECT * FROM portfolio;
----------------------------------------------------------------
DELETE FROM portfolio
WHERE quantity = 0;

SELECT * FROM portfolio;
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'SELL', 100, 180.50);
----------------------------------------------------------------
SELECT quantity FROM portfolio
WHERE user_id = 1 AND stock_id = 1;
----------------------------------------------------------------
SELECT * FROM portfolio
WHERE user_id = 1 AND stock_id = 2;
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 2, 'BUY', 2, 250.75);

INSERT INTO portfolio(user_id, stock_id, quantity)
VALUES (1, 2, 2);
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'BUY', 3, 180.50);

UPDATE portfolio
SET quantity = quantity + 3
WHERE user_id = 1 AND stock_id = 1;
----------------------------------------------------------------
SELECT quantity FROM portfolio
WHERE user_id = 1 AND stock_id = 1;
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'SELL', 2, 180.50);

UPDATE portfolio
SET quantity = quantity - 2
WHERE user_id = 1 AND stock_id = 1;
-----------------------------------------------------------------
DROP TABLE IF EXISTS portfolio;
DROP TABLE IF EXISTS stocks;
DROP TABLE IF EXISTS users;
----------------------------------------------------------------
-- Create users table

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
----------------------------------------------------------------
-- Insert user

INSERT INTO users(name, email)
VALUES ('Vedant', 'vedant@gmail.com');
----------------------------------------------------------------
-- Verify

SELECT * FROM users;
----------------------------------------------------------------
-- Create stocks table

CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
----------------------------------------------------------------
-- Insert stocks

INSERT INTO stocks(name, symbol, price) VALUES
('Apple', 'AAPL', 180.50),
('Tesla', 'TSLA', 250.75);
----------------------------------------------------------------
-- Verify

SELECT * FROM stocks;
----------------------------------------------------------------
-- Create portfolio table

CREATE TABLE portfolio (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    quantity INT NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);
----------------------------------------------------------------
-- Check IDs

SELECT * FROM users;
SELECT * FROM stocks;
----------------------------------------------------------------
-- Insert portfolio data

INSERT INTO portfolio(user_id, stock_id, quantity)
VALUES (1, 1, 10);
----------------------------------------------------------------
-- Verify

SELECT * FROM portfolio;
----------------------------------------------------------------
-- Create transactions table

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    type VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);
----------------------------------------------------------------
-- Insert transaction

INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'BUY', 10, 180.50);
----------------------------------------------------------------
-- Verify

SELECT * FROM transactions;
----------------------------------------------------------------
--insert transaction

INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'BUY', 5, 180.50);
----------------------------------------------------------------
-- update portfolio

UPDATE portfolio
SET quantity = quantity + 5
WHERE user_id = 1 AND stock_id = 1;
----------------------------------------------------------------
-- Verify

SELECT * FROM portfolio;
SELECT * FROM transactions;
----------------------------------------------------------------
-- insert transaction

INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 2, 'BUY', 3, 250.75);
----------------------------------------------------------------
-- insert into portfolio (NOT update)

INSERT INTO portfolio(user_id, stock_id, quantity)
VALUES (1, 2, 3);
----------------------------------------------------------------
-- Verify

SELECT * FROM portfolio;
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'SELL', 5, 180.50);

UPDATE portfolio
SET quantity = quantity - 5
WHERE user_id = 1 AND stock_id = 1;

SELECT * FROM portfolio;
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 2, 'SELL', 3, 250.75);

UPDATE portfolio
SET quantity = quantity - 3
WHERE user_id = 1 AND stock_id = 2;

SELECT * FROM portfolio;
----------------------------------------------------------------
DELETE FROM portfolio
WHERE quantity = 0;

SELECT * FROM portfolio;
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'SELL', 100, 180.50);
----------------------------------------------------------------
SELECT quantity FROM portfolio
WHERE user_id = 1 AND stock_id = 1;
----------------------------------------------------------------
SELECT * FROM portfolio
WHERE user_id = 1 AND stock_id = 2;
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 2, 'BUY', 2, 250.75);

INSERT INTO portfolio(user_id, stock_id, quantity)
VALUES (1, 2, 2);
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'BUY', 3, 180.50);

UPDATE portfolio
SET quantity = quantity + 3
WHERE user_id = 1 AND stock_id = 1;
----------------------------------------------------------------
SELECT quantity FROM portfolio
WHERE user_id = 1 AND stock_id = 1;
----------------------------------------------------------------
INSERT INTO transactions(user_id, stock_id, type, quantity, price)
VALUES (1, 1, 'SELL', 2, 180.50);

UPDATE portfolio
SET quantity = quantity - 2
WHERE user_id = 1 AND stock_id = 1;
-----------------------------------------------------------------
TRUNCATE TABLE portfolio RESTART IDENTITY CASCADE;
TRUNCATE TABLE transactions RESTART IDENTITY CASCADE;
TRUNCATE TABLE stocks RESTART IDENTITY CASCADE;
-----------------------------------------------------------------
SELECT * FROM stocks;
-----------------------------------------------------------------
SELECT * FROM stocks;
SELECT * FROM portfolio;
SELECT * FROM transactions;
-----------------------------------------------------------------
ALTER TABLE stock RENAME TO stocks;
-----------------------------------------------------------------
DROP TABLE portfolio;
DROP TABLE transactions;
-----------------------------------------------------------------
CREATE TABLE portfolio (
    id SERIAL PRIMARY KEY,
    stock_id INT NOT NULL,
    quantity INT NOT NULL
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    stock_id INT NOT NULL,
    type VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-----------------------------------------------------------------
SELECT * FROM portfolio;
SELECT * FROM transactions;
-----------------------------------------------------------------
ALTER TABLE portfolio 
ADD COLUMN average_price NUMERIC(10,2) NOT NULL DEFAULT 0;
-----------------------------------------------------------------
SELECT * FROM portfolio;
-----------------------------------------------------------------
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    stock_id INT NOT NULL,
    date DATE NOT NULL,

    open_price NUMERIC(10,2),
    close_price NUMERIC(10,2),
    high NUMERIC(10,2),
    low NUMERIC(10,2),

    volume BIGINT,

    CONSTRAINT fk_stock
        FOREIGN KEY(stock_id)
        REFERENCES stocks(id)
        ON DELETE CASCADE
);
-----------------------------------------------------------------
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    stock_id INT NOT NULL,

    title TEXT NOT NULL,
    content TEXT,
    published_at TIMESTAMP,

    CONSTRAINT fk_news_stock
        FOREIGN KEY(stock_id)
        REFERENCES stocks(id)
        ON DELETE CASCADE
);
-----------------------------------------------------------------
CREATE TABLE sentiment (
    id SERIAL PRIMARY KEY,
    news_id INT NOT NULL,

    score NUMERIC(3,2), -- range: -1 to 1

    CONSTRAINT fk_news
        FOREIGN KEY(news_id)
        REFERENCES news(id)
        ON DELETE CASCADE
);
-----------------------------------------------------------------
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    stock_id INT NOT NULL,

    prediction VARCHAR(10), -- UP / DOWN
    probability NUMERIC(5,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_pred_stock
        FOREIGN KEY(stock_id)
        REFERENCES stocks(id)
        ON DELETE CASCADE
);
-----------------------------------------------------------------
CREATE TABLE decisions (
    id SERIAL PRIMARY KEY,
    stock_id INT NOT NULL,

    decision VARCHAR(10), -- BUY / SELL / HOLD
    confidence NUMERIC(5,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_dec_stock
        FOREIGN KEY(stock_id)
        REFERENCES stocks(id)
        ON DELETE CASCADE
);
-----------------------------------------------------------------