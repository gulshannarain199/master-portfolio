# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 3 - Python Programming Fundamentals
# TOPIC:  Objects & Classes (Object-Oriented Programming / OOP)
# ==============================================================================

# --- 1. Class Definition & Constructor (__init__) ---
class DataPipeline:
    """Class representing an automated ETL data ingestion pipeline."""
    
    # Class Attribute (Shared across all instances)
    framework = "PySpark / Pandas"

    def __init__(self, pipeline_name, target_table):
        """Constructor initializing instance attributes."""
        self.pipeline_name = pipeline_name
        self.target_table = target_table
        self.records_processed = 0
        self.status = "IDLE"

    # --- 2. Instance Methods ---
    def start_pipeline(self):
        """Updates pipeline state to ACTIVE."""
        self.status = "ACTIVE"
        print(f"[{self.pipeline_name}] Pipeline initialized and set to {self.status}.")

    def ingest_records(self, count):
        """Simulates ingesting a batch of records."""
        if self.status != "ACTIVE":
            print(f"[{self.pipeline_name}] Cannot ingest. Pipeline is currently {self.status}.")
            return
        
        self.records_processed += count
        print(f"[{self.pipeline_name}] Ingested {count} records into target table '{self.target_table}'.")

    def get_summary(self):
        """Returns structured metadata summary of the pipeline instance."""
        return {
            "Pipeline Name": self.pipeline_name,
            "Target Table": self.target_table,
            "Total Ingested": self.records_processed,
            "Current Status": self.status,
            "Framework": self.framework
        }


# --- 3. Instantiating Objects & Executing Methods ---
print("--- 1. CREATING INSTANCES ---")
# Instantiate two distinct pipeline objects
sales_pipeline = DataPipeline("Sales_ETL", "fact_daily_sales")
user_pipeline = DataPipeline("Users_ETL", "dim_active_users")

print("--- 2. RUNNING PIPELINE OPERATIONS ---")
sales_pipeline.start_pipeline()
sales_pipeline.ingest_records(5000)
sales_pipeline.ingest_records(2500)

print("\n--- 3. INSPECTING OBJECT METADATA ---")
print(f"Sales Summary: {sales_pipeline.get_summary()}")
print(f"User Summary: {user_pipeline.get_summary()}")


# --- 4. Modifying Attributes & dir() Inspection ---
print("\n--- 4. OBJECT ATTRIBUTE INSPECTION ---")
# Modifying attribute directly
sales_pipeline.status = "COMPLETED"
print(f"Updated Sales Pipeline Status: {sales_pipeline.status}")

# dir() retrieves all attributes and methods associated with the object
print(f"Object Method Count: {len(dir(sales_pipeline))}")