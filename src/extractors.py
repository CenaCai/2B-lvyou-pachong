import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from urllib.parse import urlparse

import phonenumbers


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)


@dataclass
class Lead:
    name: str
    email: str
    phone: str
    company: str
    source_url: str
    source: str
    country: str
    crawled_at: str

    def row(self) -> list[str]:
        data = asdict(self)
        return [
            data["name"],
            data["email"],
            data["phone"],
            data["company"],
            data["source_url"],
            data["source"],
            data["country"],
            data["crawled_at"],
        ]


HEADER = ["name", "email", "phone", "company", "source_url", "source", "country", "crawled_at"]


def extract_emails(text: str) -> list[str]:
    emails = sorted({email.lower() for email in EMAIL_RE.findall(text or "")})
    return [email for email in emails if not email.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))]


def extract_phones(text: str, default_region: str | None = None) -> list[str]:
    phones: set[str] = set()
    for match in phonenumbers.PhoneNumberMatcher(text or "", default_region or None):
        if phonenumbers.is_possible_number(match.number) and phonenumbers.is_valid_number(match.number):
            phones.add(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164))
    return sorted(phones)


def domain_company_guess(url: str) -> str:
    host = urlparse(url).hostname or ""
    parts = host.replace("www.", "").split(".")
    if not parts:
        return ""
    return parts[0].replace("-", " ").title()


def build_leads(
    *,
    text: str,
    source_url: str,
    source: str,
    country: str,
    name: str = "",
    company: str = "",
) -> list[Lead]:
    emails = extract_emails(text)
    phones = extract_phones(text)
    guessed_company = company or domain_company_guess(source_url)
    phone = phones[0] if phones else ""
    crawled_at = datetime.now(timezone.utc).isoformat()

    return [
        Lead(
            name=name,
            email=email,
            phone=phone,
            company=guessed_company,
            source_url=source_url,
            source=source,
            country=country,
            crawled_at=crawled_at,
        )
        for email in emails
    ]


def dedupe_leads(leads: list[Lead]) -> list[Lead]:
    seen: set[str] = set()
    result: list[Lead] = []
    for lead in leads:
        key = lead.email.lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(lead)
    return result
