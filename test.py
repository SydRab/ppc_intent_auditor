import os
import pandas as pd
from modules.api_client import get_gemini_client, evaluate_keyword_batch
from modules.exporter import save_clean_campaign_data

def run_single_batch_test():
    print("Initializing Gemini API Client for Single-Batch Test...")
    client = get_gemini_client()
    
    # Locate your CSV file
    csv_filename = "results-20260924-035933 - pest_control_search_terms.csv"
    if not os.path.exists(csv_filename):
        # Fallback check if it's in a subdirectory or root
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if files:
            csv_filename = files[0]
            
    print(f"Loading raw data from {csv_filename}...")
    df = pd.read_csv(csv_filename)
    print(f"Loaded {len(df)} total rows. Slicing Batch 1 (First 100 rows)...")
    
    # Slice only the first batch (100 items)
    batch_df = df.head(100)
    records_batch = batch_df.to_dict(orient="records")
    
    print("Sending Batch 1 to Gemini API...")
    batch_results = evaluate_keyword_batch(client, records_batch)
    
    if not batch_results:
        print("[ERROR] Batch 1 returned empty results or failed.")
        return

    print(f"Successfully received {len(batch_results)} evaluated items from Batch 1.")
    print("Sample Output (First 3 items):")
    for item in batch_results[:3]:
        print(item)
        
    # Test the exporter logic on this batch
    output_file = "test_approved_batch1.csv"
    print(f"Testing exporter output to {output_file}...")
    save_clean_campaign_data(batch_df, batch_results, output_file)
    print("Test completed successfully!")

if __name__ == "__main__":
    run_single_batch_test()
