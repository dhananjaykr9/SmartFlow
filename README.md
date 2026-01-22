# SmartFlow – AI-Powered Data Quality Pipeline

## Overview

**SmartFlow** is an AI-driven data ingestion and validation middleware designed to eliminate the *Garbage In, Garbage Out* problem at its source.

Instead of allowing unstructured human input to directly reach enterprise databases, SmartFlow acts as a **deterministic quality gate**, ensuring that only validated, normalized, and policy-compliant data is persisted.

This system is built for real-world analytics, not demos.

---

## Problem Statement

In production systems, data quality issues originate upstream:

* Free-text inputs from users or field teams
* Inconsistent formats and ambiguous language
* Silent logical errors that bypass schema checks
* No early detection of anomalous transactions

Traditional pipelines validate *after* ingestion. SmartFlow validates *before* persistence.

---

## System Architecture

SmartFlow follows a strict **ETL (Extract, Transform, Load)** pipeline orchestrated by a FastAPI backend.

**Flow:**

1. **Capture (Frontend)**
   Users enter raw natural language input via a Streamlit interface
   Example: `Sold 5 iPhones to Client A`

2. **Ingestion (API Layer)**
   A FastAPI service receives and standardizes the request payload

3. **Transformation (AI Parsing)**
   Google Gemini converts unstructured text into structured JSON entities

4. **Validation (Deterministic Logic)**
   Pydantic enforces:

   * Schema integrity
   * Data types
   * Business rules

5. **Anomaly Detection (ML Layer)**
   An Isolation Forest model flags suspicious or outlier transactions prior to storage

6. **Persistence (Analytics-Ready Storage)**
   Only validated records are written to a SQL Server **Star Schema**, optimized for OLAP and BI tools

---

## Key Design Principles

* AI is used for **parsing**, not decision-making
* Validation remains **deterministic and auditable**
* Failures are explicit, logged, and traceable
* Analytics readiness is a first-class concern

---

## Technology Stack

**Backend**

* Python 3.10
* FastAPI
* Pydantic

**AI / ML**

* Google Gemini (entity extraction and parsing)
* Scikit-learn (Isolation Forest for anomaly detection)

**Frontend**

* Streamlit

**Database**

* Microsoft SQL Server
* Star Schema design (fact and dimension tables)

**Reliability**

* Tenacity for retry and resilience
* PyODBC with ODBC Driver 18

---

## Configuration

Create a `.env` file in the project root:

```ini
DB_SERVER=your_server_name
DB_NAME=SmartFlowDB
DB_USER=your_user
DB_PASSWORD=your_password
GOOGLE_API_KEY=your_gemini_api_key
```

---

## How to Run

### 1. Initialize the Database

Run the SQL scripts located in:

```
database/schema.sql
```

This creates the Star Schema tables.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Backend API

```bash
python main.py
```

FastAPI will run on:

```
http://localhost:8000
```

### 4. Start the Frontend

```bash
streamlit run app.py
```

Streamlit UI will be available at:

```
http://localhost:8501
```

---

## Design Decisions

**Why a Star Schema?**
Optimized for read-heavy analytics and seamless integration with BI tools such as Power BI and Tableau.

**Why Isolation Forest?**
Unsupervised anomaly detection allows identification of abnormal transactions without requiring labeled fraud data.

**Why Separate API and Frontend?**
Decoupling Streamlit from FastAPI ensures the core validation engine can be reused by mobile apps, batch jobs, or third-party integrations.

---

## What This Demonstrates

* Production-oriented AI usage
* Data engineering best practices
* Deterministic validation around LLMs
* Analytics-ready system design

SmartFlow is not about chatting with data.
It is about **trusting data before it enters the system**.

---
