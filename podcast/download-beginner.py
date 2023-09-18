import argparse
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import os
import time
from urllib.parse import unquote  # Importing this to decode the URL

import re

def format_filename(title):
    """
    Extracts the episode number from the title, removes leading #, formats it to have at least four digits,
    and adds an underscore between the episode number and the rest of the title.

    Args:
    - title (str): Original title from the h2 tag

    Returns:
    - str: Reformatted filename
    """
    # Remove the leading '#'
    title = title.replace("#", "", 1)

    # Extract the episode number using regex
    match = re.match(r'^(\d+)', title)
    if match:
        number_part = match.group(1)
        formatted_number = f"{int(number_part):04}"  # Format the number to have at least four digits
        title = title.replace(number_part, formatted_number + "_", 1)
    return title + ".mp3"

def file_already_exists(file_path):
    """Checks if the file already exists and is not empty."""
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

def fetch_content_from_page(base_url, page_num, headers):
    """Fetches content from a specified page and returns the soup object."""
    url = f"{base_url}/page/{page_num}/"
    print(f"Fetching content from {url}...")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f"Successfully fetched content from page {page_num}.")
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching page {page_num}: {e}")
        return None

def download_audio(file_path, audio_url, headers, delay):
    """Downloads a single audio."""
    print(f"Preparing to download {file_path}...")
    try:
        with requests.get(audio_url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as file:
                for chunk in r.iter_content(chunk_size=8192):
                    file.write(chunk)
        print(f"{file_path} downloaded successfully!")
    except requests.RequestException as e:
        print(f"Error downloading {file_path}: {e}")

    print(f"Waiting for {delay} seconds before next download...")
    time.sleep(delay)

def get_articles_from_page(soup):
    """Extracts articles from the soup object."""
    return soup.find_all("article", {"class": re.compile(r"post type-post")})

def get_audio_details_from_article(article):
    """Extracts audio details from a single article."""
    audio_tag = article.find("audio", {"class": "wp-audio-shortcode"})
    title_tag = article.find("h2")
    if not audio_tag or not title_tag:
        return None, None

    title = title_tag.text.strip()
    file_name = format_filename(title)
    source_tag = audio_tag.find("source")

    if source_tag and 'src' in source_tag.attrs:
        audio_url = source_tag['src']
        return file_name, audio_url
    return None, None

def process_page_articles(articles, save_path, headers, delay):
    """Processes the articles on a page and downloads necessary audios."""
    for article in articles:
        file_name, audio_url = get_audio_details_from_article(article)
        if not file_name or not audio_url:
            continue

        file_path = os.path.join(save_path, file_name)

        if file_already_exists(file_path):
            print(f"{file_name} already exists and is not empty. Skipping download.")
            continue

        download_audio(file_path, audio_url, headers, delay)

def download_audios(base_url, save_path, first_page, last_page, delay):
    print("Initializing audio download...")
    ua = UserAgent()

    if not os.path.exists(save_path):
        os.makedirs(save_path)
        print(f"Directory {save_path} created.")
    else:
        print(f"Directory {save_path} already exists.")

    headers = {
        'User-Agent': ua.random
    }

    for page_num in range(last_page, first_page - 1, -1):
        soup = fetch_content_from_page(base_url, page_num, headers)
        if not soup:
            continue

        articles = get_articles_from_page(soup)
        mp3_links_count = len([article.find("audio", {"class": "wp-audio-shortcode"}) for article in articles if article.find("audio", {"class": "wp-audio-shortcode"})])
        print(f"Found {mp3_links_count} .mp3 links on page {page_num}.")

        process_page_articles(articles, save_path, headers, delay)

    print("Finished downloading audios.")

if __name__ == '__main__':
    print("Starting script...")

    parser = argparse.ArgumentParser(description="Download audios from WordPress website")
    parser.add_argument("--baseUrl", type=str, required=True,
                        help="Base URL of the website (e.g. https://original.nihongoconteppei.com)")
    parser.add_argument("--savePath", type=str, required=True, help="Path to save the downloaded audio files")
    parser.add_argument("--firstPage", type=int, required=True, help="Starting page number")
    parser.add_argument("--lastPage", type=int, required=True, help="Last page number")
    parser.add_argument("--delay", type=int, required=True, help="Delay in seconds after each file download")

    args = parser.parse_args()
    print(
        f"Arguments received: baseUrl={args.baseUrl}, savePath={args.savePath}, firstPage={args.firstPage}, lastPage={args.lastPage}, delay={args.delay}")

    download_audios(args.baseUrl, args.savePath, args.firstPage, args.lastPage, args.delay)
