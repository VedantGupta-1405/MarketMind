# MarketMind — AI Investment System (Backend + ML)

##  Overview

MarketMind is a full-stack AI-based investment decision system.

This repository contains:

* **Spring Boot Backend**
* **FastAPI ML Service**
* **PostgreSQL Database**
* (Optional) Static Frontend

The system:

* Fetches stock data
* Runs ML prediction (UP/DOWN)
* Combines with sentiment
* Generates **BUY / SELL / HOLD decisions**

---

##  Tech Stack

* Backend: Spring Boot (Java)
* Database: PostgreSQL
* ML Service: FastAPI (Python)
* ML Model: LSTM (Keras)
* API Communication: REST

---

##  Project Structure

```id="5cv7rp"
MarketMind/
│
├── AI_Investment_System_Backend/   → Spring Boot backend
├── ml-service/                    → FastAPI ML service
├── frontend/                      → Static UI (HTML/CSS/JS)
```

---

##  Prerequisites

Make sure you have installed:

* Java 17+
* Maven
* Python 3.9+
* PostgreSQL
* Git

---

##  SETUP INSTRUCTIONS

---

### 1. Clone Repository

```bash id="i14d5u"
git clone <your-repo-url>
cd MarketMind
```

---

### 2. DATABASE SETUP

#### Create DB in PostgreSQL:

```sql id="9r9d3p"
CREATE DATABASE investment_system;
```

#### Update credentials in:

```id="kth0ye"
AI_Investment_System_Backend/src/main/resources/application.properties
```

```properties id="7psr0h"
spring.datasource.url=jdbc:postgresql://localhost:5432/investment_system
spring.datasource.username=postgres
spring.datasource.password=your_password

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
```

---

### 3. RUN BACKEND (Spring Boot)

```bash id="8r7d4g"
cd AI_Investment_System_Backend
mvn spring-boot:run
```

 Runs on:

```id="pp1s7f"
http://localhost:8080
```

---

### 4. RUN ML SERVICE (FastAPI)

```bash id="u6k0le"
cd ml-service
```

#### Create virtual environment:

```bash id="8z0hcz"
python -m venv venv
```

#### Activate:

**Windows:**

```bash id="m1x1qz"
venv\Scripts\activate
```

**Mac/Linux:**

```bash id="4f0v1d"
source venv/bin/activate
```

#### Install dependencies:

```bash id="c4a2wq"
pip install -r requirements.txt
```

#### Run ML server:

```bash id="8z0slr"
uvicorn main:app --reload
```

 Runs on:

```id="6r0xnm"
http://127.0.0.1:8000
```

---

### 5. RUN FRONTEND (Optional)

```bash id="c0g2rf"
cd frontend
```

Open `index.html` using Live Server or browser:

```id="r4o9pb"
http://127.0.0.1:5500/frontend/index.html
```

---

##  HOW SYSTEM WORKS

1. User clicks **Analyze**
2. Backend calls ML service
3. ML returns:

   * Prediction (UP/DOWN)
   * Probability
4. Backend:

   * Saves prediction
   * Fetches sentiment
   * Generates decision
5. UI displays:

   * Prediction
   * Decision
   * Charts

---

##  API ENDPOINTS

### Prediction

```http id="1md0i5"
POST /predictions/{stockId}
```

---

### Price History

```http id="3cr6kx"
GET /price-history/{stockId}
```

---

### Transactions (if implemented)

```http id="j5gl7p"
POST /transactions
GET /portfolio
```

---

##  IMPORTANT NOTES

* ML service **must be running** before prediction
* Backend depends on ML service
* DB must be connected properly
* If ML fails → fallback returns UNKNOWN

---

##  FUTURE IMPROVEMENTS

* Real sentiment API integration
* Better ML model (training pipeline)
* Auth system
* Docker deployment
* Real-time data streaming

---

##  KEY FEATURE

> This system does NOT just predict — it **generates actionable decisions**

---
