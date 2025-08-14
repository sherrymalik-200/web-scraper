# step 1: Import the required libraries
import pandas as pd

# step 2: Load the URL
url = 'https://www.apsaa.com.pk/north_zone.html'

# step 3: Fetch the HTML content with headers and read the HTML table into a DataFrame
import requests
# headers to avoid being blocked
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
# headers are important to avoid being blocked by the server
response = requests.get(url, headers=headers)
response.raise_for_status()  # Raise an error for bad status codes

tables = pd.read_html(response.text)

# step 4: Check the number of tables
print(f"Number of tables found: {len(tables)}")
# step 5: Display the first few rows of the first table
print(tables[0].head())
combined_df = pd.concat(tables, ignore_index=True)

# Save to Excel
combined_df.to_excel("north_zone.xlsx", index=False)