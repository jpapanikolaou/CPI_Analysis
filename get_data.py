#======== DO NOT ADD THIS FILE TO GIT =========
#%%
import eikon as ek
from fredapi import Fred
import requests
import prettytable
import json
from typing import List
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env file
api_key = os.getenv("BLS_API_KEY")
#%%

url = 'https://api.bls.gov/publicAPI/v1/timeseries/data/'
seriesids = ['CUUR0000SA0']

#%%


def fetch_bls_data_V2(series_ids, start_year, end_year, api_key=None):
    d = {"seriesid": series_ids, "startyear": str(start_year), "endyear": str(end_year)}
    if api_key: d["registrationkey"] = api_key
    r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/",
                      headers={"Content-Type": "application/json"},
                      data=json.dumps(d)).json()
    return pd.json_normalize(r["Results"]["series"], record_path="data", meta="seriesID")

def save_data_to_memory(df, filename, directory="bls_data"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved: {filepath}")


#%%

#%% Process and clean the dataframe and refine into tickers

series_names_df = pd.read_csv('series_names.csv')
series_names_df.columns = series_names_df.iloc[0,:]

series_names_df["begin_year"] = pd.to_numeric(series_names_df["begin_year"], errors='coerce')
series_names_df["end_year"] = pd.to_numeric(series_names_df["end_year"], errors='coerce')
series_names_df = series_names_df[series_names_df["end_year"]==2024]
series_names_df = series_names_df.iloc[1:]
series_tickers = series_names_df.iloc[:,1].tolist() #some weird error means we don't get tickers \_:/_/
series_names = series_names_df['series_title'].values
series_names_df.to_csv("series_names_df_filtered.csv")

#%% due to BLS API usage limtits, we can only pull 500 time series a day. we sort on keywords, which is not ideal...
series_df = pd.read_csv('series_names_df_filtered.csv')
series_df.columns = series_df.columns.str.strip()
series_df = series_df[['series_id', 'series_title', 'begin_year', 'end_year']]
priority_keywords = ['All items', 'Energy', 'Housing', 'Transportation', 'Medical', 'Education']
series_df['priority'] = series_df['series_title'].apply(lambda x: sum(kw in x for kw in priority_keywords))

# Sort by priority, then by longest time range (end_year - begin_year), and select top 450
salient_series = series_df.sort_values(by=['priority', 'end_year', 'begin_year'], ascending=[False, False, True]).head(380)

salient_tickers = salient_series['series_id'].values.tolist()

#%% pull the data from the BLS and save to memory


batch_size = 49
start_year = 2007
end_year = 2024

data_list = []
df_list = []
for i in range(0, len(salient_tickers), batch_size):
    batch_tickers = salient_tickers[i:i + batch_size]
    print(f"Fetching data for batch {i // batch_size + 1}...")

    # Fetch data from BLS
    bls_response = fetch_bls_data_V2(batch_tickers, start_year, end_year, api_key)
    data_list.append(bls_response)

    # Process and save results
    if "Results" in bls_response and "series" in bls_response["Results"]:
        for series in bls_response["Results"]["series"]:
            series_id = series["seriesID"]
            df_series = pd.DataFrame(series["data"])
            df_series["seriesID"] = series_id  # Add series ID column
            df_list.append(df_series)
    else:
        print("ERROR")
        print(bls_response)

        # Combine all series data into a single DataFrame and save
        if df_list:
            combined_df = pd.concat(df_list, ignore_index=True)
            save_data_to_memory(combined_df, f"bls_data_batch_{i // batch_size + 1}.csv")

print("Data collection complete!")
