# 2B-lvyou-pachong

Crawlab project template for a compliant lead-data pipeline:

```text
Authorized source pages / legally obtained exports
  -> browser extraction / CSV import
  -> email & phone normalization
  -> Google Sheets
  -> optional Mautic import later
```

Target Google Sheet:

```text
1eUknA5fqniT1KMLdsmqKSrpVXSZW726e3MXvfieOUU8
```

## Important compliance boundary

This project does **not** include code to scrape LinkedIn personal profiles, bypass login, bypass anti-bot protections, or collect private personal contact data such as personal email/phone numbers without a lawful basis.

For LinkedIn-related data, use one of these compliant inputs:

- LinkedIn official APIs / approved partner access.
- Data exported from tools/accounts where you have explicit rights to process it.
- User-consented forms, event registration data, or your own CRM records.
- Public business pages that allow crawling and do not prohibit automated access.

## Do you need n8n?

Not required for the minimal pipeline.

Use this repository directly when:

- the rules are fixed;
- the destination is only Google Sheets;
- a developer can maintain Python logic.

Add n8n when:

- operations staff need to change mapping/tagging rules visually;
- you need approval steps before writing leads;
- you need retries, alerts, or multiple destinations;
- you want to sync Google Sheets -> Mautic automatically.

## Google Sheets setup

1. Create a Google Cloud service account.
2. Enable Google Sheets API for the project.
3. Download the service-account JSON.
4. Share the target Google Sheet with the service-account email as Editor.
5. In Crawlab, set one of:
   - `GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-service-account.json`
   - or `GOOGLE_SERVICE_ACCOUNT_JSON=<raw json string>`
   - or `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=<base64 json string>` recommended when Crawlab env input does not handle multiline JSON well.

## Crawlab setup

In Crawlab:

1. Create a Python project from this Git repository.
2. Set install command:

```bash
pip install -r requirements.txt && python -m playwright install chromium
```

3. Set run command:

```bash
python src/main.py
```

4. Configure environment variables based on `.env.example`.

Required:

```bash
GOOGLE_SHEET_ID=1eUknA5fqniT1KMLdsmqKSrpVXSZW726e3MXvfieOUU8
GOOGLE_WORKSHEET_NAME=leads
SOURCE_URLS=https://example.com/contact,https://example.org/team
```

Recommended Google auth variable:

```bash
GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=<base64 encoded service-account JSON>
```

To generate this value on your own computer:

```bash
base64 -w 0 google-service-account.json
```

If your `base64` command does not support `-w`, use:

```bash
python3 -c "import base64, pathlib; print(base64.b64encode(pathlib.Path('google-service-account.json').read_bytes()).decode())"
```

Do not commit this value to GitHub.

## Output columns

The script writes these columns:

```text
name, email, phone, company, source_url, source, country, crawled_at
```

## Local dry run

```bash
cp .env.example .env
# edit SOURCE_URLS and set DRY_RUN=true
python src/main.py
```

Dry-run output is saved to `output/leads.csv`.

## Google Sheets run

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-service-account.json
export SOURCE_URLS=https://example.com/contact
python src/main.py
```

## Mautic next step

After leads land in Google Sheets, you can:

1. import CSV into Mautic manually;
2. run a separate script to push rows to Mautic Contacts API;
3. use n8n to watch Google Sheets, clean/approve rows, and write to Mautic.

Recommended production path:

```text
Crawlab -> Google Sheets review -> n8n -> Mautic Contacts API
```
