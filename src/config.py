import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    google_sheet_id: str
    worksheet_name: str
    source_urls: list[str]
    name_selector: str | None
    company_selector: str | None
    next_page_selector: str | None
    headless: bool
    max_pages: int
    request_delay_seconds: float
    default_country: str
    default_source: str
    dry_run: bool


def load_settings() -> Settings:
    source_urls = [
        url.strip()
        for url in os.getenv("SOURCE_URLS", "").split(",")
        if url.strip()
    ]

    return Settings(
        google_sheet_id=os.getenv("GOOGLE_SHEET_ID", "1eUknA5fqniT1KMLdsmqKSrpVXSZW726e3MXvfieOUU8"),
        worksheet_name=os.getenv("GOOGLE_WORKSHEET_NAME", "leads"),
        source_urls=source_urls,
        name_selector=os.getenv("NAME_SELECTOR") or None,
        company_selector=os.getenv("COMPANY_SELECTOR") or None,
        next_page_selector=os.getenv("NEXT_PAGE_SELECTOR") or None,
        headless=_bool_env("HEADLESS", True),
        max_pages=int(os.getenv("MAX_PAGES", "20")),
        request_delay_seconds=float(os.getenv("REQUEST_DELAY_SECONDS", "2")),
        default_country=os.getenv("DEFAULT_COUNTRY", ""),
        default_source=os.getenv("DEFAULT_SOURCE", "authorized_web"),
        dry_run=_bool_env("DRY_RUN", False),
    )
