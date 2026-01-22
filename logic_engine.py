# logic_engine.py
from typing import Tuple, Optional
from database import DatabaseHandler

class BusinessLogicEngine:
    """
    Enforces dynamic business rules by querying the current state 
    of the database (e.g., Stock Levels, Credit Limits).
    """
    def __init__(self):
        self.db = DatabaseHandler()

    def check_stock_availability(self, item_id: int, requested_qty: int) -> Tuple[bool, str, float]:
        """
        Verifies if we have enough stock to fulfill the order.
        
        Args:
            item_id: The SQL Primary Key of the item.
            requested_qty: How many the user wants.
            
        Returns:
            Tuple (is_allowed, message, unit_price)
            - is_allowed: True/False
            - message: Error text or "OK"
            - unit_price: The current price (needed for the Fact table later)
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Fetch current stock and price for the specific item
            query = "SELECT current_stock, unit_price FROM dim_items WHERE item_id = ?"
            cursor.execute(query, (item_id,))
            row = cursor.fetchone()
            
            if not row:
                return False, f"Item ID {item_id} not found in DB.", 0.0

            current_stock = int(row[0])
            unit_price = float(row[1])

            # THE RULE: Can't sell what you don't have
            if requested_qty > current_stock:
                msg = f"Insufficient Stock. Requested: {requested_qty}, Available: {current_stock}"
                return False, msg, unit_price
            
            return True, "Stock Available", unit_price

        except Exception as e:
            return False, f"Database Error: {e}", 0.0
        finally:
            conn.close()

# Testing Block
if __name__ == "__main__":
    logic = BusinessLogicEngine()
    
    # We know from Phase 1 that 'iPhone 15' (Item ID 1) has 50 in stock.
    print("\n--- Business Logic Tests ---")
    
    # Test 1: Valid Order (Buy 5)
    print("Test 1: Ordering 5 iPhones (Should PASS)")
    allowed, msg, price = logic.check_stock_availability(item_id=1, requested_qty=5)
    print(f"   -> Result: {allowed} | Message: {msg} | Price: ${price}")

    # Test 2: Invalid Order (Buy 1000)
    print("\nTest 2: Ordering 1000 iPhones (Should FAIL)")
    allowed, msg, price = logic.check_stock_availability(item_id=1, requested_qty=1000)
    print(f"   -> Result: {allowed} | Message: {msg}")

    # Check Logic
    if allowed is False and "Insufficient" in msg:
        print("   SUCCESS: Logic Verified.")
    else:
        print("   FAILURE: Logic allowed an impossible order!")