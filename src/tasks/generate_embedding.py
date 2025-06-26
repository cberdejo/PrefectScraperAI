from models.pydantic_models import Apartment
from models.sqlalchemy_models import Apartment_DB
from config.logger import get_logger
from sentence_transformers import SentenceTransformer
from prefect import task

logger = get_logger("generate_embeddings")


@task
def generate_embeddings(apartments: list[Apartment]) -> list[Apartment_DB]:
    """
    Generate embeddings for a list of apartments using a pre-trained SentenceTransformer model.
    Returns a list of Apartment_DB objects enriched with the generated embeddings.
    Args:
        apartments (list[Apartment]): A list of Apartment objects to generate embeddings for.
    Returns:
        list[Apartment_DB]: A list of Apartment_DB objects with embeddings.

    """
    apartments = [Apartment(**ad) if isinstance(ad, dict) else ad for ad in apartments]

    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        # model = SentenceTransformer("paraphrase-MiniLM-L3-v2")

    except Exception as e:
        logger.critical(f"Error loading SentenceTransformer model: {e}")
        return []

    results = []
    for i, apartment in enumerate(apartments):
        try:
            description = str(apartment)
            vector = model.encode([description])[0].tolist()

            apartment_db = Apartment_DB(
                url=apartment.url,
                name=apartment.name,
                address=apartment.address,
                m2=apartment.m2,
                bedrooms=apartment.bedrooms,
                bathrooms=apartment.bathrooms,
                price=apartment.price,
                embedding=vector,
            )
            results.append(apartment_db)

        except Exception as e:
            logger.warning(f"Error generating embedding for apartment [{i + 1}]: {e}")

    logger.info(f"Generated {len(results)} embeddings")
    return results
