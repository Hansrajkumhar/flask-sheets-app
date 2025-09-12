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
    Process Google Sheets data by filtering rows based on provided projects
    and writing them into another Google Sheet.

    Args:
        project_filters (list[str] or str or None): List of project names to filter.
                                                    If None or empty, all rows are processed.

    Returns:
        dict: Summary information about the processed data.
    """

    creds_path = "/tmp/temp_credentials.json"  # Only /tmp is writable on Render
    creds_json = os.getenv("GOOGLE_CREDENTIALS")

    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS environment variable not set")

    try:
        # Validate and write credentials
        creds_dict = json.loads(creds_json)
        with open(creds_path, "w") as f:
            json.dump(creds_dict, f)

        # Authenticate with gspread
        gc = gspread.service_account(filename=creds_path)

        # Source sheet
        sh = gc.open("Test_BTS_10")
        worksheet = sh.worksheet("Sheet1")
        values = worksheet.get_all_values()

        if not values or len(values) < 2:
            raise ValueError("No data found in the sheet (need header + 1 row).")

        df = pd.DataFrame(values[1:], columns=values[0])
        total_rows = len(df)

        # Normalize project_filters: convert string to list
        if isinstance(project_filters, str):
            project_filters = [project_filters]

        # If project_filters is provided, remove empty strings
        if project_filters:
            project_filters = [p for p in project_filters if p.strip() != ""]
            filtered_projects = project_filters
        else:
            # If no filter provided, take all unique non-empty project values
            filtered_projects = df["Project"].dropna().unique().tolist()

        # Target sheet
        sh2 = gc.open("SCRIPT FOR DATA ")

        results = {}
        for i, project in enumerate(filtered_projects, start=1):
            filtered_df = df[df["Project"] == project] if project_filters else df

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
        # Clean up temp credentials
        if os.path.exists(creds_path):
            os.remove(creds_path)
