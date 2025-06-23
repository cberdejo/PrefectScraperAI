from datetime import datetime
import re
from typing import Optional

from models.pydantic_models import TimeTask


def extract_int(text: str) -> int | None:
    """
    Extracts the first integer found in a given string.
    Args:
        text (str): The input string from which to extract the integer.
    Returns:
        int | None: The first integer found in the string as an integer,
        or None if no integer is found.
    """

    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def extract_square_meters(text: str) -> float | None:
    """
    Extracts the numeric value representing square meters from a given text string.
    This function searches for a numeric value followed by the letter 'm' (case-insensitive)
    in the input text. If a match is found, the numeric value is converted to a float and returned.
    If no match is found, the function returns None.
    Args:
        text (str): The input string from which to extract the square meter value.
    Returns:
        float | None: The extracted square meter value as a float, or None if no match is found.
    """

    match = re.search(r"([\d,.]+)\s?m", text.lower())
    return float(match.group(1).replace(",", ".")) if match else None


def extract_price(text: str) -> float | None:
    """
    Extracts the first float-like number from a string with optional thousands separator.
    Handles European format like '950.000 €' or '423.500,75 €'.

    Returns:
        float or None
    """
    # Eliminar símbolo € y espacios
    clean_text = text.replace("€", "").replace(" ", "").strip()

    # Reemplazar punto (miles) por nada, coma (decimal) por punto
    clean_text = clean_text.replace(".", "").replace(",", ".")

    match = re.search(r"\d+(\.\d+)?", clean_text)
    return float(match.group()) if match else None

