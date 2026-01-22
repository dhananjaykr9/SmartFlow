# router.py
import hashlib
import json
from typing import Dict, Any

# Import our worker modules
from parser import LLMParser
from validator import DataValidator
from integrity import IntegrityChecker
from logic_engine import BusinessLogicEngine
from ml_engine import AnomalyDetector
from database import DatabaseHandler


class TransactionRouter:
    def __init__(self):
        print("[Router] Initializing modules...")
        self.parser = LLMParser()
        self.validator = DataValidator()
        self.integrity = IntegrityChecker()
        self.logic = BusinessLogicEngine()
        self.ml = AnomalyDetector()
        self.db = DatabaseHandler()

    def process_request(self, raw_text: str) -> Dict[str, Any]:
        response = {
            "status": "REJECTED",
            "error": None,
            "data": None,
            "logs": {}
        }

        # --- [NEW] STEP 0: IDEMPOTENCY CHECK ---
        request_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

        if self.db.check_idempotency(request_hash):
            response["error"] = "Duplicate Transaction Detected (Idempotency Guard)."
            return response

        # --- EXISTING PIPELINE STARTS HERE ---

        # 1. Parse
        parsed_data = self.parser.parse_text(raw_text)
        if not parsed_data:
            response["error"] = "LLM failed to parse input."
            return response
        response["logs"]["parsed_json"] = parsed_data

        # 2. Structure
        is_valid_struct, struct_errors = self.validator.validate_structure(parsed_data)
        if not is_valid_struct:
            response["error"] = f"Structural Error: {struct_errors}"
            return response

        # 3. Integrity
        item_name = parsed_data["item"]
        client_name = parsed_data["client"]
        item_id, client_id, norm_logs = self.integrity.get_valid_ids(item_name, client_name)
        response["logs"]["normalization"] = norm_logs

        if not item_id or not client_id:
            response["error"] = f"Unknown Entity. Item_ID: {item_id}, Client_ID: {client_id}"
            return response

        # 4. Business Logic
        qty = parsed_data["qty"]
        is_allowed, logic_msg, unit_price = self.logic.check_stock_availability(item_id, qty)
        if not is_allowed:
            response["error"] = f"Business Rule Violation: {logic_msg}"
            return response

        # 5. ML Anomaly
        anomaly_score = self.ml.check_anomaly(qty, unit_price)
        is_flagged = anomaly_score < 0
        response["logs"]["ml_score"] = anomaly_score

        # 6. Persistence (Save to DB)
        final_payload = {
            "item_id": item_id,
            "client_id": client_id,
            "quantity": qty,
            "total_price": qty * unit_price,
            "anomaly_score": anomaly_score,
            "is_flagged": is_flagged
        }

        save_success = self.db.insert_transaction(final_payload)

        if save_success:
            # --- [NEW] LOCK THE HASH ---
            self.db.log_idempotency(request_hash)

            response["status"] = "SUCCESS"
            response["data"] = final_payload
        else:
            response["error"] = "Database Commit Failed."

        return response


if __name__ == "__main__":
    router = TransactionRouter()
    print("\n--- Full Pipeline Test ---")

    res = router.process_request("I sold 2 iPhone 15s to Client A")
    print(f"Status: {res['status']}")
    if res["status"] == "SUCCESS":
        print("Check SSMS! A new row should be in 'fact_sales_transactions'.")
