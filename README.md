# SmartFlow: AI-Powered Data Quality Pipeline

## 🚀 Executive Summary
SmartFlow is an intelligent data ingestion middleware designed to solve the "Garbage In, Garbage Out" problem. It acts as a gatekeeper between unstructured human input and enterprise databases, ensuring only valid, normalized, and safe data is persisted.

## 🏗️ Architecture
The system follows a strict **ETL (Extract, Transform, Load)** workflow orchestrated by a **FastAPI** backend:

1. **Capture (Frontend):** User inputs raw natural language (e.g., "Sold 5 iPhones to Client A") via **Streamlit**.
2. **Ingestion (API):** The **FastAPI** endpoint receives the payload.
3. **Transformation (AI):** **Google Gemini** parses the unstructured text into structured JSON entities.
4. **Validation (Logic):** **Pydantic** enforces schema integrity, data types, and business rules.
5. **Anomaly Detection (ML):** An **Isolation Forest** model flags suspicious transactions (outliers) before storage.
6. **Storage (DB):** Validated data is persisted into a **SQL Server Star Schema** for OLAP readiness.

## 🛠️ Tech Stack
* **Backend:** Python 3.10, FastAPI, Pydantic
* **Database:** Microsoft SQL Server (ODBC Driver 18), Star Schema
* **AI/ML:** Google Gemini (NER), Scikit-Learn (Isolation Forest)
* **Frontend:** Streamlit
* **Resilience:** Tenacity (Retry Logic), PyODBC

## ⚙️ Configuration
Before running, create a `.env` file in the root directory:
```ini
DB_SERVER=your_server_name
DB_NAME=SmartFlowDB
DB_USER=your_user
DB_PASSWORD=your_password
GOOGLE_API_KEY=your_gemini_api_key
⚡ How to Run
Setup Database: Run the SQL scripts in database/schema.sql to initialize the Star Schema tables.

Install Dependencies:

Bash

pip install -r requirements.txt
Start Backend API:

Bash

# Starts the FastAPI server on localhost:8000
python main.py
Start Frontend Dashboard:

Bash

# Starts the Streamlit UI on localhost:8501
streamlit run app.py
🧠 Design Decisions
Why Star Schema? Optimized for read-heavy analytics and allows for seamless integration with BI tools like PowerBI or Tableau.

Why Isolation Forest? Using unsupervised learning allows the system to detect anomalies (e.g., unusual order quantities) without needing a pre-labeled "fraud" dataset.

Why Separate API? Decoupling the Frontend (Streamlit) from the Backend (FastAPI) ensures the core validation logic can be reused by mobile apps or 3rd party integrations in the future.
