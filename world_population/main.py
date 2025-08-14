import pandas as pd
import requests

url = 'https://www.worldometers.info/world-population/population-by-country/'
headers = {'User-Agent':'Mozilla/5.0(Window NT 10.0; Win64; x64 ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
#Fetch Page...
responce = requests.get(url, headers=headers)
responce.raise_for_status()
#Extract table from HTML
tables = pd.read_html(responce.text)
print(f"Number of tables found :{len(tables)}")
df = tables[0]
df.to_excel("world_population.xlsx", index=False)
print("✅ Data saved to world_population.xlsx")