import asyncio
import csv
from pathlib import Path

from playwright.async_api import async_playwright

from config import load_settings
from extractors import HEADER, Lead, build_leads, dedupe_leads
from google_sheets import append_leads


async def _text_or_empty(page, selector: str | None) -> str:
    if not selector:
        return ""
    try:
        locator = page.locator(selector).first
        if await locator.count() == 0:
            return ""
        return (await locator.inner_text()).strip()
    except Exception:
        return ""


async def crawl_url(page, url: str, settings) -> list[Lead]:
    print(f"Crawling authorized URL: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(int(settings.request_delay_seconds * 1000))

    text = await page.locator("body").inner_text(timeout=30000)
    name = await _text_or_empty(page, settings.name_selector)
    company = await _text_or_empty(page, settings.company_selector)

    return build_leads(
        text=text,
        source_url=url,
        source=settings.default_source,
        country=settings.default_country,
        name=name,
        company=company,
    )


async def crawl_all(settings) -> list[Lead]:
    if not settings.source_urls:
        raise RuntimeError("SOURCE_URLS is empty. Add authorized URLs to crawl.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=settings.headless)
        page = await browser.new_page()

        leads: list[Lead] = []
        for url in settings.source_urls[: settings.max_pages]:
            try:
                leads.extend(await crawl_url(page, url, settings))
            except Exception as exc:
                print(f"Failed to crawl {url}: {exc}")

        await browser.close()

    return dedupe_leads(leads)


def write_csv(leads: list[Lead]) -> None:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    path = output_dir / "leads.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows([lead.row() for lead in leads])
    print(f"Wrote dry-run CSV: {path}")


async def main() -> None:
    settings = load_settings()
    leads = await crawl_all(settings)
    print(f"Extracted {len(leads)} unique leads.")

    if settings.dry_run:
        write_csv(leads)
    else:
        append_leads(settings.google_sheet_id, settings.worksheet_name, leads)


if __name__ == "__main__":
    asyncio.run(main())
