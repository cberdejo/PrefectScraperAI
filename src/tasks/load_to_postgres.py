from prefect import task

from config.postgres import get_engine, get_session
from models.sqlalchemy_models import Apartment_DB, Base
from config.logger import get_logger
from tqdm import tqdm

logger = get_logger("load_to_postgres")


def normalize_url(url: str) -> str:
    """
    Normalize URL by stripping spaces and converting to lowercase.
    This helps avoid duplicate key errors due to minor URL variations.
    """
    return url.strip().lower()


@task
def load_info_to_postgres(new_apartments: list[Apartment_DB]):
    """
    Loads a list of Apartment_DB objects into a PostgreSQL database.

    This task ensures the table exists, updates records that already exist
    (based on primary key `url`), and inserts new records using a batch operation.
    It normalizes URLs to avoid mismatches and prevents duplicate key errors by
    removing already-existing records from the insertion batch.

    Args:
        new_apartments (list[Apartment_DB]): A list of apartment records to insert or update.

    Returns:
        int: The number of errors encountered during the operation.

    """
    try:
        engine = get_engine()
        Base.metadata.create_all(engine)
        session = get_session(engine)
    except Exception as e:
        raise RuntimeError(f"Error conecting in database: {e}")

    try:
        # Normalize and map apartments by URL
        apartment_map = {normalize_url(ap.url): ap for ap in new_apartments}
        urls = list(apartment_map.keys())

        # Fetch existing apartment URLs from the database
        existing = (
            session.query(Apartment_DB.url).filter(Apartment_DB.url.in_(urls)).all()
        )
        existing_urls = {normalize_url(url[0]) for url in existing}

        updated_count = 0
        inserted_count = 0

        # Merge existing apartments
        for url in tqdm(existing_urls, desc="Merging existing apartments"):
            session.merge(apartment_map.pop(url))
            updated_count += 1

        # Insert only the remaining (new) apartments
        new_entries = list(apartment_map.values())
        if new_entries:
            session.bulk_save_objects(new_entries)
            inserted_count = len(new_entries)

        session.commit()

        # Log successful operations
        if updated_count > 0:
            logger.info(f"{updated_count} existing apartments were updated.")
        if inserted_count > 0:
            logger.info(f"{inserted_count} new apartments were inserted.")

    except Exception as e:
        session.rollback()
        logger.error(f"An error occurred while writing to PostgreSQL: {e}")
    finally:
        session.close()
