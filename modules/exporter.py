import pandas as pd

def save_clean_campaign_data(original_df: pd.DataFrame, results_list: list, output_filepath: str):
    """
    Safely merges evaluation results back to the original DataFrame 
    while strictly retaining the original column names (e.g., 'suggested_keyword').
    """
    if not results_list:
        print("[WARNING] No results returned from processing pipeline. Skipping export.")
        return

    results_df = pd.DataFrame(results_list)

    # Automatically detect the keyword column name in the source dataframe
    keyword_col = 'suggested_keyword' if 'suggested_keyword' in original_df.columns else 'keyword'
    
    if keyword_col not in original_df.columns:
        raise KeyError(f"Neither 'suggested_keyword' nor 'keyword' found in original DataFrame columns: {original_df.columns.tolist()}")

    # Ensure all expected result columns exist
    expected_cols = ['keyword', 'original_zip', 'status', 'reason', 'campaign_name', 'ad_group']
    for col in expected_cols:
        if col not in results_df.columns:
            results_df[col] = "N/A"

    # Standardize data types for safe merging
    original_df['original_zip'] = original_df['original_zip'].astype(str).str.strip()
    original_df[keyword_col] = original_df[keyword_col].astype(str).str.strip()
    
    results_df['original_zip'] = results_df['original_zip'].astype(str).str.strip()
    results_df['keyword'] = results_df['keyword'].astype(str).str.strip()

    # Drop duplicates in results to prevent duplication during merge
    results_df = results_df.drop_duplicates(subset=['keyword', 'original_zip'])

    # Merge using the detected original column name on the left and 'keyword' from results on the right
    final_df = pd.merge(
        original_df,
        results_df[['keyword', 'original_zip', 'status', 'reason', 'campaign_name', 'ad_group']],
        left_on=[keyword_col, 'original_zip'],
        right_on=['keyword', 'original_zip'],
        how='left'
    )

    # Clean up duplicate keyword column if it got duplicated during merge
    if 'keyword_y' in final_df.columns:
        final_df = final_df.drop(columns=['keyword_y'])
    if 'keyword_x' in final_df.columns:
        final_df = final_df.rename(columns={'keyword_x': keyword_col})

    # Fill unmapped rows safely
    final_df['status'] = final_df['status'].fillna('EXCLUDE')
    final_df['campaign_name'] = final_df['campaign_name'].fillna('N/A')
    final_df['ad_group'] = final_df['ad_group'].fillna('N/A')
    final_df['reason'] = final_df['reason'].fillna('Unmatched or filtered out')

    # Filter only approved records
    approved_df = final_df[final_df['status'] == 'KEEP']
    approved_df.to_csv(output_filepath, index=False)
    print(f"Successfully exported {len(approved_df)} approved keywords to {output_filepath} retaining column '{keyword_col}'.")
