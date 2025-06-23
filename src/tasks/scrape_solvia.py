from prefect import task

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from models.pydantic_models import Apartment
from config.logger import get_logger
import traceback
from tqdm import tqdm

from helpers.utils import (
    extract_price,
    extract_int,
    extract_square_meters,
)


logger = get_logger("scrape_solvia")


@task
def scrape_solvia(url: str) -> list[Apartment]:
    """
    Scrapes property listings from Solvia.
    Each listing includes name, address, m2, number of bedrooms, bathrooms, and URL.
    """

    listings = []

    try:
        r = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(r).read()
    except Exception as e:
        logger.error(f"Error fetching the URL: {url} - {e}")
        logger.debug(traceback.format_exc())
        return []

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_="house-info")
    logger.info(f"Found {len(cards)} property cards")

    for i, card in tqdm(enumerate(cards), total=len(cards), desc="Scraping Solvia"):
        try:
            # url
            url_apartment = card.find("a").get("href")
            # name
            name = card.find("h3", {"class": "build-name"}).get_text(strip=True)
            # addres
            address_div = card.find("div", class_="build-address")
            span_elements = address_div.find_all("span") if address_div else []
            address_parts = [span.get_text(strip=True) for span in span_elements]
            address = " ".join(address_parts)
            # m2, bedrooms, bathroom
            ul = card.find("ul", class_="build-tags")
            li_elements = ul.find_all("li") if ul else []
            li_texts = [li.get_text(strip=True) for li in li_elements]

            square_meters = (
                extract_square_meters(li_texts[0]) if len(li_texts) > 0 else None
            )
            num_bedroom = extract_int(li_texts[1]) if len(li_texts) > 1 else None
            num_bathroom = extract_int(li_texts[2]) if len(li_texts) > 2 else None

            # price
            price_text = card.find("span", {"class": "final-price mb-1"}).get_text(
                strip=True
            )
            price = extract_price(price_text)

            listings.append(
                {
                    "name": name,
                    "address": address,
                    "m2": square_meters,
                    "bedrooms": num_bedroom,
                    "bathrooms": num_bathroom,
                    "url": url_apartment,
                    "price": price,
                }
            )

            logger.debug(f"[{i + 1}/{len(cards)}] Parsed: {name} | {address}")

        except AttributeError as ae:
            logger.warning(
                f"[{i + 1}] Missing expected field in listing. Skipping. Error: {ae}"
            )
        except Exception as e:
            logger.error(f"[{i + 1}] Unexpected error while parsing a listing: {e}")
            logger.debug(traceback.format_exc())

    logger.info(f"Finished scraping {len(listings)} valid listings from {url}")

    return listings
