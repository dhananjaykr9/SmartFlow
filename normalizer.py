# normalizer.py
import difflib
from typing import List, Optional
from database import DatabaseHandler

class DataNormalizer:
    """
    Responsible for mapping messy user input to canonical database entities.
    """
    def __init__(self):
        self.db = DatabaseHandler()
        # Cache valid entities in memory to reduce SQL hits
        self.valid_items = self.db.fetch_valid_entities("dim_items", "item_name")
        self.valid_clients = self.db.fetch_valid_entities("dim_clients", "client_name")

    def normalize(self, user_input: str, category: str) -> Optional[str]:
        """
        Attempts to find the closest valid match for the user input.
        
        Args:
            user_input: The raw string (e.g., "iphone-15")
            category: Either 'item' or 'client'
            
        Returns:
            The canonical string from DB (e.g., "iPhone 15") or None if no match found.
        """
        if not user_input:
            return None

        # Select the correct reference list
        if category == 'item':
            reference_list = self.valid_items
        elif category == 'client':
            reference_list = self.valid_clients
        else:
            raise ValueError("Category must be 'item' or 'client'")

        # 1. Exact Match Check (Case Insensitive)
        for valid_entity in reference_list:
            if user_input.lower().strip() == valid_entity.lower():
                return valid_entity

        # 2. Fuzzy Match (Cutoff=0.6 means 60% similarity required)
        matches = difflib.get_close_matches(user_input, reference_list, n=1, cutoff=0.5)
        
        if matches:
            return matches[0] # Return the best match
        
        return None # No close match found

# Testing block
if __name__ == "__main__":
    norm = DataNormalizer()
    
    test_cases = [
        ("iphone-15", "item"),
        ("dell xps", "item"),
        ("client a", "client"),
        ("tech corp", "client"),
        ("unknown product", "item")
    ]
    
    print("\n--- Normalization Tests ---")
    for raw, cat in test_cases:
        result = norm.normalize(raw, cat)
        print(f"Input: '{raw}' -> Normalized: '{result}'")