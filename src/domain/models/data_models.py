# Domain models [data models as classes]
from dataclasses import dataclass


@dataclass
class ProviderFeatures:
    name: str
    description: str
    url: str
    image: str
    price: str
    rating: float
    iso: str


@dataclass
class Provider:
    name: str
    description: str
    url: str
    image: str
    price: str
    rating: float
    iso: str
    features: ProviderFeatures


@dataclass
class ResponseMessageDC:
    detail: str = "Success"
    data: dict = {}
