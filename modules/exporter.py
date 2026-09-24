import pandas as pd

def save_clean_campaign_data(original_df: pd.DataFrame, results_list: list, output_filepath: str):
    """
    Safely merges multi-bucket intent classifications, exports approved high-intent records, 
    and auto-generates a negative keyword exclusion list.
    """
    if not results_list:
        print("[WARNING] No results returned from processing pipeline. Skipping export.")
        return

    results_df = pd.DataFrame(results_list)

    keyword_col = 'suggested_keyword' if 'suggested_keyword' in original_df.columns else 'keyword'
    
    if keyword_col not in original_df.columns:
        raise KeyError(f"Keyword column not found in original DataFrame: {original_df.columns.tolist()}")

    # Ensure expected scoring columns exist
    expected_cols = [
        'suggested_keyword', 'original_zip', 'compliance_status', 
        'intent_type', 'is_phone_intent', 'violation_category', 
        'bid_tier_weight', 'auto_negative_reason'
    ]
    for col in expected_cols:
        if col not in results_df.columns:
            results_df[col] = "N/A"

    # Standardize types for merging
    original_df['original_zip'] = original_df['original_zip'].astype(str).str.strip()
    original_df[keyword_col] = original_df[keyword_col].astype(str).str.strip()
    
    results_df['original_zip'] = results_df['original_zip'].astype(str).str.strip()
    results_df['suggested_keyword'] = results_df['suggested_keyword'].astype(str).str.strip()

    results_df = results_df.drop_duplicates(subset=['suggested_keyword', 'original_zip'])

    # Merge results back onto the original dataframe
    final_df = pd.merge(
        original_df,
        results_df[expected_cols],
        left_on=[keyword_col, 'original_zip'],
        right_on=['suggested_keyword', 'original_zip'],
        how='left'
    )

    # Cleanup duplicate columns if any
    if 'suggested_keyword_y' in final_df.columns:
        final_df = final_df.drop(columns=['suggested_keyword_y'])
    if 'suggested_keyword_x' in final_df.columns:
        final_df = final_df.rename(columns={'suggested_keyword_x': keyword_col})

    # Fill unmapped defaults safely
    final_df['compliance_status'] = final_df['compliance_status'].fillna('EXCLUDED')
    final_df['intent_type'] = final_df['intent_type'].fillna('Unknown')
    final_df['is_phone_intent'] = final_df['is_phone_intent'].fillna(False)
    final_df['violation_category'] = final_df['violation_category'].fillna('Unmatched')
    final_df['bid_tier_weight'] = final_df['bid_tier_weight'].fillna(0)
    final_df['auto_negative_reason'] = final_df['auto_negative_reason'].fillna('Unmatched filter rule')

    # 1. Export Approved High-Intent Keywords
    approved_df = final_df[final_df['compliance_status'] == 'APPROVED']
    approved_df.to_csv(output_filepath, index=False)
    print(f"Successfully exported {len(approved_df)} approved high-intent keywords to {output_filepath}")

    # 2. Auto-Generate Negative Keyword List CSV
    negatives_df = final_df[final_df['compliance_status'] == 'EXCLUDED'][[keyword_col, 'violation_category', 'auto_negative_reason']]
    negatives_filepath = "auto_negative_keywords.csv"
    negatives_df.to_csv(negatives_filepath, index=False)
    print(f"Auto-generated negative keyword exclusion list with {len(negatives_df)} terms at {negatives_filepath}")
