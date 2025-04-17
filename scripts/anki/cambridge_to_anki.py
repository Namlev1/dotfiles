#!/usr/bin/env python3
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

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
    ipa_elem = soup.select_one('.dpron-i .ipa')
    ipa = ipa_elem.text.strip() if ipa_elem else "IPA not found"
    
    # Extract definition
    def_elem = soup.select_one('.def.ddef_d.db')
    definition = def_elem.text.strip() if def_elem else "Definition not found"
    
    # Find the pronunciation file URL
    # Looking specifically for American pronunciation
    audio_sources = []
    
    # First, search for the audio elements with US pronunciation
    audio_sections = soup.select('.dpron-i')
    us_section = None
    
    for section in audio_sections:
        region_label = section.select_one('.region.dreg')
        if region_label and 'us' in region_label.text.lower():
            us_section = section
            break
    
    if us_section:
        audio_buttons = us_section.select('.daud audio source')
        for source in audio_buttons:
            if source.get('type') == 'audio/ogg':
                audio_sources.append(source.get('src'))
    
    # If not found via structured approach, try finding all .ogg files (fallback)
    if not audio_sources:
        ogg_pattern = r'https://[^"\']+\.ogg'
        audio_sources = re.findall(ogg_pattern, response.text)
    
    # Take the second .ogg result if available, otherwise the first one
    audio_url = None
    if len(audio_sources) >= 2:
        audio_url = audio_sources[1]
    elif audio_sources:
        audio_url = audio_sources[0]
        
    return {
        'word': word,
        'ipa': ipa,
        'explanation': definition,
        'audio_url': audio_url
    }

def download_pronunciation(audio_url, word):
    """Download the pronunciation file to the specified location."""
    if not audio_url:
        print("No pronunciation URL found")
        return None
    
    # Ensure the directory exists
    download_dir = os.path.expanduser("~/Downloads/tmp")
    os.makedirs(download_dir, exist_ok=True)
    
    # Create the full file path
    file_path = os.path.join(download_dir, f"{word}.ogg")
    
    # Fix URL if it's a relative URL
    if audio_url.startswith('//'):
        audio_url = 'https:' + audio_url
    
    try:
        audio_response = requests.get(audio_url, stream=True)
        audio_response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in audio_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Pronunciation downloaded to: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error downloading pronunciation: {e}")
        return None

def format_for_anki(data, audio_path):
    """Format the data for Anki import."""
    result = {
        'Word': data['word'],
        'IPA': data['ipa'],
        'Explanation': data['explanation'],
        'Personal Connection': "",  # Left blank for user to fill in
        'Pronunciation': f"[sound:{os.path.basename(audio_path)}]" if audio_path else ""
    }
    
    return result

def main():
    if len(sys.argv) != 2:
        print("Usage: python cambridge_to_anki.py <cambridge_dictionary_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Validate URL
    if not url.startswith('https://dictionary.cambridge.org/dictionary/english/'):
        print("Please provide a valid Cambridge Dictionary URL")
        sys.exit(1)
    
    # Extract data
    data = extract_cambridge_data(url)
    
    # Download pronunciation
    audio_path = None
    if data['audio_url']:
        audio_path = download_pronunciation(data['audio_url'], data['word'])
    
    # Format for Anki
    anki_data = format_for_anki(data, audio_path)
    
    # Print the results
    print("\nData extracted for Anki:")
    print(f"Word: {anki_data['Word']}")
    print(f"IPA: {anki_data['IPA']}")
    print(f"Explanation: {anki_data['Explanation']}")
    print(f"Pronunciation file: {audio_path if audio_path else 'Not found'}")
    
    # Optionally output to a file for Anki import
    output_file = os.path.expanduser(f"~/Downloads/tmp/{data['word']}_anki.txt")
    with open(output_file, 'w') as f:
        f.write(f"Word: {anki_data['Word']}\n")
        f.write(f"IPA: {anki_data['IPA']}\n")
        f.write(f"Explanation: {anki_data['Explanation']}\n")
        f.write(f"Pronunciation: {anki_data['Pronunciation']}\n")
    
    print(f"\nAnki data saved to: {output_file}")
    print("\nYou can now import this data into your Anki deck.")

if __name__ == "__main__":
    main()
