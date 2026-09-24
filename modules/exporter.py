import pandas as pd

def save_clean_campaign_data(original_df: pd.DataFrame, results_list: list, output_filepath: str):
    """
    Merges original keyword rows with audit results and exports the approved campaign file.
    Coerces 'original_zip' to string on both sides to prevent pandas merge data-type errors.
    """
    if not results_list:
        print("[WARNING] No results returned from processing pipeline. Skipping export.")
        return

    results_df = pd.DataFrame(results_list)

    # Standardize original_zip to string to prevent int64 vs object merge crash
    original_df['original_zip'] = original_df['original_zip'].astype(str).str.strip()
    results_df['original_zip'] = results_df['original_zip'].astype(str).str.strip()

    # Merge back to original data
    final_df = pd.merge(
        original_df,
        results_df[['keyword', 'original_zip', 'status', 'reason', 'campaign_name', 'ad_group']],
        on=['keyword', 'original_zip'],
        how='inner'
    )

    # Filter only KEEP status
    approved_df = final_df[final_df['status'] == 'KEEP']

    # Save to CSV
    approved_df.to_csv(output_filepath, index=False)
    print(f"Successfully exported {len(approved_df)} approved keywords to {output_filepath}")
