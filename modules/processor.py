from modules.api_client import evaluate_keyword_batch

def process_keywords_in_chunks(client, records_list: list, chunk_size: int = 100) -> list:
    """Splits records into batches and processes them safely."""
    batches = [records_list[i:i + chunk_size] for i in range(0, len(records_list), chunk_size)]
    master_results = []
    
    for idx, batch in enumerate(batches):
        print(f"Processing batch {idx + 1} of {len(batches)} ({len(batch)} items)...")
        batch_results = evaluate_keyword_batch(client, batch)
        if batch_results:
            master_results.extend(batch_results)
            
    return master_results
