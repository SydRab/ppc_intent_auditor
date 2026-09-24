from modules.api_client import evaluate_keyword_batch

def process_keywords_in_chunks(client, keywords_list: list, chunk_size: int = 150) -> list:
    """Splits keywords into batches and processes them safely to avoid rate limits."""
    batches = [keywords_list[i:i + chunk_size] for i in range(0, len(keywords_list), chunk_size)]
    master_results = []
    
    for idx, batch in enumerate(batches):
        print(f"Processing batch {idx + 1} of {len(batches)} ({len(batch)} keywords)...")
        batch_results = evaluate_keyword_batch(client, batch)
        if batch_results:
            master_results.extend(batch_results)
            
    return master_results
