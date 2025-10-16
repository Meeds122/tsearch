import requests
from bs4 import BeautifulSoup
import os

# Headers with User-Agent to comply with Wikipedia API policy
HEADERS = {
    'User-Agent': 'WikipediaScraper/1.0 (https://example.com/contact; your.email@example.com)'
}

# Function to sanitize title for filename
def sanitize_filename(title):
    # Remove invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
       title = title.replace(char, '')
    # Replace spaces with underscores
    title = title.replace(' ', '_')
    # Limit length to avoid too long filenames
    title = title[:50]
    return title + '.txt'

# Function to get article titles from a Wikipedia category using API
def get_category_articles(category_title, limit=5):
    try:
        url = 'https://en.wikipedia.org/w/api.php'
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': f'Category:{category_title}',
            'cmtype': 'page',
            'cmlimit': limit,
            'format': 'json',
            'cmprop': 'title'
        }
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        if 'query' in data and 'categorymembers' in data['query']:
            for member in data['query']['categorymembers']:
                articles.append(member['title'])
        return articles
    except Exception as e:
        print(f"Error fetching category {category_title}: {e}")
        return []

# Function to get plain text from a Wikipedia article using API
def get_article_text(title):
    try:
        url = 'https://en.wikipedia.org/w/api.php'
        params = {
            'action': 'parse',
            'page': title,
            'prop': 'text',
            'format': 'json'
        }
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        if 'parse' in data and 'text' in data['parse']:
            soup = BeautifulSoup(data['parse']['text']['*'], 'html.parser')
            
            # Remove navigation and other non-content elements
            for element in soup(['script', 'style', 'nav', 'aside', 'footer']):
                element.decompose()
            
            # Get text from the entire soup
            text = soup.get_text(separator='\n', strip=True)
            return text
        else:
            return "No parse data found."
    except Exception as e:
        print(f"Error fetching article {title}: {e}")
        return ""

# Main script
def main():
    # Define categories
    cybersecurity_category = 'Computer security'
    programming_category = 'Programming'
    
    # List to keep track of created files
    created_files = []
    
    # Process cybersecurity articles
    cyber_titles = get_category_articles(cybersecurity_category, limit=500)
    for title in cyber_titles:
        text = get_article_text(title)
        filename = sanitize_filename(title)
        with open('data' + filename, 'w', encoding='utf-8') as f:
            f.write(f"=== {title} ===\n\n")
            f.write(text + "\n")
        created_files.append(filename)
        print(f"Created file: {filename} (length: {len(text)} chars)")
    
    # Process programming articles
    prog_titles = get_category_articles(programming_category, limit=500)
    for title in prog_titles:
        text = get_article_text(title)
        filename = sanitize_filename(title)
        with open('data/' + filename, 'w', encoding='utf-8') as f:
            f.write(f"=== {title} ===\n\n")
            f.write(text + "\n")
        created_files.append(filename)
        print(f"Created file: {filename} (length: {len(text)} chars)")
    
    print(f"\nTotal files created: {len(created_files)}")
    print("Files:", ', '.join(created_files))

if __name__ == "__main__":
    main()