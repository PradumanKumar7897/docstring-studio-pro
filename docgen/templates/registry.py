from .google import GoogleTemplate
from .numpy import NumpyTemplate
from .rest import RestTemplate


TEMPLATES = {
    "google": GoogleTemplate(),
    "numpy": NumpyTemplate(),
    "rest": RestTemplate(),
}


def get_template(style: str):
    style = (style or "google").lower()
    if style not in TEMPLATES:
        raise ValueError(f"Unknown docstring style: {style}")
    return TEMPLATES[style]
