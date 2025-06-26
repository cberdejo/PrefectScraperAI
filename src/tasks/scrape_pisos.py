from prefect import task

from typing import Optional
from config.logger import get_logger
import math
import re
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
    StaleElementReferenceException,
)

import tempfile

from models.pydantic_models import Apartment
from helpers.utils import (
    extract_int,
    extract_price,
    extract_square_meters,
)

logger = get_logger("scrape_pisos")


def init_selenium(options: Optional[Options] = None) -> WebDriver:
    """
    Initializes the Selenium WebDriver with the provided options.
    Args:
        options (Optional[Options]): Custom options for the WebDriver. If None, uses default headless options.
    Returns:
        WebDriver: An instance of the Selenium WebDriver.
    Raises:
        WebDriverException: If there is an error initializing the WebDriver.
    """

    if not options:
        options = Options()
        options.add_argument("--headless")

        # Usa un directorio temporal para evitar conflictos de usuario
        tmp_profile = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={tmp_profile}")

    try:
        driver = webdriver.Chrome(options=options)
        logger.info("Selenium WebDriver initialized.")
        return driver
    except WebDriverException as e:
        logger.error(f"Error initializing Selenium WebDriver: {e}")
        raise


def wait_page_to_be_loaded(driver: WebDriver, timeout: int = 10):
    """
    Waits for the page to be fully loaded by checking for the presence of the price element.
    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        timeout (int): Maximum time to wait for the page to load (in seconds).
    Raises:
        TimeoutException: If the page does not load within the specified timeout.
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ad-preview__price"))
        )
    except TimeoutException:
        logger.error("Timeout waiting for page to load.")


def accept_cookies(driver: WebDriver):
    """
    Accepts cookies on the page if the cookie banner is present.
    Args:
        driver (WebDriver): The Selenium WebDriver instance.
    Raises:
        TimeoutException: If the cookie banner does not appear within the specified timeout.
    """
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        accept_button.click()
        logger.info("Cookies accepted successfully.")
    except TimeoutException:
        logger.warning("No cookie banner appeared (timeout).")
    except Exception as e:
        logger.error(f"Error while accepting cookies: {e}")


def get_total_pages(driver) -> int:
    """
    Obtains the total number of pages from the pagination counter.
    Args:
        driver (WebDriver): The Selenium WebDriver instance.
    Returns:
        int: The total number of pages, or 0 if the counter is not found or an error occurs.
    """
    try:
        counter = driver.find_element(
            By.XPATH,
            '//*[@class="pagination__counter" and contains(text(), "resultados")]',
        ).text
        match = re.search(r"de\s+(\d+)\s+resultados", counter)
        if match:
            total_results = int(match.group(1))
            return math.ceil(total_results / 30)
        else:
            logger.warning("No se pudo encontrar el total de resultados.")
            return 0
    except Exception as e:
        logger.error(f"Error obteniendo el número total de páginas: {e}")
        return 0


def close_poping_modal(driver: WebDriver, timeout: int = 3):
    """
    Closes any pop-up modal that appears on the page.
    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        timeout (int): Maximum time to wait for the modal to appear (in seconds).
    Raises:
        StaleElementReferenceException: If the modal element is stale (no longer attached to the DOM).
        TimeoutException: If the modal does not appear within the specified timeout.
        Exception: For any other unexpected errors.
    """
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "modal__content")))
        logger.info("Modal detected. Attempting to close it.")

        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "modal__close"))
        )
        close_button = driver.find_element(By.CLASS_NAME, "modal__close")
        close_button.click()
        logger.info("Modal closed successfully.")

    except StaleElementReferenceException:
        logger.warning("Stale element. Modal was removed before it could be clicked.")
    except TimeoutException:
        pass
    except Exception as e:
        logger.error(f"Unexpected error while closing modal: {e}")


def scrape_page(driver: WebDriver) -> list[Apartment]:
    """
    Scrapes a single page of apartment listings from the current URL in the WebDriver.
    Args:
        driver (WebDriver): The Selenium WebDriver instance.
    Returns:
        list[Apartment]: A list of Apartment objects containing the scraped data.
    """
    close_poping_modal(driver)
    wait_page_to_be_loaded(driver)
    apartments: list[Apartment] = []

    try:
        divs = driver.find_elements(
            By.XPATH, '//div[contains(@class, "grid__wrapper")]//div[@data-lnk-href]'
        )
    except Exception as e:
        logger.error(f"Error locating apartment divs: {e}")
        return []

    for i, div in enumerate(divs):
        try:
            url_apartment = div.get_attribute("data-lnk-href")
            full_url = f"https://www.pisos.com{url_apartment}"

            name = div.find_element(By.CLASS_NAME, "ad-preview__title").text.strip()
            address = div.find_element(
                By.CLASS_NAME, "ad-preview__subtitle"
            ).text.strip()
            price_text = div.find_element(By.CLASS_NAME, "ad-preview__price").text
            price = extract_price(price_text)

            chars = div.find_elements(By.CLASS_NAME, "ad-preview__char")
            bedrooms = extract_int(chars[0].text) if len(chars) > 0 else None
            bathrooms = extract_int(chars[1].text) if len(chars) > 1 else None
            square_meters = (
                extract_square_meters(chars[2].text) if len(chars) > 2 else None
            )

            apartment = Apartment(
                name=name,
                address=address,
                m2=square_meters,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                price=price,
                url=full_url,
            )

            apartments.append(apartment)

        except NoSuchElementException as e:
            logger.warning(f"Missing expected element in listing [{i + 1}]: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing listing [{i + 1}]: {e}")

    return apartments


@task
def scrape_pisos(url: str) -> list[Apartment]:
    listings = []

    try:
        driver = init_selenium()
        driver.get(url)
        wait_page_to_be_loaded(driver)
        accept_cookies(driver)

        total_pages = get_total_pages(driver)
        progress_bar = tqdm(total=total_pages, desc="Scraping pages", unit="page")

        while True:
            page_data = scrape_page(driver)
            listings.extend(page_data)

            try:
                next_button = driver.find_element(
                    By.XPATH, '//div[contains(@class, "pagination__next")]//a'
                )
                next_button.click()
                progress_bar.update(1)
            except NoSuchElementException:
                logger.info("No more pages to scrape. Exiting loop.")
                break
            except Exception as e:
                logger.error(f"Error clicking next page: {e}")
                break

        logger.info(f"Scraping finished. Total listings: {len(listings)}")
        return listings

    except Exception as e:
        logger.critical(f"Fatal error during scraping: {e}")
        return []

    finally:
        try:
            driver.quit()
        except Exception:
            logger.warning("WebDriver could not be closed properly.")
