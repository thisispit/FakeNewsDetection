import requests
import os

def download_data():
    # URLs for ISOT Dataset (or compatible mirror)
    fake_url = "https://raw.githubusercontent.com/hosseindamavandi/Fake-News-Detection/main/Fake.csv"
    real_url = "https://raw.githubusercontent.com/hosseindamavandi/Fake-News-Detection/main/True.csv"
    
    # Ensure directory exists
    if not os.path.exists('dataset'):
        os.makedirs('dataset')

    urls = {
        "dataset/Fake.csv": fake_url,
        "dataset/True.csv": real_url
    }

    for file_path, url in urls.items():
        try:
            print(f"Downloading {file_path} from {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Saved {file_path}")
        except Exception as e:
            print(f"Failed to download {file_path}: {e}")

if __name__ == "__main__":
    download_data()