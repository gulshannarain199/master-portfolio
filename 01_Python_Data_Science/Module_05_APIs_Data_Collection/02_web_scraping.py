# ==============================================================================
# COURSE: IBM Python for Data Science, AI & Development
# MODULE: Module 5 - APIs and Data Collection
# TOPIC:  REST APIs, Web Scraping, and Working with Files
# ==============================================================================

import requests
from bs4 import BeautifulSoup

# --- 1. Fetching Web Page HTML ---
print("--- 1. FETCHING HTML FROM A WEBSITE ---")
# Using a safe, public example website for scraping practice
url = "https://example.com"
response = requests.get(url)

print(f"Target URL: {url}")
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    html_content = response.text
    
    # --- 2. Parsing HTML with BeautifulSoup ---
    print("\n--- 2. PARSING HTML TAGS ---")
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract the title tag
    page_title = soup.title.string
    print(f"Extracted Page Title: {page_title}")
    
    # Extract all paragraph texts
    print("\n--- 3. EXTRACTING PARAGRAPHS ---")
    paragraphs = soup.find_all("p")
    for i, p in enumerate(paragraphs, 1):
        print(f"Paragraph {i}: {p.get_text()}")