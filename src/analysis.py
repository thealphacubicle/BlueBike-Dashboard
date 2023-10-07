"""
Does the data cleaning and data preperation for the dashboard
DS3500 HW2
Authors: Srihari Raman & Reema Sharma
"""

import pandas as pd

#TODO: Clean dataset and store back in data folder
df = pd.read_csv("https://raw.githubusercontent.com/thealphacubicle/MBTA-Dashboard/main/src/data/mbta_cr_data.csv")
print(df.isna().sum())
df = df.dropna()

print("\nPost-processing data shape:" ,df.shape)
df.to_csv('./data/cleaned_mbta_data.csv')





