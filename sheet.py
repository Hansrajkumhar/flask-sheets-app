import os
import json
import gspread
import pandas as pd
import logging
from gspread_dataframe import set_with_dataframe
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound

logging.basicConfig(level=logging.INFO)

def process_projects(project_filters=None):
    """
    Process Google Sheets data by filtering rows based on projects
    and writing them into another Google Sheet.
    
    Args:
        project_filters (list[str] or None): List of project names to filter.
                                             If None, defaults to ["AIPPL_JAIGAD"].
    
    Returns:
        dict: Summary information about the processed data.
    """

    creds_path = "/tmp/temp_credentials.json"  # Only /tmp is writable on Render
    creds_json = os.getenv("GOOGLE_CREDENTIALS")

    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not set")

    try:
        # ✅ Validate JSON before writing
        creds_dict = json.loads(creds_json)
        with open(creds_path, "w") as f:
            json.dump(creds_dict, f)

        # ✅ Authenticate with gspread
        gc = gspread.service_account(filename=creds_path)

        # ✅ Source Sheet
        sh = gc.open("Test_BTS_10")
        worksheet = sh.worksheet("Sheet1")
        values = worksheet.get_all_values()

        if not values or len(values) < 2:
            raise ValueError("No data found in the sheet (need header + 1 row).")

        df = pd.DataFrame(values[1:], columns=values[0])
        total_rows = len(df)

        # ✅ Default projects if not provided
        if project_filters is None:
            project_filters = ["AIPPL_JAIGAD"]

        # ✅ Target Sheet
        sh2 = gc.open("SCRIPT FOR DATA ")

        results = {}
        for i, project in enumerate(project_filters, start=1):
            filtered_df = df[df["Project"] == project]

            try:
                ws = sh2.worksheet(f"Sheet{i}")
            except WorksheetNotFound:
                ws = sh2.add_worksheet(title=f"Sheet{i}", rows="1000", cols="20")

            ws.clear()
            set_with_dataframe(ws, filtered_df)

            results[project] = len(filtered_df)
            logging.info(f"Processed project {project}: {len(filtered_df)} rows → Sheet{i}")

        return {
            "total_rows": total_rows,
            "project_counts": results,
            "status": "success"
        }

    except (SpreadsheetNotFound, WorksheetNotFound) as e:
        raise ValueError(f"Sheet/worksheet not found: {str(e)}")
    except APIError as e:
        raise ValueError(f"Google Sheets API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}")
    finally:
        # ✅ Clean up temp file
        if os.path.exists(creds_path):
            os.remove(creds_path)
