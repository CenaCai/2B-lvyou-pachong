import base64
import json
import os

import gspread
from google.oauth2.service_account import Credentials

from extractors import HEADER, Lead


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _credentials() -> Credentials:
    raw_json_base64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64")
    if raw_json_base64:
        raw_json = base64.b64decode(raw_json_base64).decode("utf-8")
        info = json.loads(raw_json)
        return Credentials.from_service_account_info(info, scopes=SCOPES)

    raw_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw_json:
        info = json.loads(raw_json)
        return Credentials.from_service_account_info(info, scopes=SCOPES)

    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not path:
        raise RuntimeError(
            "Set GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_SERVICE_ACCOUNT_JSON, "
            "or GOOGLE_SERVICE_ACCOUNT_JSON_BASE64 for Google Sheets access."
        )
    return Credentials.from_service_account_file(path, scopes=SCOPES)


def append_leads(sheet_id: str, worksheet_name: str, leads: list[Lead]) -> None:
    if not leads:
        print("No leads to append.")
        return

    client = gspread.authorize(_credentials())
    spreadsheet = client.open_by_key(sheet_id)

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=len(HEADER))

    existing = worksheet.get_all_values()
    if not existing:
        worksheet.append_row(HEADER)

    existing_emails = {
        row[1].strip().lower()
        for row in existing[1:]
        if len(row) > 1 and row[1].strip()
    }
    new_rows = [lead.row() for lead in leads if lead.email.lower() not in existing_emails]

    if not new_rows:
        print("All leads already exist in the sheet.")
        return

    worksheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    print(f"Appended {len(new_rows)} new leads to Google Sheets.")
