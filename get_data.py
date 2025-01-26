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

url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
seriesids = ['CUUR0000SA0']

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


#%%

series_names_df = pd.read_csv('series_names.csv')
series_names_df.columns = series_names_df.iloc[0,:]
series_names_df = series_names_df.iloc[1:]
series_tickers = series_names_df.iloc[:,1].values #some weird error means we don't get tickers \_:/_/
series_names = series_names_df['series_title'].values

#%%
def do_bls_query(url: str,series_tickers: List[str], startyear: int, endyear: int):
    series_df_dict = {}
    for series_id in series_tickers:
        try:
            series_df = get_bls_data(url, [series_id], startyear, endyear)
            series_df_dict[series_id] = series_df
        except Exception as e:
            print(f"error for seriesid {series_id}: {e}".format(series_id=series_id))
            continue
    return series_df_dict


#%%
series_tickers_local = series_tickers[0:5]

test_dict = do_bls_query(url,series_tickers_local,2020,2024)







