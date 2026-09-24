import pandas as pd

def save_clean_campaign_data(original_df: pd.DataFrame, results_list: list, output_filepath: str):
    """
    Safely merges original rows with evaluation results without crashing on missing columns.
    """
    if not results_list:
        print("[WARNING] No results returned from processing pipeline. Skipping export.")
        return

    results_df = pd.DataFrame(results_list)

    # Ensure all expected columns exist in results_df to prevent KeyErrors
    expected_cols = ['keyword', 'original_zip', 'status', 'reason', 'campaign_name', 'ad_group']
    for col in expected_cols:
        if col not in results_df.columns:
            results_df[col] = "N/A"

    # Standardize data types for safe merging
    original_df['original_zip'] = original_df['original_zip'].astype(str).str.strip()
    original_df['keyword'] = original_df['keyword'].astype(str).str.strip()
    
    results_df['original_zip'] = results_df['original_zip'].astype(str).str.strip()
    results_df['keyword'] = results_df['keyword'].astype(str).str.strip()

    # Drop duplicates in results to avoid Cartesian explosion during merge
    results_df = results_df.drop_duplicates(subset=['keyword', 'original_zip'])

    # Perform safe left join
    final_df = pd.merge(
        original_df,
        results_df[expected_cols],
        on=['keyword', 'original_zip'],
        how='left'
    )

    # Fill unmapped rows safely
    final_df['status'] = final_df['status'].fillna('EXCLUDE')
    final_df['campaign_name'] = final_df['campaign_name'].fillna('N/A')
    final_df['ad_group'] = final_df['ad_group'].fillna('N/A')
    final_df['reason'] = final_df['reason'].fillna('Unmatched or filtered out')

    # Filter only approved records
    approved_df = final_df[final_df['status'] == 'KEEP']
    approved_df.to_csv(output_filepath, index=False)
    print(f"Successfully exported {len(approved_df)} approved keywords to {output_filepath}")
