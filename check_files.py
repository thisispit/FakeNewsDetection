import pandas as pd
import os

files = ['dataset/Fake.csv', 'dataset/True.csv']
for f in files:
    if os.path.exists(f):
        try:
            df = pd.read_csv(f)
            print(f"Successfully read {f}. Columns: {list(df.columns)}")
            print(f"Shape: {df.shape}")
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print(f"File not found: {f}")
