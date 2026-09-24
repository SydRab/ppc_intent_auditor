import time
from modules.api_client import evaluate_keyword_batch

def process_keywords_in_chunks(client, records_list: list, chunk_size: int = 100) -> list:
    """Splits records into batches and processes them safely with rate-limit pacing."""
    batches = [records_list[i:i + chunk_size] for i in range(0, len(records_list), chunk_size)]
    master_results = []
    
    for idx, batch in enumerate(batches):
        print(f"Processing batch {idx + 1} of {len(batches)} ({len(batch)} items)...")
        batch_results = evaluate_keyword_batch(client, batch)
        if batch_results:
            master_results.extend(batch_results)
            
        # Add a 12-second pause between batches to respect free-tier rate limits (max 5 req/min)
        if idx < len(batches) - 1:
            time.sleep(12)
            
    return master_results
