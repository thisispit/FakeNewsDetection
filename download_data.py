import requests
import pandas as pd
import io
import os

def download_and_merge():
    # Links for Politifact data (KaiDMML/FakeNewsNet)
    fake_url = "https://raw.githubusercontent.com/KaiDMML/FakeNewsNet/master/dataset/politifact_fake.csv"
    real_url = "https://raw.githubusercontent.com/KaiDMML/FakeNewsNet/master/dataset/politifact_real.csv"
    
    if not os.path.exists('dataset'):
        os.makedirs('dataset')
        
    try:
        print("Downloading Fake news data...")
        f_resp = requests.get(fake_url)
        f_resp.raise_for_status()
        df_fake = pd.read_csv(io.StringIO(f_resp.text))
        df_fake['label'] = 'FAKE'
        
        print("Downloading Real news data...")
        r_resp = requests.get(real_url)
        r_resp.raise_for_status()
        df_real = pd.read_csv(io.StringIO(r_resp.text))
        df_real['label'] = 'REAL'
        
        # Merge
        print("Merging datasets...")
        df_total = pd.concat([df_fake, df_real], ignore_index=True)
        
        # The Politifact dataset uses 'title' for the headline.
        # It doesn't always have full text in the CSV (it has URLs), 
        # but for this demo, we will use 'title' as the content to train on.
        df_total['text'] = df_total['title'] 
        
        output_path = "dataset/news.csv"
        df_total.to_csv(output_path, index=False)
        print(f"Saved {len(df_total)} rows to {output_path}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    download_and_merge()