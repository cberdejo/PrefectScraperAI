import asyncio
from pipeline.prefect_pipeline import run_prefect_pipeline

if __name__ == "__main__":
    pisos_urls = [
        "https://www.pisos.com/venta/pisos-torremolinos/",
    ]
    solvia_urls = [
        "https://www.solvia.es/es/comprar/viviendas?texto=29620&palabraClave=true",
        "https://www.solvia.es/es/comprar/viviendas?texto=29006&palabraClave=true",
    ]
    asyncio.run(run_prefect_pipeline(pisos_urls=pisos_urls, solvia_urls=solvia_urls))
