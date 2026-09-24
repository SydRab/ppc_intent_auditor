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
    
    print(f"Loading raw keywords from {input_file}...")
    df = pd.read_csv(input_file)
    
    keyword_col = 'suggested_keyword' if 'suggested_keyword' in df.columns else df.columns[0]
    all_keywords = df[keyword_col].dropna().tolist()
    print(f"Loaded {len(all_keywords)} raw keywords for auditing.")
    
    # Run the modular processing pipeline
    results = process_keywords_in_chunks(client, all_keywords, chunk_size=150)
    
    # Export final structured output
    save_clean_campaign_data(df, results, output_file, keyword_col)

if __name__ == "__main__":
    main()
