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
        sh = gc.open("BTS_10_NEW")
        worksheet = sh.worksheet("PBT10")
        values = worksheet.get_all_values()

        if len(values) < 2:
            raise ValueError("No data found in sheet (need header + 1 row)")

        df = pd.DataFrame(values[7:], columns=values[0])
        df["Project"] = df["Project"].astype(str).str.strip()  # remove spaces

        # ✅ Filter projects
        aroor_df = df[df["Project"] == "ABL_AROOR-THURAVOOR_KERALA"]
        jaigad_df = df[df["Project"] == "AIPPL_JAIGAD"]
        gaimukh_df = df[df["Project"] == "AIPPL_GAIMUKH"]

        # ✅ Write to target sheets
        sh2 = gc.open("LLP02756")
        ws2 = sh2.worksheet("BTS_10")
        aroor_df_sh3 = gc.open("LLP03275 RAHMAN QADAR")
        ws3 = aroor_df_sh3.worksheet("BTS_10")

        set_with_dataframe(ws2, jaigad_df, row=9,col=1)
        set_with_dataframe(ws3, aroor_df, row=9,col=1)

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
