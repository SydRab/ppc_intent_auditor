import os
import pandas as pd
from modules.api_client import get_gemini_client
from modules.processor import process_keywords_in_chunks
from modules.exporter import save_clean_campaign_data

def main():
    input_file = "results-20260924-035933 - pest_control_search_terms.csv"
    output_file = "approved_campaign_keywords.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    print("Initializing Gemini API Client...")
    client = get_gemini_client()
    
    print(f"Loading raw data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # Prepare records containing keyword and zip code for contextual evaluation
    records = []
    for _, row in df.iterrows():
        records.append({
            "keyword": str(row['suggested_keyword']),
            "original_zip": str(row['original_zip'])
        })
        
    print(f"Loaded {len(records)} total keyword-zip rows for auditing.")
    
    # Run the modular processing pipeline in batches
    results = process_keywords_in_chunks(client, records, chunk_size=100)
    
    # Export final structured output with all original metrics
    save_clean_campaign_data(df, results, output_file)

if __name__ == "__main__":
    main()
