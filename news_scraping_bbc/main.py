import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL for BBC News homepage
news_url = "https://www.bbc.com/news"

# Fetch and parse the page
response = requests.get(news_url)
news_soup = BeautifulSoup(response.content, "html.parser")

# Try multiple selectors for headlines
headlines = news_soup.find_all("h3", class_="gs-c-promo-heading__title")

# If not found, try anchor tags with class 'gs-c-promo-heading'
if not headlines:
    promo_anchors = news_soup.select("a.gs-c-promo-heading")
    headlines = [a for a in promo_anchors if a.text.strip()]

# If still not found, fallback to all anchor tags with '/news/' in href and non-empty text
if not headlines:
    headlines = [
        a for a in news_soup.find_all("a", href=True)
        if "/news/" in a["href"] and a.text.strip()
    ]

if not headlines:
    print("No headlines found using known selectors.")
else:
    data = []
    for h in headlines:
        text = h.text.strip()
        link = h.get("href")

        # If the link is relative, add BBC domain
        if link and link.startswith("/"):
            link = "https://www.bbc.com" + link

        data.append({"Headline": text, "Link": link})

    df = pd.DataFrame(data)
    df.to_excel("bbc_news_with_links.xlsx", index=False)

    print(f"Saved {len(data)} headlines with links to bbc_news_with_links.xlsx")