
import requests
import os
from urllib.parse import urlparse

# === CONFIGURATION ===
PEXELS_API_KEY = '5FzMZUULMwQoOnvn1itufawula58pfENXanxX9NFFg2eiCdkG1fNvmGN'  # Replace with your API key
QUERY = 'hotel room'
NUM_IMAGES = 100
SAVE_DIR = 'hotel_images'

# === SETUP ===
os.makedirs(SAVE_DIR, exist_ok=True)
headers = {
    'Authorization': PEXELS_API_KEY
}
per_page = 30
pages = (NUM_IMAGES // per_page) + 1

image_count = 0

for page in range(1, pages + 1):
    url = f'https://api.pexels.com/v1/search?query={QUERY}&per_page={per_page}&page={page}'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch from API: {response.status_code}")
        break

    data = response.json()
    for photo in data['photos']:
        image_url = photo['src']['large2x']
        image_name = os.path.basename(urlparse(image_url).path)
        image_path = os.path.join(SAVE_DIR, image_name)

        img_data = requests.get(image_url).content
        with open(image_path, 'wb') as f:
            f.write(img_data)
            image_count += 1
            print(f"Downloaded: {image_name}")

        if image_count >= NUM_IMAGES:
            break

    if image_count >= NUM_IMAGES:
        break

print(f"\n✅ Downloaded {image_count} images to '{SAVE_DIR}'")
