# validator.py
from typing import Dict, Any, List, Tuple

class DataValidator:
    """
    The first line of defense.
    Validates structural integrity, data types, and basic constraints.
    Does NOT check the database (that comes in Phase 5).
    """
    def __init__(self):
        self.required_fields = ['item', 'client', 'qty']

    def validate_structure(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Checks if the input dictionary adheres to the strict schema.
        
        Args:
            data: The JSON dictionary from the LLM/Parser.
            
        Returns:
            Tuple (is_valid: bool, errors: List[str])
        """
        errors = []
        
        if not data:
            return False, ["Input data is empty or None."]

        # 1. Check Required Fields
        for field in self.required_fields:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")
            elif data[field] is None:
                errors.append(f"Field '{field}' cannot be None.")

        if errors:
            return False, errors

        # 2. Type & Value Validation
        # Validate Quantity
        try:
            qty = data['qty']
            if not isinstance(qty, int):
                errors.append(f"Quantity must be an integer. Got {type(qty).__name__}.")
            elif qty <= 0:
                errors.append(f"Quantity must be positive. Got {qty}.")
        except Exception:
            errors.append("Critical error validating quantity.")

        # Validate Strings
        if not isinstance(data.get('item'), str):
            errors.append("Item name must be a string.")
        
        if not isinstance(data.get('client'), str):
            errors.append("Client name must be a string.")

        # Final Decision
        is_valid = len(errors) == 0
        return is_valid, errors

if __name__ == "__main__":
    validator = DataValidator()

    print("--- Running Validation Tests ---")
    
    # Test 1: Valid Data
    valid_payload = {"item": "Dell XPS", "qty": 5, "client": "TechCorp", "action": "sold"}
    success, errs = validator.validate_structure(valid_payload)
    print(f"Test 1 (Valid): {'PASS' if success else 'FAIL'} -> Errors: {errs}")

    # Test 2: Invalid Data (Negative Qty)
    bad_qty = {"item": "Dell XPS", "qty": -10, "client": "TechCorp"}
    success, errs = validator.validate_structure(bad_qty)
    print(f"Test 2 (Negative Qty): {'PASS' if not success else 'FAIL'} -> Errors: {errs}")

    # Test 3: Missing Field
    missing_field = {"qty": 5, "client": "TechCorp"}
    success, errs = validator.validate_structure(missing_field)
    print(f"Test 3 (Missing Item): {'PASS' if not success else 'FAIL'} -> Errors: {errs}")