# ml_engine.py
import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest

MODEL_PATH = "isolation_forest.pkl"

class AnomalyDetector:
    """
    Uses Unsupervised Machine Learning to detect suspicious transactions.
    Algorithm: Isolation Forest.
    """
    def __init__(self):
        self.model = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        """Loads existing model or trains a new one if missing."""
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            print("[ML] Model not found. Training new model on synthetic data...")
            self.train_model()

    def train_model(self):
        """
        Generates synthetic 'normal' sales data to teach the model 
        what a standard transaction looks like.
        """
        # 1. Generate 1000 'Normal' Transactions
        # Most people buy 1-5 items. Price varies.
        rng = np.random.RandomState(42)
        
        # Feature 1: Quantity (Normal: 1 to 10)
        X_qty = rng.randint(1, 10, size=(1000, 1))
        
        # Feature 2: Unit Price (Normal: $100 to $2000)
        X_price = rng.randint(100, 2000, size=(1000, 1))
        
        # Combine into a feature set
        X_train = np.hstack((X_qty, X_price))

        # 2. Train Isolation Forest
        # contamination=0.05 means we expect ~5% of data to be anomalies in the wild
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.model.fit(X_train)
        
        # 3. Save to disk
        joblib.dump(self.model, MODEL_PATH)
        print("[ML] Model trained and saved to 'isolation_forest.pkl'.")

    def check_anomaly(self, quantity: int, unit_price: float) -> float:
        """
        Scans a transaction and returns an Anomaly Score.
        
        Returns:
            Float value.
            < 0 : Anomaly (Suspicious)
            > 0 : Normal
        """
        if not self.model:
            return 1.0 # Default to normal if model fails

        # Reshape input to match training shape [qty, price]
        features = np.array([[quantity, unit_price]])
        
        # decision_function returns the raw score. 
        # Negative scores are anomalies. Positive are normal.
        score = self.model.decision_function(features)[0]
        return float(score)

# Testing Block
if __name__ == "__main__":
    detector = AnomalyDetector()
    
    print("\n--- ML Anomaly Detection Tests ---")
    
    # Test 1: Normal Transaction (Qty: 2, Price: $1000) -> Should be POSITIVE score
    score_normal = detector.check_anomaly(2, 1000)
    print(f"Test 1 (Normal): Buy 2 @ $1000 -> Score: {score_normal:.4f} [{'OK' if score_normal > 0 else 'FLAG'}]")

    # Test 2: Anomalous Transaction (Qty: 50, Price: $1000) -> Should be NEGATIVE score
    # Why? Because our training data only saw quantities of 1-10.
    score_anomaly = detector.check_anomaly(50, 1000)
    print(f"Test 2 (Suspicious): Buy 50 @ $1000 -> Score: {score_anomaly:.4f} [{'OK' if score_anomaly > 0 else 'FLAG'}]")