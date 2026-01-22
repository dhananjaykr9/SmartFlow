# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from router import TransactionRouter
import uvicorn

# Initialize App and Logic
app = FastAPI(title="SmartFlow API", version="1.0")
router = TransactionRouter()

# Define the Input Schema (What the API expects)
class TransactionRequest(BaseModel):
    text: str

# Define the Routes
@app.get("/")
def health_check():
    """Simple check to see if API is running."""
    return {"status": "online", "system": "SmartFlow v1.5"}

@app.post("/process/")
def process_transaction(request: TransactionRequest):
    """
    Main Endpoint.
    Receives raw text -> Runs Pipeline -> Returns result.
    """
    raw_text = request.text

    if not raw_text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    # Call our Orchestrator
    result = router.process_request(raw_text)

    # Map internal status to HTTP Codes
    if result["status"] == "SUCCESS":
        return result
    else:
        # Return 200 so frontend can handle errors gracefully
        return result

# -------- NEW ROUTE ADDED BELOW --------

@app.get("/transactions/")
def get_transactions():
    """Returns recent transactions for the dashboard."""
    from database import DatabaseHandler

    db = DatabaseHandler()
    df = db.fetch_recent_transactions()

    if df is not None:
        return df.to_dict(orient="records")
    return []

# --------------------------------------

if __name__ == "__main__":
    # Run the server
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
