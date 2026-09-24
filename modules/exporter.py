import pandas as pd

def save_clean_campaign_data(raw_df: pd.DataFrame, results_list: list, output_filename: str):
    """Merges LLM outputs back with original row data matching keyword and zip."""
    results_df = pd.DataFrame(results_list)
    
    if results_df.empty:
        print("Warning: No results returned from processing pipeline.")
        return

    # Keep only approved keywords
    approved_df = results_df[results_df['status'] == 'KEEP'].copy()
    
    # Merge back original metrics using both keyword and zip to maintain precise mapping
    final_df = pd.merge(
        approved_df, 
        raw_df, 
        left_on=['keyword', 'original_zip'], 
        right_on=['suggested_keyword', 'original_zip'], 
        how='left'
    )
    
    final_df.to_csv(output_filename, index=False)
    print(f"\n[Success] Clean campaign data saved to: {output_filename}")
    print(f"Total Approved Keyword-Zip Pairs Ready for Campaign Build: {len(approved_df)}")
