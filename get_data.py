#======== DO NOT ADD THIS FILE TO GIT =========
#%%
import eikon as ek
from fredapi import Fred
import requests
import prettytable
import json
from typing import List
import pandas as pd
#%%
#%%

url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
seriesids = ['CUSR0000SA0L12E']

#%%
def get_bls_data(url: str, seriesids: List[str], startyear: int, endyear: int):
    headers = {'Content-Type': 'application/json'}
    # Prepare the API request payload
    data = json.dumps({
        'seriesid': seriesids,
        'startyear': str(startyear),
        'endyear': str(endyear)
    })

    # Send the request to the BLS API
    response = requests.post(url, headers=headers, data=data)

    # Parse the JSON response
    json_data = json.loads(response.text)
    df = pd.json_normalize(
        json_data["Results"]["series"],
        record_path=["data"],
        meta=["seriesID"],
        record_prefix=""
    )

    df.rename(columns={"seriesID": "series_id", "period": "month", "periodName": "month_name"}, inplace=True)
    df["value"] = df["value"].astype(float)  # Convert value to float
    df["date"] = pd.to_datetime(df["year"] + "-" + df["month"].str[1:], format='%Y-%m')
    return df




