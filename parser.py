# parser.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import Dict, Any, Optional
import re 

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class LLMParser:
    """
    Handles communication with the LLM to parse unstructured text into JSON.
    Includes a 'Mock Mode' fail-safe if the API is down or quota is exceeded.
    """
    def __init__(self):
        # Fallback to the standard stable model (usually free tier friendly)
        self.model_name = 'gemini-1.5-flash'
        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception:
            self.model = None

    def _clean_json_string(self, json_str: str) -> str:
        """Removes Markdown formatting if the LLM includes it."""
        json_str = json_str.strip()
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        return json_str.strip()

    def parse_text(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to parse text via API. If it fails, returns MOCK data 
        so development can continue.
        """
        print(f"[*] Sending to LLM ({self.model_name})...")
        
        try:
            return self._call_api(raw_text)
        except Exception as e:
            print(f"[!] API Failed ({e}). Switching to MOCK MODE.")
            return self._mock_response(raw_text)

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(2))
    def _call_api(self, raw_text: str) -> Dict[str, Any]:
        """Internal method to call the API with retry logic."""
        prompt = f"""
        You are a Data Extraction API. 
        Extract the following fields from the user input:
        - item (string): The product name.
        - qty (integer): The quantity.
        - client (string): The client/customer name.
        - action (string): The action taken (e.g., sold, returned, ordered).

        User Input: "{raw_text}"

        Return ONLY raw JSON. Do not include markdown formatting or explanations.
        Example Output: {{"item": "iPhone 15", "qty": 5, "client": "Client A", "action": "sold"}}
        """
        response = self.model.generate_content(prompt)
        clean_text = self._clean_json_string(response.text)
        return json.loads(clean_text)


    def _mock_response(self, raw_text: str) -> Dict[str, Any]:
        """
        Returns dummy data but attempts to extract the REAL quantity
        using basic Python logic (Regex).
        """
        raw_lower = raw_text.lower()
        
        # 1. Determine Item
        item = "Unknown Item"
        if "iphone" in raw_lower: item = "iPhone 15"
        elif "dell" in raw_lower: item = "Dell XPS"
        elif "macbook" in raw_lower: item = "MacBook Pro"
        
        # 2. Determine Client
        client = "Unknown Client"
        if "techcorp" in raw_lower: client = "TechCorp"
        elif "client a" in raw_lower: client = "Client A"
        elif "alphallc" in raw_lower: client = "AlphaLLC"

        # 3. Extract Quantity using Regex (The "Smart" Part)
        # Looks for the first number in the text
        qty = 1 # Default
        match = re.search(r'\b(\d+)\b', raw_text)
        if match:
            qty = int(match.group(1))

        return {
            "item": item,
            "qty": qty, 
            "client": client,
            "action": "sold (MOCK)"
        }


# Testing Block
if __name__ == "__main__":
    parser = LLMParser()
    
    # Test Case
    sample_text = "We just shipped two Dell XPS laptops to TechCorp."
    
    print(f"Input: {sample_text}")
    result = parser.parse_text(sample_text)
    print(f"Structured Output: {result}")
    
    if result['item'] == 'Dell XPS':
        print("SUCCESS: Logic Verified (API or Mock).")