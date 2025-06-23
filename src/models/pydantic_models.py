from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Apartment(BaseModel):
    url: str
    name: str
    address: str
    m2: float | None
    bedrooms: int | None
    bathrooms: int | None
    price: float | None

    def __str__(self):
        parts = [
            f"Nombre: {self.name}",
            f"Dirección: {self.address}",
            f"Superficie: {self.m2} m²" if self.m2 else "Superficie: desconocida",
            f"Dormitorios: {self.bedrooms}"
            if self.bedrooms
            else "Dormitorios: desconocido",
            f"Baños: {self.bathrooms}" if self.bathrooms else "Baños: desconocido",
            f"Precio: {self.price} €" if self.price else "Precio: desconocido",
            f"URL: {self.url}",
        ]

        return " | ".join(parts)


class TimeTask(BaseModel):
    task_name: str
    duration: float  # in seconds
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class Report(BaseModel):
    apartments_processed: int
    errors_found_scraping: int
    errors_found_embedding: int
    errors_found_inserting_postgress: int
    time: list[TimeTask]
