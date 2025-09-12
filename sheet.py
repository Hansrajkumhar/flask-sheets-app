import os
import json
import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe

def process_projects():
    """
    Process Google Sheets data exactly like your local script:
    - Reads "Test_BTS_10" → "Sheet1"
    - Filters by project names
    - Writes filtered data to "SCRIPT FOR DATA" sheets
    - Returns counts
    """
    try:
        # ✅ Authenticate using service account JSON
        creds_json = os.getenv("GOOGLE_CREDENTIALS")
        if not creds_json:
            raise ValueError("GOOGLE_CREDENTIALS environment variable not set")

        creds_path = "/tmp/temp_credentials.json"
        with open(creds_path, "w") as f:
            json.dump(json.loads(creds_json), f)
        gc = gspread.service_account(filename=creds_path)

        # ✅ Read source sheet
        sh = gc.open("Test_BTS_10")
        worksheet = sh.worksheet("Sheet1")
        values = worksheet.get_all_values()

        if len(values) < 2:
            raise ValueError("No data found in sheet (need header + 1 row)")

        df = pd.DataFrame(values[1:], columns=values[0])
        df["Project"] = df["Project"].astype(str).str.strip()  # remove spaces

        # ✅ Filter projects
        aroor_df = df[df["Project"] == "ABL_AROOR-THURAVOOR_KERALA"]
        jaigad_df = df[df["Project"] == "AIPPL_JAIGAD"]
        gaimukh_df = df[df["Project"] == "AIPPL_GAIMUKH"]

        # ✅ Write to target sheets
        sh2 = gc.open("SCRIPT FOR DATA ")
        ws2 = sh2.worksheet("Sheet3")
        ws3 = sh2.worksheet("Sheet4")

        set_with_dataframe(ws2, jaigad_df)
        set_with_dataframe(ws3, gaimukh_df)

        # ✅ Return summary
        return {
            "total_rows": len(df),
            "aroor_count": len(aroor_df),
            "jaigad_count": len(jaigad_df),
            "gaimukh_count": len(gaimukh_df),
            "status": "success"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
