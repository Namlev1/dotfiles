#!/usr/bin/env python3
import os
import re
import sys
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import shutil

# AnkiConnect configuration
ANKI_CONNECT_URL = "http://localhost:8765"
DECK_NAME = "English::Vocabulary"
MODEL_NAME = "Basic and reversed with image"

def invoke_anki_connect(action, **params):
    """Call AnkiConnect API."""
    request = {
        "action": action,
        "version": 6,
        "params": params
    }
    
    response = requests.post(ANKI_CONNECT_URL, json=request)
    response_data = response.json()
    
    if response_data.get("error"):
        print(f"AnkiConnect error: {response_data['error']}")
        return None
    
    return response_data.get("result")

def extract_cambridge_data(url):
    """Extract word data from Cambridge Dictionary."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        sys.exit(1)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the word
    word_elem = soup.select_one('.hw.dhw')
    word = word_elem.text.strip() if word_elem else "Word not found"
    
    # Extract IPA (American pronunciation)
    ipa_elems = soup.select('.dpron-i .ipa')
    ipa = ""
    
    # Look for US pronunciation specifically
    for i, elem in enumerate(soup.select('.dpron-i')):
        region = elem.select_one('.region.dreg')
        if region and 'us' in region.text.lower():
            ipa_elem = elem.select_one('.ipa')
            if ipa_elem:
                ipa = ipa_elem.text.strip()
                break
    
    # If no US pronunciation found, take the first IPA
    if not ipa and ipa_elems:
        ipa = ipa_elems[0].text.strip()
    
    # Extract definition
    def_elem = soup.select_one('.def.ddef_d.db')
    definition = def_elem.text.strip() if def_elem else "Definition not found"
    
    # Extract the first example sentence for Personal Connection field
    example_elem = soup.select_one('.examp.dexamp')
    example = ""
    if example_elem:
        example = example_elem.text.strip()
    
    # Find the audio URL - based on the HTML structure you shared
    audio_url = None
    base_url = "https://dictionary.cambridge.org"
    
    # Look for audio sources in <source> tags
    audio_sources = []
    audio_elements = soup.select('source[type="application/ogg"], source[type="audio/ogg"]')
    for source in audio_elements:
        src = source.get('src')
        if src:
            audio_sources.append(src)
    
    # Look for video elements that might contain the audio
    video_elements = soup.select('video source')
    for source in video_elements:
        src = source.get('src')
        if src:
            audio_sources.append(src)
    
    # Also search for any .ogg files in the page source (fallback)
    if not audio_sources:
        ogg_pattern = r'src=["\']((?:/|https?:)[^"\']+\.ogg)["\']'
        matches = re.findall(ogg_pattern, response.text)
        audio_sources.extend(matches)
    
    # Print found audio sources
    print(f"Found {len(audio_sources)} potential audio sources:")
    for i, source in enumerate(audio_sources):
        print(f"  {i}: {source}")
    
    # Prioritize US pronunciation if available
    for source in audio_sources:
        if 'us_pron' in source.lower():
            audio_url = source
            print(f"Selected US pronunciation URL: {audio_url}")
            break
    
    # If no US pronunciation, take the first one
    if not audio_url and audio_sources:
        audio_url = audio_sources[0]
        print(f"Selected audio URL: {audio_url}")
    
    return {
        'word': word,
        'ipa': ipa,
        'explanation': definition,
        'example': example,
        'audio_url': audio_url,
        'base_url': base_url
    }

def download_pronunciation(audio_url, word, base_url="https://dictionary.cambridge.org"):
    """Download the pronunciation file to the specified location."""
    if not audio_url:
        print("No pronunciation URL found")
        return None
    
    # Ensure the directory exists
    download_dir = os.path.expanduser("~/Downloads/tmp")
    os.makedirs(download_dir, exist_ok=True)
    
    # Create the full file path
    file_path = os.path.join(download_dir, f"{word}.ogg")
    
    # Fix URL if it's not a complete URL
    if audio_url.startswith('//'):
        audio_url = 'https:' + audio_url
    elif audio_url.startswith('/'):
        # It's a path from the root of the site
        audio_url = base_url + audio_url
    
    print(f"Downloading from URL: {audio_url}")
    
    # Set up headers with referrer to the dictionary page
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Referer': f"{base_url}/dictionary/english/{word}"
    }
    
    try:
        # Use a session to maintain cookies and headers
        session = requests.Session()
        # First visit the dictionary page to get cookies
        session.get(f"{base_url}/dictionary/english/{word}", headers=headers)
        
        # Then download the audio file
        audio_response = session.get(audio_url, headers=headers, stream=True)
        audio_response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in audio_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Check if file was downloaded successfully
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:  # Ensure it's not an empty or error page
            print(f"Pronunciation downloaded to: {file_path}")
            return file_path
        else:
            print("Warning: Downloaded file seems too small, might not be valid audio")
    except Exception as e:
        print(f"Error downloading pronunciation: {e}")
    
    # If we reach here, the download failed with requests
    # Try using curl as a fallback
    try:
        import subprocess
        print("Attempting download with curl...")
        
        curl_cmd = [
            'curl', '-L', '-o', file_path,
            '-H', f'User-Agent: {headers["User-Agent"]}',
            '-H', f'Referer: {headers["Referer"]}',
            audio_url
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
            print(f"Successfully downloaded audio using curl to: {file_path}")
            return file_path
    except Exception as e:
        print(f"Error with curl: {e}")
    
    print("Could not download the audio file")
    return None

def add_to_anki(data, audio_path):
    """Add the note to Anki using AnkiConnect."""
    # Check if AnkiConnect is available
    try:
        version = invoke_anki_connect("version")
        if not version:
            print("Error: Cannot connect to AnkiConnect. Make sure Anki is running with AnkiConnect add-on installed.")
            return False
    except:
        print("Error: Cannot connect to AnkiConnect. Make sure Anki is running with AnkiConnect add-on installed.")
        return False
    
    # Add media file to Anki if available
    filename = None
    if audio_path:
        filename = os.path.basename(audio_path)
        with open(audio_path, "rb") as file:
            media_bytes = file.read()
        
        # Convert to base64 for AnkiConnect
        import base64
        media_b64 = base64.b64encode(media_bytes).decode("utf-8")
        
        # Store file in Anki media collection
        result = invoke_anki_connect("storeMediaFile", filename=filename, data=media_b64)
        if not result:
            print("Warning: Failed to store audio file in Anki")
    
    # Create note with example sentence in Personal Connection field
    note = {
        "deckName": DECK_NAME,
        "modelName": MODEL_NAME,
        "fields": {
            "Word": data["word"],
            "IPA": data["ipa"],
            "Explanation": data["explanation"],
            "Personal Connection": data.get("example", ""),  # Use example sentence or empty string
            "Pronunciation": f"[sound:{filename}]" if filename else ""
        },
        "options": {
            "allowDuplicate": False
        },
        "tags": ["auto_cambridge"]
    }
    
    # Add note to Anki
    result = invoke_anki_connect("addNote", note=note)
    
    if result:
        print(f"Note added successfully to Anki with ID: {result}")
        return True
    else:
        print("Failed to add note to Anki. It might be a duplicate.")
        
        # Get the list of fields from the model to help with debugging
        fields_list = invoke_anki_connect("modelFieldNames", modelName=MODEL_NAME)
        if fields_list:
            print(f"Available fields for '{MODEL_NAME}' note type: {fields_list}")
            print("Make sure your script uses these exact field names.")
        
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python cambridge_to_anki_direct.py <cambridge_dictionary_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Validate URL
    if not url.startswith('https://dictionary.cambridge.org/dictionary/english/'):
        print("Please provide a valid Cambridge Dictionary URL")
        sys.exit(1)
    
    # Extract data
    print(f"Extracting data from {url}...")
    data = extract_cambridge_data(url)
    
    # Download pronunciation
    audio_path = None
    if data['audio_url']:
        print(f"Downloading pronunciation...")
        audio_path = download_pronunciation(data['audio_url'], data['word'], data['base_url'])
    
    # Print the extracted data
    print("\nExtracted data:")
    print(f"Word: {data['word']}")
    print(f"IPA: {data['ipa']}")
    print(f"Explanation: {data['explanation']}")
    print(f"Example: {data.get('example', 'Not found')}")
    print(f"Audio: {'Found' if audio_path else 'Not found'}")
    
    # Add to Anki
    print("\nAdding to Anki...")
    success = add_to_anki(data, audio_path)
    
    if success:
        print("\nCard added successfully to your Anki deck!")
    else:
        print("\nFailed to add card to Anki. See errors above.")

if __name__ == "__main__":
    main()
