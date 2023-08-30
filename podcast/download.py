import requests
from bs4 import BeautifulSoup
import os
import argparse
import time

def download_audios(base_url, save_path, first_page, last_page, delay):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    for page_num in range(first_page, last_page+1):
        url = f"{base_url}/page/{page_num}/"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the download link for each podcast entry
        for article in soup.find_all('article'):
            download_link = article.select_one('.share-icon.download a')
            if download_link:
                audio_url = download_link['href']
                file_name = os.path.basename(audio_url)
                print(f"Downloading {file_name}...")

                try:
                    with requests.get(audio_url, stream=True) as r:
                        r.raise_for_status()
                        with open(os.path.join(save_path, file_name), 'wb') as file:
                            for chunk in r.iter_content(chunk_size=8192):
                                file.write(chunk)
                    print(f"{file_name} downloaded successfully!")
                except requests.RequestException as e:
                    print(f"Error downloading {file_name}: {e}")

                # Wait for specified delay time after downloading a file
                time.sleep(delay)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download audios from WordPress website")
    parser.add_argument("--baseUrl", type=str, required=True, help="Base URL of the website (e.g. https://original.nihongoconteppei.com)")
    parser.add_argument("--savePath", type=str, required=True, help="Path to save the downloaded audio files")
    parser.add_argument("--firstPage", type=int, required=True, help="Starting page number")
    parser.add_argument("--lastPage", type=int, required=True, help="Last page number")
    parser.add_argument("--delay", type=int, required=True, help="Delay in seconds after each file download")

    args = parser.parse_args()

    download_audios(args.baseUrl, args.savePath, args.firstPage, args.lastPage, args.delay)
