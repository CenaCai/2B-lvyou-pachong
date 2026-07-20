import csv
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from extractors import Lead, dedupe_leads
from google_sheets import append_leads


load_dotenv()


def main() -> None:
    path = os.getenv("INPUT_CSV", "input/leads.csv")
    sheet_id = os.getenv("GOOGLE_SHEET_ID", "1eUknA5fqniT1KMLdsmqKSrpVXSZW726e3MXvfieOUU8")
    worksheet_name = os.getenv("GOOGLE_WORKSHEET_NAME", "leads")

    leads: list[Lead] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            email = (row.get("email") or row.get("Email") or "").strip().lower()
            if not email:
                continue
            leads.append(
                Lead(
                    name=(row.get("name") or row.get("Name") or "").strip(),
                    email=email,
                    phone=(row.get("phone") or row.get("Phone") or "").strip(),
                    company=(row.get("company") or row.get("Company") or "").strip(),
                    source_url=(row.get("source_url") or row.get("Source URL") or "").strip(),
                    source=(row.get("source") or "csv_import").strip(),
                    country=(row.get("country") or row.get("Country") or "").strip(),
                    crawled_at=(row.get("crawled_at") or datetime.now(timezone.utc).isoformat()).strip(),
                )
            )

    append_leads(sheet_id, worksheet_name, dedupe_leads(leads))


if __name__ == "__main__":
    main()
