import pandas as pd

def save_clean_campaign_data(raw_df: pd.DataFrame, results_list: list, output_filename: str, keyword_col: str):
    """Merges LLM outputs back with original metrics and exports clean CSV."""
    results_df = pd.DataFrame(results_list)
    
    if results_df.empty:
        print("Warning: No results returned from processing pipeline.")
        return

    # Keep only approved keywords
    approved_df = results_df[results_df['status'] == 'KEEP'].copy()
    
    # Merge back original metrics (search volume, CPC data, etc.)
    final_df = pd.merge(approved_df, raw_df, left_on='keyword', right_on=keyword_col, how='left')
    
    final_df.to_csv(output_filename, index=False)
    print(f"\n[Success] Clean campaign data saved to: {output_filename}")
    print(f"Total Approved Keywords Ready for Campaign Build: {len(approved_df)}")
