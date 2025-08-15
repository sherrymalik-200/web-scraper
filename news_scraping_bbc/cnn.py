import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import time
from urllib.parse import urlparse
import hashlib

# Define headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def get_cnn_news(save_images=True, fetch_content=True, max_articles=10):
    """
    Extract headlines from CNN's website with enhanced functionality:
    - Extracts headlines and links
    - Fetches article content (paragraphs)
    - Downloads and saves images
    - Creates organized folders
    
    Args:
        save_images (bool): Whether to download and save images
        fetch_content (bool): Whether to fetch the full article content
        max_articles (int): Maximum number of articles to scrape
        
    Returns:
        list: List of dictionaries containing article data
    """
    url = "https://www.cnn.com"
    
    # Create directory for saving data
    today = datetime.now().strftime("%Y%m%d")
    base_dir = f"_images_cnn_{today}"
    if save_images and not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    try:
        # Make request with headers and appropriate timeout
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find headline containers using multiple strategies
        headlines = []
        seen_urls = set()
        
        # Strategy 1: Find headline containers directly
        for container in soup.select('div[class*="headline"], span[class*="headline"], h3[class*="headline"]'):
            link_tag = container.find('a', href=True) or container.find_parent('a', href=True)
            if link_tag:
                text = container.get_text(strip=True)
                link = link_tag.get('href', '')
                if text and link and link not in seen_urls:
                    if link.startswith('/'):
                        link = f"https://www.cnn.com{link}"
                    
                    # Initialize article data dictionary
                    article_data = {
                        "headline": text,
                        "link": link,
                        "content": "",
                        "images": []
                    }
                    
                    headlines.append(article_data)
                    seen_urls.add(link)
        
        # Strategy 2: Find all article links by their URL pattern
        if len(headlines) < 3:
            for link_tag in soup.find_all('a', href=True):
                link = link_tag.get('href', '')
                text = link_tag.get_text(strip=True)
                
                # CNN articles typically include year in URL
                if (text and link and link not in seen_urls and 
                    ('/20' in link or 'article' in link) and 
                    not link.endswith('.jpg') and not link.endswith('.png')):
                    
                    if link.startswith('/'):
                        link = f"https://www.cnn.com{link}"
                    
                    # Ensure it's a CNN link
                    if 'cnn.com' in link:
                        article_data = {
                            "headline": text,
                            "link": link,
                            "content": "",
                            "images": []
                        }
                        
                        headlines.append(article_data)
                        seen_urls.add(link)
        
        # Limit to max_articles
        headlines = headlines[:max_articles]
        
        # Fetch article content and images if requested
        if fetch_content:
            for idx, article in enumerate(headlines):
                print(f"Fetching article {idx+1}/{len(headlines)}: {article['headline']}")
                
                try:
                    # Add a delay to avoid overwhelming the server
                    time.sleep(1)
                    
                    # Fetch article page
                    article_response = requests.get(article['link'], headers=HEADERS, timeout=15)
                    if article_response.status_code != 200:
                        print(f"  Error: Could not fetch article. Status code: {article_response.status_code}")
                        continue
                        
                    article_soup = BeautifulSoup(article_response.content, "html.parser")
                    
                    # Extract article content (paragraphs)
                    # Look for the main content area with multiple fallbacks
                    content_container = article_soup.select_one('div[class*="article__content"], div[class*="body"], div[class*="story-body"]')
                    if not content_container:
                        content_container = article_soup  # Fallback to the entire page
                    
                    # Extract paragraphs
                    paragraphs = content_container.find_all('p')
                    article_text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    article['content'] = article_text
                    
                    # Extract images if requested
                    if save_images:
                        # Find all images in the article
                        images = content_container.find_all('img', src=True)
                        
                        # Create article-specific directory (using a hash of the headline to avoid invalid filenames)
                        article_hash = hashlib.md5(article['headline'].encode()).hexdigest()[:10]
                        article_dir = os.path.join(base_dir, article_hash)
                        if not os.path.exists(article_dir):
                            os.makedirs(article_dir)
                        
                        # Download and save images
                        for i, img in enumerate(images):
                            img_url = img['src']
                            
                            # Skip data URLs and invalid URLs
                            if img_url.startswith('data:') or not img_url or img_url == '#':
                                continue
                                
                            # Make URL absolute if needed
                            if img_url.startswith('/'):
                                img_url = f"https://www.cnn.com{img_url}"
                                
                            try:
                                # Get the image extension
                                img_ext = os.path.splitext(urlparse(img_url).path)[1]
                                if not img_ext:
                                    img_ext = '.jpg'  # Default extension
                                
                                # Create the image filename
                                img_filename = f"image_{i+1}{img_ext}"
                                img_path = os.path.join(article_dir, img_filename)
                                
                                # Download the image
                                img_response = requests.get(img_url, headers=HEADERS, timeout=10)
                                if img_response.status_code == 200:
                                    with open(img_path, 'wb') as f:
                                        f.write(img_response.content)
                                    article['images'].append({
                                        'url': img_url,
                                        'local_path': img_path
                                    })
                                    print(f"  Saved image: {img_path}")
                            except Exception as e:
                                print(f"  Error saving image {img_url}: {e}")
                
                except Exception as e:
                    print(f"  Error processing article: {e}")
        
        return headlines
        
    except Exception as e:
        print(f"Error scraping CNN: {e}")
        return []

# Get the news with enhanced functionality
print("CNN News Headlines with Content and Images:")
articles = get_cnn_news(save_images=True, fetch_content=True, max_articles=5)

# Display the results
for idx, article in enumerate(articles, 1):
    print(f"\n{idx}. {article['headline']}")
    print(f"   Link: {article['link']}")
    
    # Show content preview (first 200 characters)
    content_preview = article['content'][:200].replace('\n', ' ')
    if article['content'] and len(article['content']) > 200:
        content_preview += "..."
    print(f"   Content preview: {content_preview}")
    
    # Show images
    if article['images']:
        print(f"   Downloaded {len(article['images'])} images")
    else:
        print("   No images downloaded")
    
    print("-" * 80)

# Save all data to a markdown file for easy viewing
markdown_path = f"cnn_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(markdown_path, 'w', encoding='utf-8') as f:
    f.write(f"# CNN News Articles - {datetime.now().strftime('%Y-%m-%d')}\n\n")
    
    for idx, article in enumerate(articles, 1):
        f.write(f"## {idx}. {article['headline']}\n\n")
        f.write(f"**Link**: [{article['link']}]({article['link']})\n\n")
        
        if article['content']:
            f.write("### Content:\n\n")
            f.write(article['content'].replace('\n', '\n\n'))
            f.write("\n\n")
        
        if article['images']:
            f.write("### Images:\n\n")
            for img in article['images']:
                f.write(f"- [{img['url']}]({img['local_path']})\n")
            f.write("\n")
        
        f.write("---\n\n")

print(f"\nSaved all articles to {markdown_path}")