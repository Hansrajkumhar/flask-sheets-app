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
        from google.oauth2.service_account import Credentials

        creds_json = os.getenv("GOOGLE_CREDENTIALS")
        if not creds_json:
            raise ValueError("GOOGLE_CREDENTIALS environment variable not set")

        creds_dict = json.loads(creds_json)  # parse string from env var
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)


        # ✅ Read source sheet
        sh = gc.open("BTS_10_NEW")
        worksheet = sh.worksheet("PBT10")
        values = worksheet.get_all_values()

        if len(values) < 2:
            raise ValueError("No data found in sheet (need header + 1 row)")

        # Row 8 = headers
        df = pd.DataFrame(values[8:], columns=values[7])
        df["Project"] = df["Project"].astype(str).str.strip()  # remove spaces

        # ✅ Filter projects
        aroor_df = df[df["Project"] == "ABL_AROOR-THURAVOOR_KERALA"]
        jaigad_df = df[df["Project"] == "AIPPL_JAIGAD"]
        gaimukh_df = df[df["Project"] == "AIPPL_GAIMUKH"]
        mumbai_df = df[df['Project'] == 'ABL_SBR9_CIDCO_NAVI MUMBAI']
        sheela_df = df[df['Project'] == 'ATIPL_SHEELA NAGAR_VISAKHAPATNAM']

        # ✅ Write to target spreadsheets
        jd_2756 = gc.open("LLP02756")
        jd_0127 = gc.open("LLP00127")
        gm_2941 = gc.open("LLP02941 - Pankaj Singh")
        sn_3273 = gc.open("LLP03273")
        nm_0981 = gc.open("LLP00981 - GANESH")
        ar_3275 = gc.open("LLP03275 RAHMAN QADAR")

        # ✅ Write to target sheets
        jd_BTS1_10 = jd_2756.worksheet("BTS_10")
        jd_BTS2_10 = jd_0127.worksheet("BTS_10")
        gm_BTS__10 = gm_2941.worksheet("BTS_10")
        sn_BTS__10 = sn_3273.worksheet("BTS_10")
        nm_BTS__10 = nm_0981.worksheet("BTS_10")    
        ar_BTS__10 = ar_3275.worksheet("BTS_10")

        set_with_dataframe(jd_BTS1_10, jaigad_df, row=9,col=1,include_column_header=False) # LLP02756
        set_with_dataframe(jd_BTS2_10, jaigad_df, row=9,col=1,include_column_header=False) # LLP00127
        set_with_dataframe(gm_BTS__10, gaimukh_df, row=9,col=1,include_column_header=False) # LLP02941
        set_with_dataframe(sn_BTS__10, sheela_df, row=9,col=1,include_column_header=False) # LLP03273
        set_with_dataframe(nm_BTS__10, mumbai_df, row=9,col=1,include_column_header=False) # LLP00981
        set_with_dataframe(ar_BTS__10, aroor_df, row=9,col=1,include_column_header=False) #LLP003275
        

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
