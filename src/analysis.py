import pandas as pd

#TODO: Clean dataset
df = pd.read_csv('/Users/srihariraman/PycharmProjects/DS3500/HW/HW2/data/mbta_cr_data.csv')
print("\nBeginning shape:", df.shape, "\n")
print(df.isna().sum())
df = df.dropna()

print("\nPost-processing shape:" ,df.shape)
df.to_csv("/Users/srihariraman/PycharmProjects/DS3500/HW/HW2/data/cleaned_mbta_cr_data.csv")



