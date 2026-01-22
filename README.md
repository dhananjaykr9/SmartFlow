# SmartFlow: AI-Powered Data Quality Pipeline

## 🚀 Executive Summary
SmartFlow is an intelligent data ingestion middleware designed to solve the "Garbage In, Garbage Out" problem. It acts as a gatekeeper between unstructured human input and enterprise databases, ensuring only valid, normalized, and safe data is persisted.

## 🏗️ Architecture
The system follows a strict **ETL (Extract, Transform, Load)** workflow:
1.  **Ingestion (Streamlit):** Captures raw natural language (e.g., "Sold 5 iPhones to Client A").
2.  **Transformation (AI):** Uses LLMs (Gemini) to parse text into structured JSON.
3.  **Validation (Python):** Enforces Structural Integrity, Data Types, and Business Rules (Stock Limits).
4.  **Anomaly Detection (ML):** Uses an **Isolation Forest** model to flag suspicious but valid transactions.
5.  **Storage (SQL Server):** Persists data into a **Star Schema** (Fact/Dimension) for OLAP readiness.

## 🛠️ Tech Stack
* **Backend:** Python 3.10, FastAPI, Pydantic
* **Database:** Microsoft SQL Server (ODBC Driver 18), Star Schema
* **AI/ML:** Google Gemini (NER), Scikit-Learn (Isolation Forest)
* **Frontend:** Streamlit
* **Resilience:** Tenacity (Retry Logic), PyODBC

## ⚡ How to Run
1.  **Setup Database:** Run the SQL scripts in `database/schema.sql` (Phase 1).
2.  **Install Dependencies:** `pip install -r requirements.txt`.
3.  **Start API:** `python main.py`
4.  **Start Frontend:** `streamlit run app.py`

## 🧠 Design Decisions
* **Why Star Schema?** Optimized for read-heavy analytics and easy integration with PowerBI/Tableau.
* **Why Isolation Forest?** Unsupervised learning allows us to detect anomalies without needing a labeled "fraud" dataset.
* **Why Separate API?** Decoupling the Frontend from the Backend ensures the logic can be reused by mobile apps or other services.
