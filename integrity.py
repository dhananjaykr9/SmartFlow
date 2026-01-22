# integrity.py
from typing import Tuple, Optional, Dict, Any
from database import DatabaseHandler
from normalizer import DataNormalizer

class IntegrityChecker:
    """
    Ensures that items and clients mentioned in the transaction 
    actually exist in the SQL Dimension tables.
    """
    def __init__(self):
        self.db = DatabaseHandler()
        self.normalizer = DataNormalizer()

    def get_valid_ids(self, raw_item: str, raw_client: str) -> Tuple[Optional[int], Optional[int], Dict[str, str]]:
        """
        Validates existence and returns SQL IDs.
        
        Args:
            raw_item: User input for item (e.g. "iphone-15")
            raw_client: User input for client (e.g. "client a")
            
        Returns:
            Tuple: (item_id, client_id, logs)
            - item_id: Int ID from DB or None
            - client_id: Int ID from DB or None
            - logs: Dictionary of normalization steps for debugging
        """
        logs = {}
        
        # 1. Normalize Names (Text -> Canonical)
        canon_item = self.normalizer.normalize(raw_item, "item")
        canon_client = self.normalizer.normalize(raw_client, "client")
        
        logs['normalized_item'] = canon_item
        logs['normalized_client'] = canon_client

        # If normalization failed (no match found), we can't get an ID
        if not canon_item or not canon_client:
            return None, None, logs

        # 2. Fetch IDs from SQL (Canonical -> ID)
        item_id = self._fetch_id("dim_items", "item_id", "item_name", canon_item)
        client_id = self._fetch_id("dim_clients", "client_id", "client_name", canon_client)
        
        return item_id, client_id, logs

    def _fetch_id(self, table: str, id_col: str, name_col: str, value: str) -> Optional[int]:
        """Helper query to get a single ID."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = f"SELECT {id_col} FROM {table} WHERE {name_col} = ?"
            cursor.execute(query, (value,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return int(row[0])
            return None
        except Exception as e:
            print(f"DB Error fetching ID: {e}")
            return None

# Testing Block
if __name__ == "__main__":
    checker = IntegrityChecker()
    
    print("\n--- Referential Integrity Tests ---")
    
    # Test 1: Perfect Scenario
    print("Test 1: Check 'iphone-15' (Should exist)")
    i_id, c_id, logs = checker.get_valid_ids("iphone-15", "client a")
    print(f"   -> Item ID: {i_id} | Client ID: {c_id} | Logs: {logs}")
    
    if i_id and c_id: 
        print("   RESULT: PASS")
    else: 
        print("   RESULT: FAIL")

    # Test 2: Ghost Item
    print("\nTest 2: Check 'Samsung Galaxy' (Should NOT exist)")
    i_id, c_id, logs = checker.get_valid_ids("Samsung Galaxy", "client a")
    print(f"   -> Item ID: {i_id} | Client ID: {c_id} | Logs: {logs}")
    
    if i_id is None: 
        print("   RESULT: PASS (Correctly rejected)")
    else: 
        print("   RESULT: FAIL (False positive)")