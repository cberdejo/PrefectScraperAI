import asyncio
from prefect import flow

from tasks.generate_embedding import generate_embeddings
from tasks.scrape_pisos import scrape_pisos
from tasks.scrape_solvia import scrape_solvia
from tasks.upload_report import save_task_metadata_to_minio
from tasks.load_to_postgres import load_info_to_postgres


@flow(name="Real Estate Scraper", retries=1, retry_delay_seconds=5)
async def run_prefect_pipeline(pisos_urls: list[str], solvia_urls: list[str]) -> None:

     # Scrape pisos and solvia
    pisos_futures = scrape_pisos.map(pisos_urls)
    pisos_results = list(zip(*[f.result() for f in pisos_futures]))
    
    solvia_futures = scrape_solvia.map(solvia_urls)
    solvia_results = list(zip(*[f.result() for f in solvia_futures]))
    
    # Combine results by converting zips to lists first
    all_results = [ad for group in list(pisos_results) + list(solvia_results) for ad in group]

    # Generate embeddings

    embedded_all_results =  generate_embeddings(all_results)

    # Load into Postgres

    load_info_to_postgres(embedded_all_results)

    # Error count and report
    await save_task_metadata_to_minio()