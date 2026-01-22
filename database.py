# database.py
import os
import pyodbc
from dotenv import load_dotenv
from typing import List
import pandas as pd

# Load environment variables
load_dotenv()


class DatabaseHandler:
    """
    Handles connections and raw queries to Microsoft SQL Server.
    """
    def __init__(self):
        self.server = os.getenv("DB_SERVER", "localhost")
        self.database = os.getenv("DB_NAME", "SmartFlowDB")
        self.driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")

        # TrustServerCertificate=yes is required for Driver 18 on localhost
        self.connection_string = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )

    def get_connection(self) -> pyodbc.Connection:
        """Establishes and returns a database connection."""
        try:
            return pyodbc.connect(self.connection_string)
        except pyodbc.Error as e:
            print(f"Error connecting to SQL Server: {e}")
            raise

    def fetch_valid_entities(self, table_name: str, column_name: str) -> List[str]:
        """
        Fetches a list of valid canonical names from a dimension table.
        """
        query = f"SELECT {column_name} FROM {table_name}"

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            print(f"Error fetching entities from {table_name}: {e}")
            return []
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def insert_transaction(self, data: dict) -> bool:
        """
        Commits the validated transaction to the Fact Table.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO fact_sales_transactions
        (client_id, item_id, quantity, total_price, anomaly_score, is_flagged, data_source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        try:
            cursor.execute(query, (
                data["client_id"],
                data["item_id"],
                data["quantity"],
                data["total_price"],
                data["anomaly_score"],
                1 if data["is_flagged"] else 0,
                "API_V1"
            ))
            conn.commit()
            print("[DB] Transaction saved successfully.")
            return True
        except Exception as e:
            print(f"[DB] Insert Failed: {e}")
            conn.rollback()
            return False
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def fetch_recent_transactions(self):
        """
        Fetches the last 10 transactions for the dashboard.
        """
        conn = self.get_connection()
        query = """
        SELECT TOP 10
            t.transaction_id,
            i.item_name,
            c.client_name,
            t.quantity,
            t.total_price,
            t.anomaly_score,
            t.transaction_date
        FROM fact_sales_transactions t
        JOIN dim_items i ON t.item_id = i.item_id
        JOIN dim_clients c ON t.client_id = c.client_id
        ORDER BY t.transaction_date DESC
        """

        try:
            return pd.read_sql(query, conn)
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def check_idempotency(self, request_hash: str) -> bool:
        """
        Returns True if the hash ALREADY exists (Duplicate).
        Returns False if it is new (Safe to proceed).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            query = """
            SELECT COUNT(*)
            FROM transaction_idempotency_log
            WHERE request_hash = ?
            """
            cursor.execute(query, (request_hash,))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"[DB] Idempotency Check Error: {e}")
            return False
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def log_idempotency(self, request_hash: str):
        """
        Saves the hash to prevent future duplicates.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            query = """
            INSERT INTO transaction_idempotency_log (request_hash)
            VALUES (?)
            """
            cursor.execute(query, (request_hash,))
            conn.commit()
        except Exception as e:
            print(f"[DB] Failed to log hash: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    # Quick Test
    db = DatabaseHandler()
    items = db.fetch_valid_entities("dim_items", "item_name")
    print(f"Connected! Valid Items in DB: {items}")

    recent = db.fetch_recent_transactions()
    print(recent)
