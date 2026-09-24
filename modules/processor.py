import time
from modules.api_client import evaluate_keyword_batch

def process_keywords_in_chunks(client, records_list: list, chunk_size: int = 150) -> list:
    """
    Splits records into batches and processes them. 
    Implements a 'fail-fast' mechanism to stop immediately on any API error.
    """
    batches = [records_list[i:i + chunk_size] for i in range(0, len(records_list), chunk_size)]
    master_results = []
    
    for idx, batch in enumerate(batches):
        print(f"Processing batch {idx + 1} of {len(batches)} ({len(batch)} items)...")
        
        try:
            batch_results = evaluate_keyword_batch(client, batch)
            
            # If the API client returns an empty list or encounters an unhandled issue
            if batch_results is None:
                raise ValueError(f"Batch {idx + 1} returned a null/empty response from Gemini API.")
                
            master_results.extend(batch_results)
            
        except Exception as e:
            print(f"\n[FATAL ERROR] Pipeline halted at batch {idx + 1} of {len(batches)}.")
            print(f"Reason: {e}")
            print("Stopping execution immediately to prevent partial outputs.")
            # Raise exception to stop workflow instantly and prevent git exit code 128
            raise SystemExit(1)
            
        # Pacing timer to maintain smooth throughput
        if idx < len(batches) - 1:
            time.sleep(5)
            
    return master_results
