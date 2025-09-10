import os
import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound

def process_projects(project_filter=None):
    # Hardcoded credentials path
    creds_path = "C:/Users/Hanshraj/Downloads/PYTHON/gleaming-glass-394303-a32a50e54159.json"
    if not os.path.exists(creds_path):
        raise ValueError(f"Credentials file not found: {creds_path}")

    try:
        gc = gspread.service_account(filename=creds_path)
        sh = gc.open("Test_BTS_10")
        worksheet = sh.worksheet("Sheet1")
        values = worksheet.get_all_values()

        if not values or len(values) < 2:
            raise ValueError("No data found in the sheet (need at least header + 1 row).")

        df = pd.DataFrame(values[1:], columns=values[0])

        if project_filter is None:
            project_filter = "AIPPL_JAIGAD"

        filtered_df = df[df["Project"] == project_filter]
        aroor_df = df[df["Project"] == "ABL_AROOR-THURAVOOR_KERALA"]
        jaigad_data = df[df["Project"] == "AIPPL_JAIGAD"]
        gaimukh_df = df[df["Project"] == "AIPPL_GAIMUKH"]

        sh2 = gc.open("SCRIPT FOR DATA ")
        ws2 = sh2.worksheet("Sheet3")
        ws3 = sh2.worksheet("Sheet4")

        ws2.clear()
        set_with_dataframe(ws2, filtered_df)  # Sheet3: Dynamic filter
        ws3.clear()
        set_with_dataframe(ws3, gaimukh_df)  # Sheet4: Gaimukh

        return {
            "total_rows": len(df),
            "filtered_project": project_filter,
            "filtered_count": len(filtered_df),
            "aroor_count": len(aroor_df),
            "jaigad_count": len(jaigad_data),
            "gaimukh_count": len(gaimukh_df),
            "status": "success"
        }
    
    except (SpreadsheetNotFound, WorksheetNotFound) as e:
        raise ValueError(f"Sheet/worksheet not found: {str(e)}")
    except APIError as e:
        raise ValueError(f"Google Sheets API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}")