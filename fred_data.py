import pandas as pd
import numpy as np
from fredapi import Fred
import matplotlib.pyplot as plt

FRED_API_KEY = "0f3ca202b8d291c41c2cfc3d5c03dffc"
fred = Fred(api_key=FRED_API_KEY)

# Function to pull data from FRED
def fetch_fred_data(series_id, start_date, end_date):
    print(f"Fetching {series_id} data...")
    return fred.get_series(series_id, observation_start=start_date, observation_end=end_date)

# Define the date range for analysis
start_date = "2000-01-01"
end_date = "2025-01-01"

# Fetch CPI data
cpi = fetch_fred_data("CPIAUCSL", start_date, end_date)  # CPI for All Urban Consumers
cpi = cpi.to_frame(name="CPI").reset_index()
cpi.columns = ["Date", "CPI"]

# Fetch 2-Year Treasury Yield
two_year_yield = fetch_fred_data("DGS2", start_date, end_date)  # 2-Year Treasury Yield
two_year_yield = two_year_yield.to_frame(name="2Y Nominal Yield").reset_index()
two_year_yield.columns = ["Date", "2Y Nominal Yield"]

# Fetch 10-Year Treasury Yield
ten_year_yield = fetch_fred_data("DGS10", start_date, end_date)  # 10-Year Treasury Yield
ten_year_yield = ten_year_yield.to_frame(name="10Y Nominal Yield").reset_index()
ten_year_yield.columns = ["Date", "10Y Nominal Yield"]

# Fetch 30-Year Treasury Yield
thirty_year_yield = fetch_fred_data("DGS30", start_date, end_date)  # 30-Year Treasury Yield
thirty_year_yield = thirty_year_yield.to_frame(name="30Y Nominal Yield").reset_index()
thirty_year_yield.columns = ["Date", "30Y Nominal Yield"]

# Fetch 10-Year TIPS Yield
tips_yield = fetch_fred_data("DFII10", start_date, end_date)  # 10-Year TIPS Yield
tips_yield = tips_yield.to_frame(name="10Y TIPS Yield").reset_index()
tips_yield.columns = ["Date", "10Y TIPS Yield"]

# Fetch 5-Year Breakeven Inflation Rate
five_year_breakeven = fetch_fred_data("T5YIE", start_date, end_date)  # 5-Year Breakeven Inflation
five_year_breakeven = five_year_breakeven.to_frame(name="5Y Breakeven Inflation").reset_index()
five_year_breakeven.columns = ["Date", "5Y Breakeven Inflation"]

# Fetch 10-Year Breakeven Inflation Rate
ten_year_breakeven = fetch_fred_data("T10YIE", start_date, end_date)  # 10-Year Breakeven Inflation
ten_year_breakeven = ten_year_breakeven.to_frame(name="10Y Breakeven Inflation").reset_index()
ten_year_breakeven.columns = ["Date", "10Y Breakeven Inflation"]

# Merge all data
data = pd.merge(cpi, ten_year_yield, on="Date", how="outer")
data = pd.merge(data, tips_yield, on="Date", how="outer")
data = pd.merge(data, two_year_yield, on="Date", how="outer")
data = pd.merge(data, thirty_year_yield, on="Date", how="outer")
data = pd.merge(data, five_year_breakeven, on="Date", how="outer")
data = pd.merge(data, ten_year_breakeven, on="Date", how="outer")

# Calculate additional metrics
data["Breakeven Inflation (10Y)"] = data["10Y Nominal Yield"] - data["10Y TIPS Yield"]
data["Real Yield (10Y)"] = data["10Y Nominal Yield"] - (data["CPI"].pct_change(periods=12) * 100)  # Annualized Inflation Rate

# Sort data by Date in descending order
data = data.sort_values(by="Date", ascending=False)

# Save to CSV with the most recent date at the top
data.to_csv("cpi_yield_data.csv", index=False)

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(data["Date"], data["2Y Nominal Yield"], label="2Y Nominal Yield", linestyle="--")
plt.plot(data["Date"], data["10Y Nominal Yield"], label="10Y Nominal Yield", linestyle="-")
plt.plot(data["Date"], data["30Y Nominal Yield"], label="30Y Nominal Yield", linestyle="-.")
plt.plot(data["Date"], data["5Y Breakeven Inflation"], label="5Y Breakeven Inflation")
plt.plot(data["Date"], data["10Y Breakeven Inflation"], label="10Y Breakeven Inflation")
plt.xlabel("Date")
plt.ylabel("Rate (%)")
plt.title("Treasury Yields and Breakeven Inflation Rates")
plt.legend()
plt.grid()
plt.show()
