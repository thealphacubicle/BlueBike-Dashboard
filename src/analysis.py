import pandas as pd

def main():
    df = pd.read_csv("bluebikes_tripdata.csv")
    print(df.shape)
    df = df.iloc[:150000:]
    df.to_csv('bluebike_trunc.csv', index=False)



main()
